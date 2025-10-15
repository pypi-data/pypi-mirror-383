"""File containing class to handle connections to datacore"""

import json

import jwt
import requests

from ..atrium_response import AtriumResponse
from ..endpoints import get_endpoint_url


class AuthException(Exception):
    """Exception to be raised when authentication fails"""

    pass


class DatacoreAPI:
    """A class to handle the connection to AtriumSports Datacore"""

    DEFAULT_LIMIT = 10
    DEFAULT_PAGE_LIMIT = 200

    def __init__(self, options):
        """initialise the class"""
        self._sport = options.get("sport", "basketball")
        self._credential_id = options.get("credential_id", "")
        self._credential_secret = options.get("credential_secret", "")
        self._org_group = options.get("org_group")
        self._organizations = options.get("organizations", [])
        self._environment = options.get("environment", "production")
        self._version = 1
        self._headers = options.get("headers", {})
        self._api_endpoint_url = get_endpoint_url(self._environment, "api", version=self._version)
        self._auth_token = options.get("token")
        self._openapi_api_client = None

    def _create_openapi_configuration(self):
        from .openapi import Configuration

        openapi_configuration = Configuration(
            host=self._api_endpoint_url,
        )
        openapi_configuration.access_token = self.auth_token
        openapi_configuration.safe_chars_for_path_param = ":"
        return openapi_configuration

    def __enter__(self):
        """We're creating a new ApiClient class with connection pool to backend
        that is closed when we exit the context manager

        example of creation and usage:

        atrium = AtriumSports(
            {
                "sport": "basketball",
                "credential_id": "XXXXX",
                "credential_secret": "YYYY",
                "organizations": ["b1e34"],
            }
        )
        datacore = atrium.client("datacore")
        # prepare api client with access token and connection pool
        with datacore as api_client:
            # create api instance object for handling input and output of chosen endpoint
            api_instance = CompetitionsApi(api_client)
        """
        from .openapi import ApiClient

        openapi_configuration = self._create_openapi_configuration()
        self._openapi_api_client = ApiClient(openapi_configuration)
        return self._openapi_api_client

    def __exit__(self, exc_type, exc_value, traceback):
        self._openapi_api_client = None

    def _get_api_url(self, url_path):
        return f"{self._api_endpoint_url}/{self._sport}{url_path}"

    def post(self, url, **kwargs):
        """POST method"""
        return self.call("POST", url, **kwargs)

    def put(self, url, **kwargs):
        """PUT method"""
        if not kwargs.get("body"):
            return self._return_error("PUT method requires a body parameter")
        return self.call("PUT", url, **kwargs)

    def get(self, url, **kwargs):
        """GET method"""
        return self.call("GET", url, **kwargs)

    def delete(self, url, **kwargs):
        """DELETE method"""
        return self.call("DELETE", url, **kwargs)

    def _generate_token(self):
        """generate an auth token"""
        auth_endpoint_url = get_endpoint_url(self._environment, "auth")

        auth_data = {
            "credentialId": self._credential_id,
            "credentialSecret": self._credential_secret,
            "sport": self._sport,
            "organization": {},
        }
        if self._org_group:
            auth_data["organization"]["group"] = self._org_group
        else:
            auth_data["organization"]["id"] = self._organizations

        response = self._api_call_internal("POST", auth_endpoint_url, body=auth_data, timeout=30)
        if response.success():
            return response.data().get("token")
        raise AuthException(response.error_string())

    @property
    def auth_token(self):
        # if token is not defined or expired, generate a new one.
        if not self._auth_token or self._is_token_expired(self._auth_token):
            self._auth_token = self._generate_token()

        return self._auth_token

    @staticmethod
    def _is_token_expired(auth_token):
        # if the token is not set, it is expired
        if not auth_token:
            return True

        try:
            jwt.decode(auth_token, options={"verify_signature": False, "verify_exp": True})
            return False
        except jwt.exceptions.ExpiredSignatureError:
            return True

    def call(self, method, url, **kwargs):
        url = self._get_api_url(url)

        limit = kwargs.get("limit", self.DEFAULT_LIMIT)
        page_limit = kwargs.pop("page_limit", self.DEFAULT_PAGE_LIMIT)
        kwargs["limit"] = self._get_call_limit(limit, page_limit)
        kwargs["headers"] = self._get_headers(kwargs.get("headers"))

        response = AtriumResponse()
        while True:
            resp = self._api_call_internal(method, url, **kwargs)
            response.merge(resp)
            if not resp.success():
                break
            next_page_url = resp.links("next")
            if not next_page_url:
                break
            # don't pass offset or limit params to next page call if it's already in the url
            if "offset=" in next_page_url and "offset" in kwargs:
                kwargs.pop("offset")
            if "limit=" in next_page_url and "limit" in kwargs:
                kwargs.pop("limit")
            url = next_page_url
            call_limit = self._get_call_limit(limit - response.data_count(), page_limit)
            if call_limit <= 0:
                break

        return response

    def _get_call_limit(self, limit, page_limit):
        return min(limit, page_limit)

    def _get_headers(self, headers=None):
        result_headers = self._headers.copy()
        result_headers.update(headers or {})
        result_headers["Authorization"] = "Bearer {}".format(self.auth_token)
        result_headers["Content-Type"] = "application/json"
        return result_headers

    def _api_call_internal(self, method, url, **kwargs):
        """make the api call"""
        try:
            response = self._make_request(method, url, **kwargs)
            return AtriumResponse.create_from_str(response.status_code, response.text)
        except requests.exceptions.RequestException as err:
            return self._return_error(str(err))

    @staticmethod
    def _make_request(method, url, **kwargs):
        """Lets seperate the actual request code"""
        headers = kwargs.pop("headers", {})
        body = json.dumps(kwargs.pop("body", {}))
        timeout = kwargs.pop("timeout", None)

        response = None
        if method == "GET":
            response = requests.get(url, headers=headers, params=kwargs, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=body, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, headers=headers, data=body, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, data=body, timeout=timeout)
        return response

    @staticmethod
    def _return_error(error):
        """Return an error response"""
        response = AtriumResponse()
        response.set_error(error)
        return response
