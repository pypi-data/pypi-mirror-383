from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    post,
    patch,
    delete,
    returns,
    headers,
    retry,
    Body,
    json,
    Query,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Machine_Logs(Consumer):
    """Inteface to machine logs resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("machines/logs")
    def list(
        self,
        machine_log_uid: Query = None,
        machine_uid: Query = None,
        model: Query = None,
        serial: Query = None,
    ):
        """This call will return log information for the specified criteria."""

    @returns.json
    @delete("machines/logs")
    def delete(self, uid: Query):
        """This call will delete the log information for the specified uid."""

    @returns.json
    @json
    @post("machines/logs")
    def insert(self, machine_log: Body):
        """This call will create log information with the specified parameters."""

    @returns.json
    @json
    @patch("machines/logs")
    def update(self, log: Body):
        """This call will update the log information with the specified parameters."""
