from __future__ import annotations

import airflow
import functools
import logging
import os
import re
from acceldata.airflow.constants import ROOT_SPAN_EVENT_UID, STARTED, ENDED, \
    STATE, \
    DURATION, SUCCESS, FAILED, MESSAGE, DAG_ID, DAG_RUN_ID, TASK_RUN_ID, OPERATOR, TRY_NUMBER, TASK_ID, \
    DURATION_UNIT, RUN_TYPE, OWNER, QUEUE, SCHEDULE_INTERVAL, DAG_URL
from acceldata_sdk.errors import APIError, TorchSdkException
from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_sdk.models.job import CreateJob, Node
from acceldata_sdk.models.pipeline import CreatePipeline, PipelineRunResult, PipelineRunStatus, PipelineSourceType
from acceldata_sdk.torch_client import TorchClient
from airflow.configuration import conf
from airflow.models import DagBag, DagModel
from airflow.models.dagrun import DagRun
from airflow.models.taskinstance import TaskInstance
from pkg_resources import parse_version

log = logging.getLogger(__name__)


def singleton(cls):
    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        if not wrapper.instance:
            log.info("Initializing singleton instance ")
            wrapper.instance = cls(*args, **kwargs)
        return wrapper.instance

    wrapper.instance = None
    return wrapper


@singleton
class SingletonTorchClient:
    def __init__(self) -> None:
        self.torchClient = get_or_create_torch_client()

    def get_torch_client(self):
        return self.torchClient


def get_dag_run_url(dag_run):
    base_url = conf.get('webserver', 'BASE_URL')
    import urllib.parse
    execution_date = urllib.parse.quote(dag_run.execution_date.isoformat())
    dag_url = f'{base_url}/graph?root=&dag_id={dag_run.dag_id}&execution_date={execution_date}&arrang=LR'
    log.info(dag_url)
    return dag_url


def get_or_create_torch_client():
    # TODO: Required on Mac else the app crashes
    os.environ["no_proxy"] = "*"
    adoc_catalog_url = os.environ.get("TORCH_CATALOG_URL")
    access_key = os.environ.get("TORCH_ACCESS_KEY")
    secret_key = os.environ.get("TORCH_SECRET_KEY")
    timeout_ms = int(os.environ.get("TIMEOUT_MS", 10000))
    # Handle missing environment variables
    if not adoc_catalog_url:
        raise TorchSdkException("The environment variable 'TORCH_CATALOG_URL' is not set")
    if not access_key:
        raise TorchSdkException("The environment variable 'TORCH_ACCESS_KEY' is not set")
    if not secret_key:
        raise TorchSdkException(" The environment variable 'TORCH_SECRET_KEY' is not set")
    adoc_client = TorchClient(url=adoc_catalog_url, access_key=access_key,
                              secret_key=secret_key,timeout_ms=timeout_ms)
    return adoc_client


def should_ignore_dag(dag_id):
    dagids_to_ignore = os.environ.get("DAGIDS_TO_IGNORE")
    dagids_regex_to_ignore = os.environ.get("DAGIDS_REGEX_TO_IGNORE")
    ignore_dag_id = False

    # If any one of these env variables are present, ignore based on the criteria
    dag_id_match = False
    dag_id_regex_match = False
    if dagids_regex_to_ignore is not None:
        dag_id_regex_match = re.search(dagids_regex_to_ignore, dag_id)

    if dagids_to_ignore is not None:
        if dag_id in dagids_to_ignore.split(','):
            dag_id_match = True

    if dag_id_regex_match or dag_id_match:
        ignore_dag_id = True
        log.debug("Ignoring dag_id %s instrumentation", dag_id)

    return ignore_dag_id


def observe_dag_env_variables_detected():
    dagids_to_observe = os.environ.get("DAGIDS_TO_OBSERVE")
    dagids_regex_to_observe = os.environ.get("DAGIDS_REGEX_TO_OBSERVE")
    log.debug("DAGIDS_TO_OBSERVE")
    log.debug(dagids_to_observe)
    log.debug("DAGIDS_REGEX_TO_OBSERVE")
    log.debug(dagids_regex_to_observe)
    if dagids_to_observe is not None or dagids_regex_to_observe is not None:
        return True
    return False


