"""A file defining all the endpoint addresses"""

import os


class ConfigurationException(Exception):
    """Exception to be raised when a configuration is invalid"""

    pass


def _get_endpoint(environment, endpoint_type):
    """return urls for the atriumsports environments"""

    # Check if the URL is overridden by an environment variable
    env_var_name = f"DC_SDK_{endpoint_type.upper()}_URL"
    overridden_url = os.getenv(env_var_name)
    if overridden_url:
        return overridden_url

    # add some extra mapping
    fix_mapping = {
        "prod": "production",
        "uat": "nonprod",
        "dev": "sandpit",
        "test": "sandpit",
        "stg": "nonprod",
    }
    environment = fix_mapping.get(environment, environment)
    envs = {
        "auth": {
            "production": "https://token.connect.sportradar.com/v1/oauth2/rest/token",
            "nonprod": "https://token.stg.connect-nonprod.sportradar.dev/v1/oauth2/rest/token",
            "sandpit": "https://token.dev.connect-nonprod.sportradar.dev/v1/oauth2/rest/token",
            "localhost": "http://localhost:XXXX",
        },
        "api": {
            "production": "https://api.dc.connect.sportradar.com",
            "nonprod": "https://api.dc.stg.connect-nonprod.sportradar.dev",
            "sandpit": "https://api.dc.dev.connect-nonprod.sportradar.dev",
            "localhost": "http://localhost:XXXX",
        },
        "streamauth": {
            "production": "https://token.connect.sportradar.com/v1/stream/XXXX/access",
            "nonprod": "https://token.stg.connect-nonprod.sportradar.dev/v1/stream/XXXX/access",
            "sandpit": "https://token.dev.connect-nonprod.sportradar.dev/v1/stream/XXXX/access",
            "localhost": "http://localhost:XXXX",
        },
    }
    return envs.get(endpoint_type, {}).get(environment)


def get_endpoint_url(environment, endpoint_type, version=None):
    endpoint_url = _get_endpoint(environment, endpoint_type)
    if not endpoint_url:
        raise ConfigurationException(f"No endpoint {endpoint_type} for environment {environment}")
    if version is not None:
        endpoint_url = f"{endpoint_url}/v{version}"
    return endpoint_url
