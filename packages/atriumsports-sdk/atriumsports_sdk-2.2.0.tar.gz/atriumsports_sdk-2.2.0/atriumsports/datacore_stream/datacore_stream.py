"""File containing class to handle connections to datacore"""

import json
import logging
from urllib.parse import urlparse

import requests
from paho.mqtt.client import Client, error_string

from ..atrium_response import AtriumResponse
from ..endpoints import get_endpoint_url


class AuthException(Exception):
    """Exception to be raised when authentication fails"""

    pass


class DatacoreStreamingAPI:
    """A class to handle the connection to AtriumSports Datacore"""

    def __init__(self, options):
        """initialise the class"""
        self._sport = options.get("sport", "basketball")
        self._credential_id = options.get("credential_id", "")
        self._credential_secret = options.get("credential_secret", "")
        self._environment = options.get("environment", "production")
        self._version = 1
        self._callbacks = {}
        self._fixture_id = None
        self._venue_id = None
        self._scopes = []
        self._client = None
        self._auth_data = {}
        self._scope_matrix = {}
        self._error = ""

    def connect(self, options):
        """Open a connection"""

        if "fixture_id" in options:
            self._fixture_id = options.get("fixture_id")
        if "venue_id" in options:
            self._venue_id = options.get("venue_id")
        if "scopes" in options:
            self._scopes = options.get("scopes", [])

        if "on_read" in options:
            self._callbacks["on_read"] = options.get("on_read")
        if "on_connect" in options:
            self._callbacks["on_connect"] = options.get("on_connect")

        topics = self.auth_data.get("topics", [])
        if not topics:
            self._error = "No topics defined in authorization"
            return False
        self._build_scope_matrix()

        client_id = self.auth_data.get("clientId", "")
        urlparts = urlparse(self.auth_data.get("url"))
        host = urlparts.netloc

        self._client = Client(client_id=client_id, transport="websockets")
        # logging.basicConfig(level=logging.DEBUG)
        # logger = logging.getLogger(__name__)
        # self._client.enable_logger(logger)

        self._client.tls_set()
        headers = {"host": host, "Host": host}

        self._client.ws_set_options(path="{}?{}".format(urlparts.path, urlparts.query), headers=headers)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(host, 443, 15)
        self._client.loop_start()
        return True

    def disconnect(self):
        """disconnect connection"""
        self._client.loop_stop()
        return True

    def error(self):
        """return last error"""
        return self._error or ""

    @property
    def auth_data(self):
        """return auth data"""
        if not self._auth_data:
            self._auth_data = self._generate_auth_data()
        return self._auth_data

    def _generate_auth_data(self):
        """generate an auth token"""
        auth_url = get_endpoint_url(self._environment, "streamauth")

        auth_data = {
            "credentialId": self._credential_id,
            "credentialSecret": self._credential_secret,
            "sport": self._sport,
            "scopes": self._scopes,
        }
        if self._venue_id:
            auth_data["venueId"] = self._venue_id
            auth_url = auth_url.replace("XXXX", "venue")
        else:
            auth_data["fixtureId"] = self._fixture_id
            auth_url = auth_url.replace("XXXX", "fixture")

        response = self._api_call_internal(auth_url, auth_data)
        if response and response.success():
            return response.data()
        raise AuthException(response.error_string())

    def _api_call_internal(self, url, body):
        """make the api call"""
        try:
            body = json.dumps(body or "{}")
            response = requests.post(url, data=body)
            return AtriumResponse.create_from_str(response.status_code, response.text)
        except requests.exceptions.RequestException as err:
            return self._return_error(str(err))

    def _build_scope_matrix(self):
        """build a lookup between scopes and topics"""
        for row in self.auth_data.get("topics", []):
            self._scope_matrix[row.get("scope")] = row
        return True

    # pylint: disable=unused-argument
    def _on_connect(self, client, userdata, flags, connection_result):
        """callback when connected"""
        callback = self._callbacks.get("on_connect")
        self._subscribe_to_topics()
        if callback:
            callback(self)

    def _on_message(self, client, userdata, msg):
        """callback when message received"""
        callback = self._callbacks.get("on_read")
        if callback:
            try:
                message = json.loads(msg.payload)
                callback(self, msg.topic, message)
            except json.JSONDecodeError as err:
                logging.warning("JSON decode error: %s : %s", err, msg.payload)

    def publish(self, scope, message, qos=0):
        """send a message based on a scope"""
        if not message:
            return False
        topic = None
        topic_info = self._scope_matrix.get(scope)
        if not topic_info:
            return False
        if topic_info.get("permission") == "write":
            topic = topic_info.get("topic")
        if not topic:
            return False
        message_info = self._client.publish(topic, json.dumps(message), qos)
        if message_info.rc > 0:
            logging.warning("Streaming message publish failed: %s" % (error_string(message_info.rc)))
            return False
        return True

    def _subscribe_to_topics(self):
        """Subscribe to topics"""
        for row in self.auth_data.get("topics", []):
            if row.get("permission") == "read":
                self._client.subscribe(row.get("topic"))

    @staticmethod
    def _return_error(error):
        """Return an error response"""
        response = AtriumResponse()
        response.set_error(error)
        return response