def ignore_dag_env_variables_detected():
    dagids_to_ignore = os.environ.get("DAGIDS_TO_IGNORE")
    dagids_regex_to_ignore = os.environ.get("DAGIDS_REGEX_TO_IGNORE")
    if dagids_to_ignore is not None or dagids_regex_to_ignore is not None:
        return True
    return False


def should_observe_dag(dag_id):
    dagids_to_observe = os.environ.get("DAGIDS_TO_OBSERVE")
    dagids_regex_to_observe = os.environ.get("DAGIDS_REGEX_TO_OBSERVE")

    # If any one of these env variables are present, observe based on the criteria
    observe_dag_id = False
    dag_id_match = False
    dag_id_regex_match = False

    if dagids_regex_to_observe is not None:
        dag_id_regex_match = re.search(dagids_regex_to_observe, dag_id)

    if dagids_to_observe is not None:
        if dag_id in dagids_to_observe.split(','):
            dag_id_match = True

    if dag_id_regex_match or dag_id_match:
        observe_dag_id = True
        log.debug("Observing dag_id %s ", dag_id)

    return observe_dag_id


def get_torch_client() -> TorchClient:
    singleton_torch_client = SingletonTorchClient()
    return singleton_torch_client.get_torch_client()


def is_dag_run_supported_for_version(version):
    parsed_version_airflow = parse_version(version)
    parsed_version_dag_run_support = parse_version("2.5.0.dev0")
    log.debug(f"parsed_version_airflow : {parsed_version_airflow}")
    log.debug(f"parsed_version_dag_run_support : {parsed_version_dag_run_support}")
    if parsed_version_airflow >= parsed_version_dag_run_support:
        log.debug("dag_run state change events are supported ")
        return True
    log.debug("dag_run state change events not supported ")
    return False


def get_downstream_ids_task_instance(task_instance: TaskInstance, session):
    dag_model = DagModel.get_current(task_instance.dag_id, session=session)
    dagbag = DagBag(dag_folder=dag_model.fileloc, read_dags_from_db=True)
    dag = dagbag.get_dag(task_instance.dag_id, session=session)
    task_ids = dag.task_dict[task_instance.task_id].downstream_task_ids
    return task_ids


def create_pipeline(pipeline_name, torch_client):
    log.debug("Creating/updating pipeline for the DAG with the pipeline_name %s", pipeline_name)
    pipeline = CreatePipeline(uid=pipeline_name, name=pipeline_name, sourceType=PipelineSourceType.AIRFLOW)
    return torch_client.create_pipeline(pipeline)


def prepare_dag_run_context_data(dag_run, dag_id, dag_run_id, dag_url, msg):
    schedule_interval = (
        str(dag_run.dag.schedule_interval)
        if dag_run is not None and dag_run.dag is not None and dag_run.dag.schedule_interval is not None
        else None
    )

    return {
        STARTED: str(dag_run.start_date),
        STATE: str(dag_run.state),
        DAG_ID: str(dag_id),
        DAG_RUN_ID: str(dag_run_id),
        RUN_TYPE: str(dag_run.run_type),
        DAG_URL: dag_url,
        SCHEDULE_INTERVAL: schedule_interval,
        MESSAGE: msg
    }


def prepare_dag_completion_context_data(dag_run, dag_id, dag_run_id, msg):
    return {
        STARTED: str(dag_run.start_date),
        ENDED: str(dag_run.end_date),
        STATE: str(dag_run.state),
        DAG_ID: str(dag_id),
        DAG_RUN_ID: str(dag_run_id),
        RUN_TYPE: str(dag_run.run_type),
        MESSAGE: msg
    }


