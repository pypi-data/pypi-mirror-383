"""
Hold AtriumResponse class
"""

import json


class AtriumResponse:
    """
    A response class object from Atrium Sports APIs
    """

    def __init__(self, status_code=0, data=None, links=None, errors=None):
        """initialise the class
        request_response is instance of the response object from the requests module"""

        self._status_code = status_code
        self._data = data or []
        self._links = links or {}
        self._errors = errors or []
        self._resources = {}

    @staticmethod
    def create_from_str(status_code, raw):
        try:
            json_output = json.loads(raw)
        except ValueError:
            return AtriumResponse(status_code, errors=[raw])
        return AtriumResponse.create(status_code, json_output)

    @staticmethod
    def _create_error(status_code, json_output):
        errors = []
        if json_output and "error" in json_output:
            errors.append(json_output["error"]["message"])
        elif json_output and "Message" in json_output:
            errors.append(json_output["Message"])
        else:
            errors.append("Error Code: {}".format(status_code))
        return AtriumResponse(status_code, errors=errors)

    @staticmethod
    def create(status_code, json_output):
        if status_code != 200:
            return AtriumResponse._create_error(status_code, json_output)
        response = AtriumResponse(status_code, data=json_output.get("data"), links=json_output.get("links"))
        includes = json_output.get("includes", {})
        if includes:
            response._handle_resources(includes.get("resources", {}))
        return response

    def success(self):
        """return True if call succeeded"""
        if self._status_code == 200:
            return True
        return False

    def status(self):
        """return the status code of the response"""
        return int(self._status_code)

    def data(self):
        """return the data from the request"""
        return self._data or []

    def data_count(self):
        """return the number of rows of data from the request"""
        return len(self._data or [])

    def links(self, link_type=None):
        """return the links from the request"""
        if link_type:
            return self._links.get(link_type)
        return self._links or {}

    def errors(self):
        """return the errors from the response"""
        return self._errors or []

    def error_string(self):
        """return the errors from the response as one string"""
        if self._errors:
            return "\n".join(self._errors)
        return ""

    def resources(self):
        """return the resources from the last call"""
        return self._resources or {}

    def expand_resource(self, key, data_row):
        """Return the resource from an included resource key"""
        if key not in data_row:
            return None
        r_id = data_row[key].get("id")
        r_type = data_row[key].get("resourceType")
        if r_type in self._resources and r_id in self._resources[r_type]:
            return self._resources[r_type].get(r_id, {})
        return None

    def merge(self, response_data):
        """Merge a number of responses into the one object"""
        if isinstance(response_data, list):
            responses = response_data
        else:
            responses = [response_data]
        for response in responses:
            new_status = response.status()
            if not self._status_code or self._status_code == 200:
                self._status_code = new_status
            self._links = response.links()
            self._handle_resources(response.resources())
            self._data = self._data + response.data()
            self._errors = self._errors + response.errors()
        return True

    def _handle_resources(self, resources):
        """store include data"""

        for include_key in resources.keys():
            self._resources.setdefault(include_key, {})
            self._resources[include_key].update(resources.get(include_key, {}))
        return True

    def set_error(self, error):
        """Manually add an error to the response. Automatically sets status_code"""
        self._errors.append(error)
        self._status_code = 500
        return True
