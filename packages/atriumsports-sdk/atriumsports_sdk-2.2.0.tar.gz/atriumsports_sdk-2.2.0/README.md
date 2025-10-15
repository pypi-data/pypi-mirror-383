# Atrium Sports API SDK

Python module to make use of the Atrium Sports Datacore API

## Datacore REST API

```python
from atriumsports import AtriumSports

atrium = AtriumSports(
    {
        "sport": "basketball",
        "credential_id": "XXXXX",
        "credential_secret": "YYYY",
        "organizations": ["b1a23"],
    }
)
datacore = atrium.client("datacore")
response = datacore.get("/o/b1a23/competitions", limit=500)
for data in response.data():
    print(data)
```

or using **openapi client**

### GET endpoints

```python
from pprint import pprint

from atriumsports import AtriumSports
from atriumsports.datacore.openapi import CompetitionsApi

atrium = AtriumSports(
    {
        "sport": "basketball",
        "credential_id": "XXXXX",
        "credential_secret": "YYYY",
        "organizations": ["b1a23"],
    }
)
datacore = atrium.client("datacore")
# prepare api client with access token and connection pool
with datacore as api_client:
    # create api instance object for handling input and output of chosen endpoint
    api_instance = CompetitionsApi(api_client)
    response = api_instance.competition_list(sport="basketball", organization_id="b1a23")

    pprint(response)
```

### POST and PUT endpoints

```python
from atriumsports import AtriumSports
from atriumsports.datacore.openapi import EntitiesApi
from atriumsports.datacore.openapi import EntityPostBody
from atriumsports.datacore.openapi import EntityPutBody

atrium = AtriumSports(
    {
        "sport": "basketball",
        "credential_id": "XXXXX",
        "credential_secret": "YYYY",
        "organizations": ["b1a23"],
    }
)
datacore = atrium.client("datacore")
with datacore as api_client:
    api_instance = EntitiesApi(api_client)

    response = api_instance.entity_insert(
        sport="basketball",
        organization_id="b1a23",
        entity_post_body=EntityPostBody(
            name_full_local="Test",
            status="INACTIVE",
        ),
    )

    entity_id = response.data[0].entity_id

    response = api_instance.entity_update(
        sport="basketball",
        organization_id="b1a23",
        entity_id=entity_id,
        entity_put_body=EntityPutBody(
            status="ACTIVE",
        ),
    )

    assert response.data[0].status == "ACTIVE"
```

### Response body

Response body is a pydantic object containing deserialized response data.

Example:

```python
from atriumsports import AtriumSports
from atriumsports.datacore.openapi import LeaguesApi

atrium = AtriumSports(
    {
        "sport": "basketball",
        "credential_id": "XXXXX",
        "credential_secret": "YYYY",
        "organizations": ["b1a23"],
    }
)
datacore = atrium.client("datacore")
with datacore as api_client:
    api_instance = LeaguesApi(api_client)
    # throws error if response body doesn't pass validation
    response = api_instance.league_list("b1a23", "basketball")
    print(response.data)
    print(response.data[0].region_type)
```

## Datacore Streaming API

```python
import time

from atriumsports import AtriumSports

atrium = AtriumSports(
    {
        "sport": "basketball",
        "credential_id": "XXXXX",
        "credential_secret": "YYYY",
        "environment": "sandpit",
    }
)
stream_api = atrium.client("datacore-stream")


def on_connect_callback_function(client):
    """example callback when connected"""
    print("connected")


def on_read_callback_function(client, topic, message):
    """example callback when message read"""
    print("{}: {}".format(topic, message))


connected = stream_api.connect(
    {
        "fixture_id": "f71dfdd6-51f1-11ea-8889-22953e2ee7e2",  # fixture_id
        "scopes": ["write:stream_events", "read:stream_events"],  # Scopes
        "on_read": on_read_callback_function,
        "on_connect": on_connect_callback_function,
    }
)
if not connected:
    print(stream_api.error())
else:
    stream_api.publish(
        "write:stream_events",
        {
            "type": "event",
            "data": {
                "eventClass": "sport",
                "eventId": "c2404cc0-9f75-11e8-98d0-529269fb1459",
                "entityId": "c24048a6-9f75-11e8-98d0-529269fb1459",
                "personId": "c2405b2a-9f75-11e8-98d0-529269fb1459",
                "eventType": "2pt",
                "subType": "jumpshot",
                "clock": "PT08:23",
                "shotClock": "PT12.3",
                "periodId": 2,
                "success": True,
                "timestamp": "2018-08-14T16:45:34.34",
                "clientId": "c2408302-9f75-11e8-98d0-529269fb1459",
                "clientType": "TestApi:1.1.2",
            },
        },
        qos=1,  # QoS level 0=at most once, 1=at least once, 2=exactly once
    )
    time.sleep(40)

    stream_api.disconnect()
```

For the available apis and models please check modules under `atriumsports.datacore.openapi`.

Using your IDE, navigate to this module to see all details of the generated API classes.