def prepare_task_run_context_data(task_instance):
    return {
        TASK_ID: str(task_instance.task_id),
        TASK_RUN_ID: str(task_instance.run_id),
        STARTED: str(task_instance.start_date),
        OPERATOR: str(task_instance.operator),
        STATE: str(task_instance.state),
        TRY_NUMBER: str(task_instance.try_number),
        OWNER: str(task_instance.task.owner),
        QUEUE: str(task_instance.task.queue)
    }


def prepare_task_completion_context_data(task_instance, try_number):
    return {
        TASK_ID: str(task_instance.task_id),
        TASK_RUN_ID: str(task_instance.run_id),
        STARTED: str(task_instance.start_date),
        ENDED: str(task_instance.end_date),
        DURATION: str(task_instance.duration) + DURATION_UNIT,
        OPERATOR: str(task_instance.operator),
        STATE: str(task_instance.state),
        TRY_NUMBER: str(try_number)
    }


def create_pipeline_run(pipeline_response, context_data, dag_id, dag_run_id):
    continuation_id = f"{dag_id}.{dag_run_id}"
    log.debug("Creating pipeline run for the pipeline with name %s and continuation_id %s", pipeline_response.name,
             continuation_id)
    return pipeline_response.create_pipeline_run(context_data=context_data, continuation_id=continuation_id)


def create_root_span(pipeline_run, root_span_uid, context_data):
    log.debug("Creating the root span with uid %s", root_span_uid)
    root_span = pipeline_run.create_span(uid=root_span_uid)
    event_uid = ROOT_SPAN_EVENT_UID
    pipeline_start_event = GenericEvent(context_data=context_data, event_uid=event_uid)
    root_span.send_event(span_event=pipeline_start_event)
    return root_span


def get_pipeline_by_name(torch_client, pipeline_name):
    log.debug("Getting the pipeline corresponding to the pipeline name: %s", pipeline_name)
    return torch_client.get_pipeline(pipeline_name)


def get_pipeline_run_by_continuation_id(torch_client, dag_id, run_id, pipeline):
    continuation_id = f"{dag_id}.{run_id}"
    log.debug("Getting the pipeline run corresponding to dag run based on continuation_id : %s and pipeline_id: %s",
             continuation_id, pipeline.id)
    return torch_client.get_pipeline_run(continuation_id=continuation_id, pipeline_id=pipeline.id)


def end_pipeline_for_dag_run(dag_run: DagRun, torch_client, pipeline_run_result: PipelineRunResult,
                             pipeline_run_status: PipelineRunStatus, msg: str):
    log.debug("end_pipeline_for_dag_run called with dag_run: %s", dag_run)

    dag_id = dag_run.dag_id
    dag_run_id = dag_run.run_id

    # 1. get the pipeline corresponding to the above pipelineName
    pipeline = get_pipeline_by_name(torch_client, dag_id)
    #  2. get the pipeline run for the dag run
    pipeline_run = get_pipeline_run_by_continuation_id(torch_client, dag_id, dag_run_id, pipeline)

    # 3. get the root span for the run and mark it as success or failure accordingly
    root_span_context = pipeline_run.get_root_span()
    log.debug("Got the root span context %s", root_span_context)
    root_span_uid = dag_id+".span"
    log.debug("Root span uid for the pipeline run is : %s", root_span_uid)
    event_uid = f'{ROOT_SPAN_EVENT_UID}.end_event'
    context_data = prepare_dag_completion_context_data(dag_run, dag_id, dag_run_id, msg)
    pipeline_end_event = GenericEvent(context_data=context_data,
                                      event_uid=event_uid)
    root_span_context.send_event(span_event=pipeline_end_event)

    #  4.Mark the run as success or failure based on run result
    if pipeline_run_result == PipelineRunResult.SUCCESS:
        log.debug("pipeline_run_result is: %s", pipeline_run_result)
        root_span_context.end()
        log.debug("Root span has been ended.")

    elif pipeline_run_result == PipelineRunResult.FAILURE:
        log.debug("pipeline_run_result is: %s", pipeline_run_result)
        root_span_context.failed()
        log.debug("Root span has been Failed.")

    log.debug("Ending the pipeline run")
    # 5. Terminating the pipeline run
    pipeline_run.update_pipeline_run(context_data=context_data,
                                     result=pipeline_run_result,
                                     status=pipeline_run_status)


