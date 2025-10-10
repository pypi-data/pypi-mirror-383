from __future__ import annotations

from acceldata.airflow import listener
from airflow.plugins_manager import AirflowPlugin


# os.environ["TORCH_CATALOG_URL"] = "URL of the ADOC server"
# os.environ["TORCH_ACCESS_KEY"] = "API access key generated from torch UI"
# os.environ["TORCH_SECRET_KEY"] = "API secret key generated from torch UI"
# os.environ["TIMEOUT_MS"] = "(Optional) Time in ms to wait for ADOC server to respond to requests. Default value is 10000 ms"

# If set matching dag ids will be ignored and everything else will be observed
# IGNORE and OBSERVE environment variables are mutually exclusive
# Don't set if OBSERVE environment variables are set in the below step
# os.environ["DAGIDS_TO_IGNORE"] = "Comma separated dag ids to ignore observation"
# os.environ["DAGIDS_REGEX_TO_IGNORE"] = "Regex for dag ids to ignore observation"

# If set matching dag ids will be observed and everything else will be ignored.
# IGNORE and OBSERVE environment variables are mutually exclusive
# Don't set if IGNORE environment variables are set in the above step
# os.environ["DAGIDS_TO_OBSERVE"] = "Comma separated dag ids to observe"
# os.environ["DAGIDS_REGEX_TO_OBSERVE"] = "Regex for dag ids to observe"


class AcceldataListenerPlugin(AirflowPlugin):
    name = "AcceldataListenerPlugin"
    listeners = [listener]
