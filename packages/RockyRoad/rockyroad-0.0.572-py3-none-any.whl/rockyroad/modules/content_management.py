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
    QueryMap,
)


@retry(on_exception=retry.CONNECTION_TIMEOUT, max_attempts=4)
@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class _Content_Management(Consumer):
    """Inteface to Content Management resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def cms_pages(self):
        """Inteface to Cms_Page resource for the RockyRoad API."""
        return self._Cms_Pages(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class _Cms_Pages(Consumer):
        """Inteface to Cms_Page resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def cms_page_fields(self):
            """Inteface to Cms_Page_Field resource for the RockyRoad API."""
            return self._Cms_Page_Fields(self)

        @returns.json
        @http_get("content-management/pages")
        def list(
            self,
            page_type: Query = None,
            title: Query = None,
            subtitle: Query = None,
            category_1: Query = None,
            category_2: Query = None,
            category_3: Query = None,
            field: Query = None,
            is_exact_match: Query = False,
            is_whole_word_match: Query = None,
            is_sort_title_asc: Query = None,
            is_published: Query = None,
            is_searchable: Query = None,
            security_auth_params: QueryMap = {},
        ):
            """This call will return list of Cms_Page_Objects."""

        @returns.json
        @http_get("content-management/pages/{uid}")
        def get(self, uid: str):
            """This call will get the Cms_Page_Object for the specified uid."""

        @delete("content-management/pages/{uid}")
        def delete(self, uid: str):
            """This call will delete the Cms_Page_Object for the specified uid."""

        @returns.json
        @json
        @post("content-management/pages")
        def insert(self, cms_page_object: Body):
            """This call will create the Cms_Page_Object with the specified parameters."""

        @json
        @patch("content-management/pages/{uid}")
        def update(self, uid: str, cms_page_object: Body):
            """This call will update the Cms_Page_Object with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class _Cms_Page_Fields(Consumer):
            """Inteface to Cms_Page_Field resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @http_get("content-management/pages/{cms_page_uid}/fields")
            def list(self, cms_page_uid: str):
                """This call will return list of Cms_Page_Fields."""

            @returns.json
            @http_get("content-management/pages/fields")
            def list_all(self):
                """This call will return list of all Cms_Page_Fields."""

            @returns.json
            @http_get("content-management/pages/fields/{uid}")
            def get(self, uid: str):
                """This call will return list of Cms_Page_Fields."""

            @delete("content-management/pages/fields/{uid}")
            def delete(self, uid: str):
                """This call will the Cms_Page_Field."""

            @returns.json
            @json
            @post("content-management/pages/{cms_page_uid}/fields")
            def insert(self, cms_page_uid: str, cms_page_field_object: Body):
                """This call will create the Cms_Page_Field."""

            @json
            @patch("content-management/pages/fields/{uid}")
            def update(self, uid: str, cms_page_field_object: Body):
                """This call will update the Cms_Page_Field."""