def validate_and_auto_instrument_dag(dag_id):
    # Observe the given dag if any one of below condition happens:
    observe_dag_var_detected = observe_dag_env_variables_detected()
    ignore_dag_var_detected = ignore_dag_env_variables_detected()
    # 1. None of the environment variables to observe/ignore are present
    # 2. dag_id matches the OBSERVE environment variable criteria
    # 3. dag_id doesn't match the IGNORE environment variable criteria

    if ((not observe_dag_var_detected and not ignore_dag_var_detected)
            or (observe_dag_var_detected and should_observe_dag(dag_id))
            or (ignore_dag_var_detected and not should_ignore_dag(dag_id))):
        return True
    return False


def create_job_and_span(task_instance: TaskInstance, torch_client: TorchClient):
    dag_run_id = task_instance.dag_run.run_id
    dag_id = task_instance.dag_id
    pipeline_name = str(task_instance.dag_id)
    pipeline = get_pipeline_by_name(torch_client, pipeline_name)
    pipeline_run = get_pipeline_run_by_continuation_id(torch_client, dag_id, dag_run_id, pipeline)
    root_span_context = pipeline_run.get_root_span()
    log.debug("Got the root span context %s", root_span_context)

    # 1. create a job with  job_uid and inputs based on upstream tasks
    upstream_list = []
    if task_instance.task and task_instance.task.upstream_list:
        upstream_list = task_instance.task.upstream_list

    input_nodes = []
    associated_job_uids = []

    # Construct node inputs
    log.debug("Constructing the input_nodes from upstream tasks")
    for upstream in upstream_list:
        job_uid = upstream.task_id
        input_nodes.append(Node(job_uid=job_uid))

    job_uid = task_instance.task_id
    associated_job_uids.append(job_uid)
    job = CreateJob(
        uid=job_uid,
        name=job_uid,
        version=pipeline_run.versionId,
        pipeline_run_id=pipeline_run.id,
        inputs=input_nodes,
        bounded_by_span=False
    )

    log.debug("Creating job: %s", job)
    pipeline.create_job(job)

    # 2. get the root span and then create child span on that object using the spanUid above
    # and pass the jobUid as well to this function

    log.debug("Initiate Child span for job with job_uid %s", job_uid)
    child_span_uid = f'{job_uid}.span'
    log.debug("associatedJobUids %s for the child span with child_span_uid %s", associated_job_uids, child_span_uid)

    try_number = task_instance.try_number
    event_uid = f'{child_span_uid}.job.start.try_{try_number}.event'
    context_data = prepare_task_run_context_data(task_instance)
    job_start_event = GenericEvent(context_data=context_data,
                                   event_uid=event_uid)

    # 3. Handle the case when the span already exists (retry)
    try:
        child_span = pipeline_run.get_span(child_span_uid)
        log.debug("Span already exists with child_span_uid : %s", child_span_uid)
        # Emit generic events related to the retry here
        log.debug("Sending job retry start event %s for the child span with child_span_uid %s", job_start_event,
                 child_span_uid)
        child_span.send_event(span_event=job_start_event)
        log.debug("Successfully sent job start retry event for the child span with child_span_uid %s", child_span_uid)
        return
    except Exception as e:
        # Span doesn't exist, create the span under the root span
        log.info("Non existent span : %s", e)
        log.debug("Span doesn't exist with child_span_uid %s . Create the child span", child_span_uid)
        child_span = root_span_context.create_child_span(uid=child_span_uid, associatedJobUids=associated_job_uids)
        log.debug("Created span with child_span_uid %s", child_span_uid)
        child_span.start()
        log.debug("Started the child span with child_span_uid %s", child_span_uid)
        log.debug("Sending job start event %s for the child span with child_span_uid %s", job_start_event,
                 child_span_uid)
        child_span.send_event(span_event=job_start_event)
        log.debug("Successfully sent job start event for the child span with child_span_uid %s", child_span_uid)


