"""
Hold AtriumSports class
"""

from atriumsports.datacore.datacore import DatacoreAPI
from atriumsports.datacore_stream.datacore_stream import DatacoreStreamingAPI


class AtriumSports:
    """
    A class that handles getting the correct client objects
    """

    def __init__(self, options):
        """initialise the class"""

        self._options = {
            "sport": options.get("sport", "basketball"),
            "credential_id": options.get("credential_id"),
            "credential_secret": options.get("credential_secret"),
            "organizations": options.get("organizations", []),
            "org_group": options.get("org_group"),
            "environment": options.get("environment", "production"),
            "headers": options.get("headers", {}),
            "version": 1,
        }

    def client(self, client_type):
        """return a client object"""

        if client_type == "datacore":
            return DatacoreAPI(self._options)
        elif client_type == "datacore-stream":
            return DatacoreStreamingAPI(self._options)
        return None
