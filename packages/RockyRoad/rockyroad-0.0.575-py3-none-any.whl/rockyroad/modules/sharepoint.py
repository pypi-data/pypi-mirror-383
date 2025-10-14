from .module_imports import get_key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    returns,
    headers,
    retry,
    Query,
)

# Module configuration
USE_SERVICES_API = True
key = get_key(use_services_api=USE_SERVICES_API)

@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Sharepoint(Consumer):
    """Inteface to Sharepoint resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
        super().__init__(base_url=self._base_url, *args, **kw)

    @returns.json
    @http_get("sharepoint/sites")
    def list_sites(self):
        """This call will return list of sites."""

    @returns.json
    @http_get("sharepoint/files")
    def list_files(self, site_name: Query = None, drive_name: Query = None, item_id: Query = None):
        """This call will return list of files for the specified site, drive, and item."""
        