def handle_failed_state(task_instance, child_span_uid, try_number, max_retries, child_span):
    # Task instance state comes as FAILED, so try_number is incremented by 1, hence, need to reduce by 1
    # If the TaskInstance is currently running, this will match the column in the database,
    # in all other cases this will be incremented.
    task_failure_try_number = try_number - 1
    context_data = prepare_task_completion_context_data(task_instance, task_failure_try_number)
    if task_failure_try_number <= max_retries:
        # Logic to send generic event for job failure if this isn't the last retry
        log.debug("Sending job end event for the child span with child_span_uid %s", child_span_uid)
        job_fail_event = GenericEvent(context_data=context_data,
                                      event_uid=f'{child_span_uid}.job.failed.try_{task_failure_try_number}.event')
        child_span.send_event(span_event=job_fail_event)
        log.debug("Sending failed retry data event for the child span with child_span_uid %s", child_span_uid)
        return

    # This is the last retry, the span should be ended here
    log.debug("Task instance in failed State and last retry. Sending JobFailEvent")
    event_uid = f'{child_span_uid}.job.failed.try.{task_failure_try_number}.event'
    job_fail_event = GenericEvent(context_data=context_data, event_uid=event_uid)
    child_span.send_event(span_event=job_fail_event)
    child_span.failed()
    log.debug("Marking child span as failed")


def handle_failed_state_listener_bug(task_instance, child_span_uid, try_number, max_retries, child_span):
    # Task instance state is coming as running for failure callback also, so no need to decrement in this case
    # If the TaskInstance is currently running, this will match the column in the database,
    # in all other cases this will be incremented.
    context_data = prepare_task_completion_context_data(task_instance, try_number)
    if try_number <= max_retries:
        log.debug("Sending job end event for the child span with child_span_uid %s", child_span_uid)
        job_fail_event = GenericEvent(context_data=context_data,
                                      event_uid=f'{child_span_uid}.job.failed.try.{try_number}.event')
        child_span.send_event(span_event=job_fail_event)
        log.debug("Sending failed retry data event for the child span with child_span_uid %s", child_span_uid)
        return

    # This is the last retry, the span should be ended here
    log.debug("Task instance in failed State and last retry. Sending JobFailEvent")
    event_uid = f'{child_span_uid}.job.failed.try.{try_number}.event'
    job_fail_event = GenericEvent(context_data=context_data, event_uid=event_uid)
    child_span.send_event(span_event=job_fail_event)
    child_span.failed()
    log.debug("Marking child span as failed")


def handle_success_state(task_instance, child_span, child_span_uid, try_number):
    # Task instance state comes as SUCCESS, so try_number is incremented by 1, hence, need to reduce by 1
    # If the TaskInstance is currently running, this will match the column in the database,
    task_success_try_number = try_number - 1
    context_data = prepare_task_completion_context_data(task_instance, task_success_try_number)
    log.debug("Task instance in success State. Sending JobEndEvent")
    event_uid = f'{child_span_uid}.job.success.try.{task_success_try_number}.event'
    job_end_event = GenericEvent(context_data=context_data, event_uid=event_uid)
    child_span.send_event(span_event=job_end_event)
    child_span.end()
    log.debug("Marking child span as success")


def end_job_and_span(task_instance: TaskInstance, torch_client: TorchClient, ):
    log.debug("TaskInstance State: %s", task_instance.state)
    # 1. Get pipeline for the task
    log.debug("Get pipeline for the task")
    dag_id = task_instance.dag_id
    pipeline_name = str(dag_id)
    pipeline = torch_client.get_pipeline(pipeline_name)

    #  2. get the pipeline run on the dag run
    dag_run_id = task_instance.dag_run.run_id
    pipeline_run = get_pipeline_run_by_continuation_id(torch_client, dag_id, dag_run_id, pipeline)
    job_uid = task_instance.task_id

    child_span_uid = f'{job_uid}.span'
    log.debug("Fetching the child span with child span uid %s", child_span_uid)

    log.debug("Triggering job end events based on the task state")
    try_number = task_instance.try_number
    log.debug("try_number inside task failure/success callback %s", try_number)

    max_retries = task_instance.task.retries

    log.debug("max_retries %s", max_retries)
    child_span = pipeline_run.get_span(child_span_uid)

    if str(task_instance.state) == SUCCESS:
        handle_success_state(task_instance, child_span, child_span_uid, try_number)
    elif str(task_instance.state) == FAILED:
        handle_failed_state(task_instance, child_span_uid, try_number, max_retries, child_span)
    else:
        # Due to a bug in airflow  the task instance state is coming as running for failure callback also,
        # so no need to decrement the try number and take care of this case
        handle_failed_state_listener_bug(task_instance, child_span_uid, try_number, max_retries, child_span)


def create_pipeline_for_older_versions(task_instance: TaskInstance, session):
    log.debug("Checking if pipeline needs to be created for the task_instance : %s", task_instance)
    upstream_size = len(task_instance.task.upstream_list)
    log.debug("Upstream size: %s", upstream_size)
    current_version = airflow.__version__
    log.debug(f"Current Airflow Version : {current_version}")
    if upstream_size == 0:
        if not is_dag_run_supported_for_version(current_version):
            log.debug("Creating the pipeline for events with zero upstream events for the Current Airflow Version: %s",
                     current_version)
            create_pipeline_for_dag_run(task_instance.dag_run, get_torch_client(), msg="", )
        else:
            log.debug("task instance initiation handling not needed to start the pipeline for the newer versions")


def end_pipeline_for_older_versions(task_instance: TaskInstance, pipelineRunResult: PipelineRunResult,
                                    pipelineRunStatus: PipelineRunStatus, session):
    log.debug("Checking if pipeline needs to be ended for the task instance : %s ", task_instance)
    current_version = airflow.__version__
    log.debug(f"Current Airflow Version : {current_version}")
    task_ids = get_downstream_ids_task_instance(task_instance, session)
    log.debug("downstream task_ids: %s", task_ids)
    downstream_size = len(task_ids)
    log.debug("Downstream length: %s", downstream_size)
    if downstream_size == 0 or task_instance.state == FAILED:
        if not is_dag_run_supported_for_version(current_version):
            log.debug("Either the Downstream size is 0 or task_instance is in failed state.")
            log.debug("Ending the pipeline run the with the Current Airflow Version: %s",
                     current_version)
            end_pipeline_for_dag_run(task_instance.dag_run, get_torch_client(), pipelineRunResult,
                                     pipelineRunStatus, msg="")
        else:
            log.debug("task instance completion handling not needed to terminate the pipeline for the newer versions")
    else:
        log.debug("Downstream size is > 0 and task_instance state is not FAILED. Proceeding with the next tasks")


def create_pipeline_for_dag_run(dag_run: DagRun, torch_client, msg: str):
    log.debug("create_pipeline_for_dag_run invoked")
    dag_id = dag_run.dag_id
    pipeline_name = dag_id
    root_span_uid = dag_id+".span"
    dag_url = get_dag_run_url(dag_run)
    try:
        # 1. Create/Update Pipeline
        pipeline_response = create_pipeline(pipeline_name, torch_client)
        dag_run_id = dag_run.run_id

        # 2. Create pipeline run
        log.debug(f"dag run: {dag_run}")
        context_data = prepare_dag_run_context_data(dag_run, dag_id, dag_run_id, dag_url, msg)
        pipeline_run = create_pipeline_run(pipeline_response, context_data, dag_id, dag_run_id)
        pipeline_run_id = pipeline_run.id
        log.debug("Created pipeline run with the pipeline_run_id: %s", pipeline_run_id)

        # 3. Create root span
        log.debug("Creating the root span")
        root_span = create_root_span(pipeline_run, root_span_uid, context_data)
    except APIError as api_error:
        log.error("Pipeline creation for the pipeline with name : %s  , failed with error:  %s", str(pipeline_name),
                  str(api_error))
