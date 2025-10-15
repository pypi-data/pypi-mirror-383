# coding: utf-8

# flake8: noqa

"""
DataCore API  - Sport

# Introduction

The DataCore API is a REST based API. This means it makes use of the followng HTTP primitives:
 * GET - To retrieve data
 * POST - To add a record
 * PUT - To update a record
 * DELETE - To delete a record

All data sent and received as well as error messages is in the JSON format.

## Character Sets and Names

All data sent as both body and query parameters should be in the UTF-8 character set. All data returned will also be in UTF-8 strings.

A number of fields (especially names) have both a *local* and *latin* variant. The *local* variant is the string as it would be written in the local language of the organization.  The *latin* variant is the string as it would be written, only using latin characters/alphabet. Character sets like Cyrillic, Chinese are valid for the *local* string but not the *latin* string.  Regardless of the name, all strings should still be sent using UTF-8.

## Partial Responses

By default, the server sends back the full representation of a resource after processing requests. For better performance, you can ask the server to send only the fields you really need and get a partial response instead. This lets your application avoid transferring, parsing and storing un-needed data.

To request a partial response, use the `fields` query parameter to specify the fields you want returned.

    fields=dob,firstName,familyName,organization(id),organizations[name],teams[name,details/metrics/*,tags(id)]

### Syntax

 Character | Meaning
 --------- | -------
 **,**     | Delimits fields. All fields need to be delimited by a **,**.  eg. `fields=firstName,familyName`
 **/**     | Use `a/b` to select a field b that is nested within field a; use `a/b/c` to select a field c nested within b.
 **( )**   | The subselector allows you to specify a set of sub fields of an array or object by placing those fields in the parentheses. For example `competitors(name,address/state)` would return the name fields of the competitors key and the state field of the address key inside the competitors object.  This is also equivalent to `competitors/name,competitors/address/state`.
 **\***   | The wildcard character matches all fields at a level. eg. `*,organization/id` would return all fields, but only the id field of the organization key
 **[]**  | The field selection will generally only refer to the fields being returned in the *data* section on the response, but by giving the name of the resource type and then enclosing the field selection syntax in square brackets you can select which fields display in the *included* section as well. eg `firstName,familyName,organizations[name,id,country]` will display the firstName and familyName from the data element and only the name, id and country from the organizations resources in the include section.

All field references are relative to the `data` element.

If the resourceType and id fields are not displayed inside the data section for a sub-element, then the system will not make them available for [Resource Inclusion](#Resource_Inclusion), regardless of the use of the includes parameter.


## Pagination
When retrieving information using GET methods, the optional `limit` parameter sets the maximum number of rows to return in a response. The maximum is 1000. If this value is empty `limit` defaults to 10.

If more rows are available, the response will include a `next` element (inside the *links* section), which contains a URL for requesting the next page. If this value is not provided, no more rows are available. A `previous` page element is also provided if appropriate.

These URIs can be generated manually by using the `offset` parameter combined with the `limit` parameter. The `offset` parameter will return `limit` rows of data starting at the **offset + 1** row.


## Sorting
Where allowed, a route can have `sortBy` passed with a list of fields to sort by.  For each allowed field a `-` before the field name will denote DESC sort. The default sort is ASCENDING.
The below example will sort by `startTimeUTC` "descending" then `fixtureNumber` "ascending":

?sortBy=-startTimeUTC,fixtureNumber

## Resource Inclusion
When a response is returned it will not automatically include extra data from other resources/models. It will only list the resource type and id. eg.

        "competition" : {
            "resourceType" : "competitions",
            "id" : "009e9276-5c80-11e8-9c2d-fa7ae01bbebc"
        },
If specified in the query string the `include` parameter will expand that resource in the *includes* section of the response. The `include` parameter takes a comma separated list of resourceTypes to be included.

    /v1/sport/org/1/teams/009e9276-5c80-11e8-9c2d-fa7ae01bbebc?include=competitions,leagues

If the resourceType is included in the parameter and that resourceType is available in the response, then response will include an *includes* key.  Inside that *includes* key is a *resources* object.  Inside that object, there are keys for each type of included resourceType.  Inside each resourceType keyed against the id is an object representing that resource.

    {
        "meta": ...
        "links": ...
        "data": ...
        "includes": {
            "resources": {
                "competitions":
                    "009e9276-5c80-11e8-9c2d-fa7ae01bbebc": {
                        ...
                        Competition Resource Details
                        ...
                    }
                },
                "leagues": {
                    "009e9276-5c80-11e8-9c2d-fa7bc24e4ebc": {
                        ...
                        League Resource Details
                        ...
                    }
                }
            }
        }
    }

If the resourceType/id block is not available in the response, then the `include` will not link in the requested resource.  eg. an `include=competitions` in a fixtures call will not return anything as the competition resource is not returned in these calls. However, the include functionality also checks the included resources for resourceType/id blocks. This means that you can chain includes to get further along the data model.  For example an `include=competitions,seasons` in a fixtures call will return the competition resource as the competition resourceType/id block is returned in the season resource.

The list of available inclusions are


 code            | Resource
 -----            | -----
 `competitions`|Competitions
 `entities`      | Entities
 `entityGroups`|Entity Groups
 `fixtures`|Fixtures
 `leagues`       | Leagues
 `organizations` | Organizations
 `persons`|Persons
 `sites`|Sites
 `seasons`|Seasons
 `seasonPools`|Pools
 `seasonStages`|Stages
 `seasonRounds`|Rounds
 `venues`|Venues

## External Ids

The API allows certain end-points to be accessed via the externalId as supplied by the user.

The external parameter when used, lists the Ids that are to be replaced.

    /v1/sport/org/1/competitions/NL?external=competitionId

Below are a list of all the Ids that can be replaced.  These Ids can be replaced in GET, POST, PUT & DELETE calls.
* competitionId
* seasonId
* fixtureId
* siteId
* venueId
* entityGroupId
* entityId
* personId

The allowable format of an externalId is any character except:
* / (forward slash)
* ? (question mark)
* & (ampersand)

## Date formats

The API only accepts dates formatted in the ISO-8601 standard. These dates should be sent with **no** timezone qualifier. The correct timezone will be implied by the context of the call.

**Example:**

 For dates with a time component

     YYYY-MM-DDThh:mm:ss.s eg. 2017-06-29T18:20:00.00

 For dates with no time component

     YYYY-MM-DD eg. 2017-06-29

where
 YYYY = four-digit year
 MM = two-digit month (01=January, etc.)
 DD = two-digit day of month (01 through 31)
 hh = two digits of hour (00 through 23) (am/pm NOT allowed)
 mm = two digits of minute (00 through 59)
 ss = two digits of second (00 through 59)
 s = one or more digits representing a decimal fraction of a second

## UUIDs

The majority of objects in the API use a [universally unique identifier](https://en.wikipedia.org/wiki/Universally_unique_identifier) (uuid) as an identifier.  The uuid is a number, represented as 32 hexadecimal digits. There are a number of different versions of the uuid, but this API uses only uuid version 1.

When a new record (that uses a uuid) is created, this uuid can be generated by the client and included in the POST call.  If left blank, it will be automatically created by the server and return it in the response.

An example uuid is: `206c7392-b05f-11e8-96f8-529269fb1459`

## Images

Some API calls will return image objects for things such as logos or photos.  The url field of the image object contains the url where you will find that image.  This url is for the 'default' version of the image.  There are some query string parameters available to change how the image is returned.

`format`

 By default the image is returned in whatever format it was uploaded in, but by specifying the 'format' parameter you can change this.  Valid options are: `png`, `jpg`, `webp`.

`size`

By default the image is returned as a square of 100x100 pixels.  By specifying the 'size' parameter the image will be returned at a difference size.  The available options are

size parameter | dimensions
 -----            | -----
`100` | 100x100
`200` | 200x200
`400` | 400x400
`800` | 800x800
`1000` | 1000x1000
`RAW` | The original dimensions that the image was uploaded with

Images will not be scaled up. If you ask for an image with `size=400`, but the image is only 200x200 then the image will be returned as 200x200.

All images returned (apart from `size=RAW`) are square. If the original image that is uploaded is not square, then it is padded with a transparent (white for jpg) background.

An example url is: `https://img.dc.atriumsports.com/586aa6b195d243c4ae4154c8a61eda19?size=200&format=webp`

## DataCore Object Model

<a href = "https://yuml.me/diagram/scruffy;dir:LR/class/[Organizations]-<>[Persons],[Organizations]-.-<>[Leagues],[Organizations]-.-<>[Divisions],[Divisions]-.-<>[Conferences],[Organizations]-<>[Competitions],[Organizations]-<>[Entity Groups],[Organizations]-<>[Venues],[Organizations]-<>[Sites],[Organizations]-<>[Entities],[Competitions]-<>[Seasons],[Leagues]-.-<>[Competitions],[Seasons]-<>[Fixtures],[Fixtures]-2<>[~Competitors~],[~Competitors~]-.->[Conferences][Fixtures]-1[Venues],[Entity Groups]-.-<>[Entities],[Sites]-.-<>[Venues],[Fixtures]-<>[Fixture Roster],[Seasons]->[Stages],[Seasons]->[Pools],[Seasons]->[Rounds],[Fixtures]-.->[Stages],[Fixtures]-.->[Pools],[Fixtures]-.->[Rounds],[~Competitors~]<-[Entities],[Fixture Roster]<-[Persons],[Entities]->[Season Roster],[Season Roster]<-[Persons].jpg">
<img src="https://yuml.me/diagram/scruffy;dir:LR/class/[Organizations]-<>[Persons],[Organizations]-.-<>[Leagues],[Organizations]-.-<>[Divisions],[Divisions]-.-<>[Conferences],[Organizations]-<>[Competitions],[Organizations]-<>[Entity Groups],[Organizations]-<>[Venues],[Organizations]-<>[Sites],[Organizations]-<>[Entities],[Competitions]-<>[Seasons],[Leagues]-.-<>[Competitions],[Seasons]-<>[Fixtures],[Fixtures]-2<>[~Competitors~],[~Competitors~]-.->[Conferences][Fixtures]-1[Venues],[Entity Groups]-.-<>[Entities],[Sites]-.-<>[Venues],[Fixtures]-<>[Fixture Roster],[Seasons]->[Stages],[Seasons]->[Pools],[Seasons]->[Rounds],[Fixtures]-.->[Stages],[Fixtures]-.->[Pools],[Fixtures]-.->[Rounds],[~Competitors~]<-[Entities],[Fixture Roster]<-[Persons],[Entities]->[Season Roster],[Season Roster]<-[Persons]"></a>


More detailed information about each component is available in that section of the API documentation.

## Fixture Status Flow

Each fixture can have one of the following status values:
  * **IF_NEEDED** - Only played if needed
  * **BYE** - Entity has no fixture scheduled for this group of fixtures
  * **SCHEDULED** - Yet to be played
  * **PENDING** - Ready to start
  * **WARM_UP** - Players have begun to warm up
  * **ON_PITCH** - Players are on the playing field
  * **ABOUT_TO_START** - Fixture is about to start
  * **IN_PROGRESS** - Currently in play
  * **FINISHED** - Fixture finished but not yet 'official'
  * **CONFIRMED** - Fixture officially completed
  * **POSTPONED** - Will be played at a future time
  * **CANCELLED** - Will not be played
  * **ABANDONED** - Fixture began but had to be stopped

<img src="https://yuml.me/diagram/scruffy/activity/(start)-|a|,|a|->(IF_NEEDED)->(SCHEDULED),|a|->(BYE)->(SCHEDULED),|a|->(SCHEDULED)->(PENDING)->(WARM_UP)->(IN_PROGRESS)->(FINISHED)->(CONFIRMED)->(end),(SCHEDULED)->(CANCELLED)->(end),(SCHEDULED)->(ABANDONED)->(end),(SCHEDULED)->(POSTPONED)->(end),(IN_PROGRESS)->(ABANDONED)->(end)" >

## Bulk POST & PUT requests

When performing bulk POST or PUT requests, it is essential to consider the size of the payload to ensure optimal performance and avoid potential issues.

**Payload Size for Complex Structures**
For complex structures, such as Fixtures, the recommended number of rows to include in the payload is 70. This guideline helps maintain efficiency and reliability during data processing.

**Payload Size for Other Endpoints**
For other endpoints, it may be possible to handle larger payloads. However, it is crucial to analyze the performance and determine the appropriate size for your specific use case. Conduct thorough testing and monitoring to identify the optimal payload size that your system can handle without compromising performance.


## Limits/Throttling

All API requests are limited/throttled to prevent abuse and ensure stability.  There are two types of limiting in place:
 1. Usage Limits/Quota
    As a customer you would have been given a number of API calls that you are allowed to make each month. If you exceed this limit then your request will fail.
 2. Rate Limits
    As part of your plan you will also have limits as to how often you can make particular calls. For example you may only be able to call a particular endpoint once per minute.  If you exceed these limits then your request will fail.

# Authorization

This API uses the OAuth 2.0 protocol to authorize calls. OAuth is an open standard that many companies use to provide secure access to protected resources.

When you created an application in our management systems you would have been provided with an OAuth client ID and secret key.  By using these credentials and other parameters in a [get token](#token) call you will receive back an **access token**.

This **access token** must then be sent in the `Authorization` header for each subsequent API call.  Access tokens have a finite life and will expire. When the token expires you will need to create a new token to make more API calls.  Creation of tokens is rate-limited, so you should use the existing token as long as possible.

<!-- ReDoc-Inject: <security-definitions> -->
  # noqa: E501
"""

__version__ = "2.2.0"

# Define package exports
__all__ = [
    "AwardsApi",
    "CareerStatisticsApi",
    "ChangeLogApi",
    "CompetitionStatisticsApi",
    "CompetitionExternalIDsApi",
    "CompetitionsApi",
    "ConductApi",
    "ConferenceExternalIDsApi",
    "ConferencesDivisionsApi",
    "DivisionExternalIDsApi",
    "DownloadVideoApi",
    "EntitiesApi",
    "EntityFixtureHistoryApi",
    "EntityFixtureStatisticsApi",
    "EntityGroupExternalIDsApi",
    "EntityGroupsApi",
    "EntityExternalIDsApi",
    "FixtureEntitiesApi",
    "FixtureExternalPLAYBYPLAYApi",
    "FixtureLiveSummaryApi",
    "FixturePLAYBYPLAYApi",
    "FixturePersonsApi",
    "FixtureProfilesApi",
    "FixtureProgressionsApi",
    "FixtureRosterApi",
    "FixtureExternalIDsApi",
    "FixturesApi",
    "HeadToHeadFixturesApi",
    "ImagesApi",
    "LeaderCriteriaSetsApi",
    "LeaderQualifiersApi",
    "LeagueExternalIDsApi",
    "LeaguesApi",
    "LocalVideoEndpointsApi",
    "MergeRecordsApi",
    "OrganizationsApi",
    "PartnerAPIsApi",
    "PersonExternalIDsApi",
    "PersonFixtureHistoryApi",
    "PersonFixtureStatisticsApi",
    "PersonsApi",
    "RolesApi",
    "SeasonEntitiesApi",
    "SeasonEntityBaseStatisticsApi",
    "SeasonEntityPlacingsApi",
    "SeasonLeadersApi",
    "SeasonPersonBaseStatisticsApi",
    "SeasonPersonPlacingsApi",
    "SeasonPersonsApi",
    "SeasonRosterApi",
    "SeasonSeriesApi",
    "SeasonStatisticsApi",
    "SeasonExternalIDsApi",
    "SeasonsApi",
    "SiteExternalIDsApi",
    "SitesApi",
    "StagesPoolsRoundsApi",
    "StandingAdjustmentsApi",
    "StandingConfigurationsApi",
    "StandingProgressionsApi",
    "StandingsApi",
    "TransfersApi",
    "UniformItemsApi",
    "UniformsApi",
    "VenueExternalIDsApi",
    "VenuesApi",
    "VideoStreamInputsApi",
    "VideoStreamSubscriptionsApi",
    "VideoStreamsAvailableApi",
    "ApiResponse",
    "ApiClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "AwardPostBody",
    "AwardPutBody",
    "AwardsModel",
    "AwardsModelOrganization",
    "AwardsResponse",
    "BlankModelResponse",
    "Broadcasts",
    "CareerPersonRepresentationalStatisticsModel",
    "CareerPersonRepresentationalStatisticsModelOrganization",
    "CareerPersonRepresentationalStatisticsResponse",
    "CareerPersonSeasonStatisticsModel",
    "CareerPersonSeasonStatisticsModelOrganization",
    "CareerPersonSeasonStatisticsResponse",
    "CareerPersonStatisticsModel",
    "CareerPersonStatisticsModelOrganization",
    "CareerPersonStatisticsResponse",
    "ChangeLogModel",
    "ChangeLogModelOrganization",
    "ChangeLogResponse",
    "CompetitionEntityStatisticsModel",
    "CompetitionEntityStatisticsModelOrganization",
    "CompetitionEntityStatisticsResponse",
    "CompetitionExternalIdsModel",
    "CompetitionExternalIdsModelOrganization",
    "CompetitionExternalIdsPostBody",
    "CompetitionExternalIdsPutBody",
    "CompetitionExternalIdsResponse",
    "CompetitionHistoricalName",
    "CompetitionPersonStatisticsModel",
    "CompetitionPersonStatisticsModelOrganization",
    "CompetitionPersonStatisticsResponse",
    "CompetitionPostBody",
    "CompetitionPutBody",
    "CompetitionsModel",
    "CompetitionsModelLeague",
    "CompetitionsModelOrganization",
    "CompetitionsResponse",
    "CompetitionsSeasonStatusModel",
    "CompetitionsSeasonStatusModelLeague",
    "CompetitionsSeasonStatusModelOrganization",
    "CompetitionsSeasonStatusResponse",
    "ConductModel",
    "ConductModelOrganization",
    "ConductPenaltyResult",
    "ConductPostBody",
    "ConductPutBody",
    "ConductResponse",
    "ConferenceExternalIdsModel",
    "ConferenceExternalIdsModelOrganization",
    "ConferenceExternalIdsPostBody",
    "ConferenceExternalIdsPutBody",
    "ConferenceExternalIdsResponse",
    "ConferencePostBody",
    "ConferencePutBody",
    "ConferencesModel",
    "ConferencesModelOrganization",
    "ConferencesResponse",
    "ContactDetails",
    "DivisionExternalIdsModel",
    "DivisionExternalIdsModelOrganization",
    "DivisionExternalIdsPostBody",
    "DivisionExternalIdsPutBody",
    "DivisionExternalIdsResponse",
    "DivisionPostBody",
    "DivisionPutBody",
    "DivisionsModel",
    "DivisionsModelOrganization",
    "DivisionsResponse",
    "EntitiesModel",
    "EntitiesModelEntityGroup",
    "EntitiesModelOrganization",
    "EntitiesResponse",
    "EntityAdditionalDetails",
    "EntityAddress",
    "EntityExternalIdsModel",
    "EntityExternalIdsModelOrganization",
    "EntityExternalIdsPostBody",
    "EntityExternalIdsPutBody",
    "EntityExternalIdsResponse",
    "EntityGroupAddress",
    "EntityGroupExternalIdsModel",
    "EntityGroupExternalIdsModelOrganization",
    "EntityGroupExternalIdsPostBody",
    "EntityGroupExternalIdsPutBody",
    "EntityGroupExternalIdsResponse",
    "EntityGroupHistoricalName",
    "EntityGroupPostBody",
    "EntityGroupPostBodyAdditionalNames",
    "EntityGroupPostBodyColors",
    "EntityGroupPutBody",
    "EntityGroupsModel",
    "EntityGroupsModelOrganization",
    "EntityGroupsResponse",
    "EntityHistoricalName",
    "EntityPostBody",
    "EntityPostBodyAdditionalNames",
    "EntityPostBodyColors",
    "EntityPutBody",
    "EnvironmentalDetails",
    "ErrorListModel",
    "ErrorModel",
    "FixtureCompetitor",
    "FixtureEntitiesModel",
    "FixtureEntitiesModelConference",
    "FixtureEntitiesModelDivision",
    "FixtureEntitiesModelEntity",
    "FixtureEntitiesModelOrganization",
    "FixtureEntitiesModelUniform",
    "FixtureEntitiesPostBody",
    "FixtureEntitiesResponse",
    "FixtureEntityPeriodStatisticsPostBody",
    "FixtureEntityStatisticsModel",
    "FixtureEntityStatisticsModelOrganization",
    "FixtureEntityStatisticsPeriodsModel",
    "FixtureEntityStatisticsPeriodsModelOrganization",
    "FixtureEntityStatisticsPeriodsResponse",
    "FixtureEntityStatisticsPostBody",
    "FixtureEntityStatisticsResponse",
    "FixtureExternalIdsModel",
    "FixtureExternalIdsModelOrganization",
    "FixtureExternalIdsPostBody",
    "FixtureExternalIdsPutBody",
    "FixtureExternalIdsResponse",
    "FixtureLiveSummaryModel",
    "FixtureLiveSummaryResponse",
    "FixturePBPEventPostBody",
    "FixturePBPEventPutBody",
    "FixtureParticipant",
    "FixturePbpEventModel",
    "FixturePbpEventModelOrganization",
    "FixturePbpEventResponse",
    "FixturePbpExternalModel",
    "FixturePbpExternalModelOrganization",
    "FixturePbpExternalResponse",
    "FixturePbpModel",
    "FixturePbpModelOrganization",
    "FixturePbpResponse",
    "FixturePersonStatisticsModel",
    "FixturePersonStatisticsModelOrganization",
    "FixturePersonStatisticsPeriodsModel",
    "FixturePersonStatisticsPeriodsModelOrganization",
    "FixturePersonStatisticsPeriodsPostBody",
    "FixturePersonStatisticsPeriodsResponse",
    "FixturePersonStatisticsPostBody",
    "FixturePersonStatisticsResponse",
    "FixturePersonsModel",
    "FixturePersonsModelOrganization",
    "FixturePersonsModelPerson",
    "FixturePersonsPostBody",
    "FixturePersonsResponse",
    "FixturePostBody",
    "FixtureProfilesModel",
    "FixtureProfilesModelOrganization",
    "FixtureProfilesPostBody",
    "FixtureProfilesPutBody",
    "FixtureProfilesResponse",
    "FixtureProgressionPostBody",
    "FixtureProgressionPutBody",
    "FixtureProgressionsModel",
    "FixtureProgressionsModelFixture",
    "FixtureProgressionsModelOrganization",
    "FixtureProgressionsModelSeason",
    "FixtureProgressionsResponse",
    "FixturePutBody",
    "FixtureRosterModel",
    "FixtureRosterModelOrganization",
    "FixtureRosterPostBody",
    "FixtureRosterResponse",
    "FixtureVideosteamPostBody",
    "FixturesByCompetitionModel",
    "FixturesByCompetitionResponse",
    "FixturesByEntityModel",
    "FixturesByEntityResponse",
    "FixturesModel",
    "FixturesModelFixtureProfile",
    "FixturesModelOrganization",
    "FixturesModelRound",
    "FixturesModelSeries",
    "FixturesModelVenue",
    "FixturesResponse",
    "GameLogEntityModel",
    "GameLogEntityModelOrganization",
    "GameLogEntityResponse",
    "GameLogPersonModel",
    "GameLogPersonModelOrganization",
    "GameLogPersonResponse",
    "HeadToHeadEntityModel",
    "HeadToHeadEntityModelOrganization",
    "HeadToHeadEntityResponse",
    "HeadToHeadIdentification",
    "HeadToHeadIdentificationForSubsequentChecks",
    "HeadToHeadResolution",
    "HeadToHeadResolutionForExtraDepthH2hS",
    "ImagesModel",
    "ImagesModelOrganization",
    "ImagesPostBody",
    "ImagesPutBody",
    "ImagesResponse",
    "IncludedData",
    "InlineObject",
    "LeaderCriteriaModel",
    "LeaderCriteriaModelOrganization",
    "LeaderCriteriaPostBody",
    "LeaderCriteriaPutBody",
    "LeaderCriteriaResponse",
    "LeaderQualifierPostBody",
    "LeaderQualifierPutBody",
    "LeaderQualifiersModel",
    "LeaderQualifiersModelOrganization",
    "LeaderQualifiersResponse",
    "LeaderSummaryModel",
    "LeaderSummaryResponse",
    "LeagueExternalIdsModel",
    "LeagueExternalIdsModelLeague",
    "LeagueExternalIdsModelOrganization",
    "LeagueExternalIdsPostBody",
    "LeagueExternalIdsPutBody",
    "LeagueExternalIdsResponse",
    "LeaguePostBody",
    "LeaguePutBody",
    "LeaguesModel",
    "LeaguesModelOrganization",
    "LeaguesResponse",
    "OrganizationPostBody",
    "OrganizationPutBody",
    "OrganizationsModel",
    "OrganizationsResponse",
    "PersonAdditionalDetails",
    "PersonExternalIdsModel",
    "PersonExternalIdsModelOrganization",
    "PersonExternalIdsPostBody",
    "PersonExternalIdsPutBody",
    "PersonExternalIdsResponse",
    "PersonHistoricalName",
    "PersonPostBody",
    "PersonPostBodyAdditionalNamesValue",
    "PersonPutBody",
    "PersonsModel",
    "PersonsModelOrganization",
    "PersonsResponse",
    "PoolPostBody",
    "PoolPutBody",
    "ResponseLinks",
    "ResponseMetaData",
    "RolePostBody",
    "RolePutBody",
    "RolesModel",
    "RolesModelOrganization",
    "RolesResponse",
    "RoundPostBody",
    "RoundPutBody",
    "SEASONENTITYPlacingsPostBody",
    "SEASONENTITYPlacingsPutBody",
    "SEASONPERSONPlacingsPostBody",
    "SEASONPERSONPlacingsPutBody",
    "SEASONROSTERConfiguration",
    "SeasonEntitiesListModel",
    "SeasonEntitiesListModelOrganization",
    "SeasonEntitiesListResponse",
    "SeasonEntitiesModel",
    "SeasonEntitiesPostBody",
    "SeasonEntitiesResponse",
    "SeasonEntityBaseStatisticsModel",
    "SeasonEntityBaseStatisticsModelOrganization",
    "SeasonEntityBaseStatisticsPostBody",
    "SeasonEntityBaseStatisticsResponse",
    "SeasonEntityPlacingsModel",
    "SeasonEntityPlacingsModelOrganization",
    "SeasonEntityPlacingsResponse",
    "SeasonEntityStatisticsModel",
    "SeasonEntityStatisticsModelOrganization",
    "SeasonEntityStatisticsResponse",
    "SeasonExternalIdsModel",
    "SeasonExternalIdsModelOrganization",
    "SeasonExternalIdsPostBody",
    "SeasonExternalIdsPutBody",
    "SeasonExternalIdsResponse",
    "SeasonFixtureStagesPoolsListModel",
    "SeasonFixtureStagesPoolsListModelOrganization",
    "SeasonFixtureStagesPoolsListModelPool",
    "SeasonFixtureStagesPoolsListModelStage",
    "SeasonFixtureStagesPoolsListResponse",
    "SeasonPersonBaseStatisticsModel",
    "SeasonPersonBaseStatisticsModelOrganization",
    "SeasonPersonBaseStatisticsPostBody",
    "SeasonPersonBaseStatisticsResponse",
    "SeasonPersonPlacingsModel",
    "SeasonPersonPlacingsModelOrganization",
    "SeasonPersonPlacingsResponse",
    "SeasonPersonStatisticsModel",
    "SeasonPersonStatisticsModelOrganization",
    "SeasonPersonStatisticsPeriodsModel",
    "SeasonPersonStatisticsPeriodsResponse",
    "SeasonPersonStatisticsResponse",
    "SeasonPersonTotalStatisticsModel",
    "SeasonPersonTotalStatisticsModelOrganization",
    "SeasonPersonTotalStatisticsResponse",
    "SeasonPersonsListModel",
    "SeasonPersonsListModelOrganization",
    "SeasonPersonsListResponse",
    "SeasonPersonsModel",
    "SeasonPersonsPostBody",
    "SeasonPersonsResponse",
    "SeasonPoolsModel",
    "SeasonPoolsModelOrganization",
    "SeasonPoolsResponse",
    "SeasonPostBody",
    "SeasonPostBodyPromotionRelegationRulesInner",
    "SeasonPutBody",
    "SeasonRosterModel",
    "SeasonRosterModelOrganization",
    "SeasonRosterPostBody",
    "SeasonRosterResponse",
    "SeasonRoundsModel",
    "SeasonRoundsModelOrganization",
    "SeasonRoundsResponse",
    "SeasonSeriesCompetitor",
    "SeasonSeriesModel",
    "SeasonSeriesModelOrganization",
    "SeasonSeriesResponse",
    "SeasonStagePostBody",
    "SeasonStagePutBody",
    "SeasonStagesModel",
    "SeasonStagesModelOrganization",
    "SeasonStagesResponse",
    "SeasonStandingsStagesPoolsListModel",
    "SeasonStandingsStagesPoolsListModelOrganization",
    "SeasonStandingsStagesPoolsListResponse",
    "SeasonVenuesAddress",
    "SeasonVenuesListModel",
    "SeasonVenuesListModelOrganization",
    "SeasonVenuesListModelSite",
    "SeasonVenuesListResponse",
    "SeasonsModel",
    "SeasonsModelCompetition",
    "SeasonsModelFixtureProfile",
    "SeasonsModelLeadersCriteria",
    "SeasonsModelOrganization",
    "SeasonsModelStandingConfiguration",
    "SeasonsResponse",
    "SeriesPostBody",
    "SeriesPutBody",
    "SiteAddress",
    "SiteExternalIdsModel",
    "SiteExternalIdsModelOrganization",
    "SiteExternalIdsModelSite",
    "SiteExternalIdsPostBody",
    "SiteExternalIdsPutBody",
    "SiteExternalIdsResponse",
    "SitePostBody",
    "SitePutBody",
    "SitesModel",
    "SitesModelOrganization",
    "SitesResponse",
    "SocialMedia",
    "SocialMedia1",
    "Sorting",
    "StandingAdjustmentPostBody",
    "StandingAdjustmentPutBody",
    "StandingAdjustmentsModel",
    "StandingAdjustmentsModelOrganization",
    "StandingAdjustmentsResponse",
    "StandingBuilding",
    "StandingConfiguration",
    "StandingConfigurationsModel",
    "StandingConfigurationsModelOrganization",
    "StandingConfigurationsPostBody",
    "StandingConfigurationsPutBody",
    "StandingConfigurationsResponse",
    "StandingPostBody",
    "StandingPostBodyCalculatedValue",
    "StandingPostBodyPointsValue",
    "StandingProgressionsModel",
    "StandingProgressionsModelOrganization",
    "StandingProgressionsPostBody",
    "StandingProgressionsPutBody",
    "StandingProgressionsResponse",
    "StandingPutBody",
    "StandingsModel",
    "StandingsModelOrganization",
    "StandingsResponse",
    "SuccessModel",
    "SuccessResponse",
    "TransferComponent",
    "TransferPostBody",
    "TransferPutBody",
    "TransfersModel",
    "TransfersModelOrganization",
    "TransfersResponse",
    "UniformItemsModel",
    "UniformItemsModelOrganization",
    "UniformItemsPostBody",
    "UniformItemsPostBodyColors",
    "UniformItemsPutBody",
    "UniformItemsResponse",
    "UniformsModel",
    "UniformsModelOrganization",
    "UniformsPostBody",
    "UniformsPutBody",
    "UniformsResponse",
    "VenueAddress",
    "VenueExternalIdsModel",
    "VenueExternalIdsModelOrganization",
    "VenueExternalIdsPostBody",
    "VenueExternalIdsPutBody",
    "VenueExternalIdsResponse",
    "VenueHistoricalName",
    "VenuePostBody",
    "VenuePutBody",
    "VenuesModel",
    "VenuesModelOrganization",
    "VenuesModelSite",
    "VenuesResponse",
    "VideoFilePostBody",
    "VideoFilesDownloadModel",
    "VideoFilesDownloadResponse",
    "VideoFilesModel",
    "VideoFilesModelOrganization",
    "VideoFilesResponse",
    "VideoStreamInputsModel",
    "VideoStreamInputsModelOrganization",
    "VideoStreamInputsResponse",
    "VideoStreamLocalModel",
    "VideoStreamLocalModelOrganization",
    "VideoStreamLocalPostBody",
    "VideoStreamLocalPutBody",
    "VideoStreamLocalResponse",
    "VideoStreamOutputsModel",
    "VideoStreamOutputsModelOrganization",
    "VideoStreamOutputsResponse",
    "VideoSubscriptionPostBody",
    "VideoSubscriptionPutBody",
    "VideoSubscriptionsModel",
    "VideoSubscriptionsModelOrganization",
    "VideoSubscriptionsResponse",
]

# import apis into sdk package
from atriumsports.datacore.openapi.api.awards_api import AwardsApi as AwardsApi
from atriumsports.datacore.openapi.api.career_statistics_api import CareerStatisticsApi as CareerStatisticsApi
from atriumsports.datacore.openapi.api.change_log_api import ChangeLogApi as ChangeLogApi
from atriumsports.datacore.openapi.api.competition_statistics_api import (
    CompetitionStatisticsApi as CompetitionStatisticsApi,
)
from atriumsports.datacore.openapi.api.competition_external_ids_api import (
    CompetitionExternalIDsApi as CompetitionExternalIDsApi,
)
from atriumsports.datacore.openapi.api.competitions_api import CompetitionsApi as CompetitionsApi
from atriumsports.datacore.openapi.api.conduct_api import ConductApi as ConductApi
from atriumsports.datacore.openapi.api.conference_external_ids_api import (
    ConferenceExternalIDsApi as ConferenceExternalIDsApi,
)
from atriumsports.datacore.openapi.api.conferences_divisions_api import (
    ConferencesDivisionsApi as ConferencesDivisionsApi,
)
from atriumsports.datacore.openapi.api.division_external_ids_api import DivisionExternalIDsApi as DivisionExternalIDsApi
from atriumsports.datacore.openapi.api.download_video_api import DownloadVideoApi as DownloadVideoApi
from atriumsports.datacore.openapi.api.entities_api import EntitiesApi as EntitiesApi
from atriumsports.datacore.openapi.api.entity_fixture_history_api import (
    EntityFixtureHistoryApi as EntityFixtureHistoryApi,
)
from atriumsports.datacore.openapi.api.entity_fixture_statistics_api import (
    EntityFixtureStatisticsApi as EntityFixtureStatisticsApi,
)
from atriumsports.datacore.openapi.api.entity_group_external_ids_api import (
    EntityGroupExternalIDsApi as EntityGroupExternalIDsApi,
)
from atriumsports.datacore.openapi.api.entity_groups_api import EntityGroupsApi as EntityGroupsApi
from atriumsports.datacore.openapi.api.entity_external_ids_api import EntityExternalIDsApi as EntityExternalIDsApi
from atriumsports.datacore.openapi.api.fixture_entities_api import FixtureEntitiesApi as FixtureEntitiesApi
from atriumsports.datacore.openapi.api.fixture_external_playbyplay_api import (
    FixtureExternalPLAYBYPLAYApi as FixtureExternalPLAYBYPLAYApi,
)
from atriumsports.datacore.openapi.api.fixture_live_summary_api import FixtureLiveSummaryApi as FixtureLiveSummaryApi
from atriumsports.datacore.openapi.api.fixture_playbyplay_api import FixturePLAYBYPLAYApi as FixturePLAYBYPLAYApi
from atriumsports.datacore.openapi.api.fixture_persons_api import FixturePersonsApi as FixturePersonsApi
from atriumsports.datacore.openapi.api.fixture_profiles_api import FixtureProfilesApi as FixtureProfilesApi
from atriumsports.datacore.openapi.api.fixture_progressions_api import FixtureProgressionsApi as FixtureProgressionsApi
from atriumsports.datacore.openapi.api.fixture_roster_api import FixtureRosterApi as FixtureRosterApi
from atriumsports.datacore.openapi.api.fixture_external_ids_api import FixtureExternalIDsApi as FixtureExternalIDsApi
from atriumsports.datacore.openapi.api.fixtures_api import FixturesApi as FixturesApi
from atriumsports.datacore.openapi.api.head_to_head_fixtures_api import HeadToHeadFixturesApi as HeadToHeadFixturesApi
from atriumsports.datacore.openapi.api.images_api import ImagesApi as ImagesApi
from atriumsports.datacore.openapi.api.leader_criteria_sets_api import LeaderCriteriaSetsApi as LeaderCriteriaSetsApi
from atriumsports.datacore.openapi.api.leader_qualifiers_api import LeaderQualifiersApi as LeaderQualifiersApi
from atriumsports.datacore.openapi.api.league_external_ids_api import LeagueExternalIDsApi as LeagueExternalIDsApi
from atriumsports.datacore.openapi.api.leagues_api import LeaguesApi as LeaguesApi
from atriumsports.datacore.openapi.api.local_video_endpoints_api import LocalVideoEndpointsApi as LocalVideoEndpointsApi
from atriumsports.datacore.openapi.api.merge_records_api import MergeRecordsApi as MergeRecordsApi
from atriumsports.datacore.openapi.api.organizations_api import OrganizationsApi as OrganizationsApi
from atriumsports.datacore.openapi.api.partner_apis_api import PartnerAPIsApi as PartnerAPIsApi
from atriumsports.datacore.openapi.api.person_external_ids_api import PersonExternalIDsApi as PersonExternalIDsApi
from atriumsports.datacore.openapi.api.person_fixture_history_api import (
    PersonFixtureHistoryApi as PersonFixtureHistoryApi,
)
from atriumsports.datacore.openapi.api.person_fixture_statistics_api import (
    PersonFixtureStatisticsApi as PersonFixtureStatisticsApi,
)
from atriumsports.datacore.openapi.api.persons_api import PersonsApi as PersonsApi
from atriumsports.datacore.openapi.api.roles_api import RolesApi as RolesApi
from atriumsports.datacore.openapi.api.season_entities_api import SeasonEntitiesApi as SeasonEntitiesApi
from atriumsports.datacore.openapi.api.season_entity_base_statistics_api import (
    SeasonEntityBaseStatisticsApi as SeasonEntityBaseStatisticsApi,
)
from atriumsports.datacore.openapi.api.season_entity_placings_api import (
    SeasonEntityPlacingsApi as SeasonEntityPlacingsApi,
)
from atriumsports.datacore.openapi.api.season_leaders_api import SeasonLeadersApi as SeasonLeadersApi
from atriumsports.datacore.openapi.api.season_person_base_statistics_api import (
    SeasonPersonBaseStatisticsApi as SeasonPersonBaseStatisticsApi,
)
from atriumsports.datacore.openapi.api.season_person_placings_api import (
    SeasonPersonPlacingsApi as SeasonPersonPlacingsApi,
)
from atriumsports.datacore.openapi.api.season_persons_api import SeasonPersonsApi as SeasonPersonsApi
from atriumsports.datacore.openapi.api.season_roster_api import SeasonRosterApi as SeasonRosterApi
from atriumsports.datacore.openapi.api.season_series_api import SeasonSeriesApi as SeasonSeriesApi
from atriumsports.datacore.openapi.api.season_statistics_api import SeasonStatisticsApi as SeasonStatisticsApi
from atriumsports.datacore.openapi.api.season_external_ids_api import SeasonExternalIDsApi as SeasonExternalIDsApi
from atriumsports.datacore.openapi.api.seasons_api import SeasonsApi as SeasonsApi
from atriumsports.datacore.openapi.api.site_external_ids_api import SiteExternalIDsApi as SiteExternalIDsApi
from atriumsports.datacore.openapi.api.sites_api import SitesApi as SitesApi
from atriumsports.datacore.openapi.api.stages_pools_rounds_api import StagesPoolsRoundsApi as StagesPoolsRoundsApi
from atriumsports.datacore.openapi.api.standing_adjustments_api import StandingAdjustmentsApi as StandingAdjustmentsApi
from atriumsports.datacore.openapi.api.standing_configurations_api import (
    StandingConfigurationsApi as StandingConfigurationsApi,
)
from atriumsports.datacore.openapi.api.standing_progressions_api import (
    StandingProgressionsApi as StandingProgressionsApi,
)
from atriumsports.datacore.openapi.api.standings_api import StandingsApi as StandingsApi
from atriumsports.datacore.openapi.api.transfers_api import TransfersApi as TransfersApi
from atriumsports.datacore.openapi.api.uniform_items_api import UniformItemsApi as UniformItemsApi
from atriumsports.datacore.openapi.api.uniforms_api import UniformsApi as UniformsApi
from atriumsports.datacore.openapi.api.venue_external_ids_api import VenueExternalIDsApi as VenueExternalIDsApi
from atriumsports.datacore.openapi.api.venues_api import VenuesApi as VenuesApi
from atriumsports.datacore.openapi.api.video_stream_inputs_api import VideoStreamInputsApi as VideoStreamInputsApi
from atriumsports.datacore.openapi.api.video_stream_subscriptions_api import (
    VideoStreamSubscriptionsApi as VideoStreamSubscriptionsApi,
)
from atriumsports.datacore.openapi.api.video_streams_available_api import (
    VideoStreamsAvailableApi as VideoStreamsAvailableApi,
)

# import ApiClient
from atriumsports.datacore.openapi.api_response import ApiResponse as ApiResponse
from atriumsports.datacore.openapi.api_client import ApiClient as ApiClient
from atriumsports.datacore.openapi.configuration import Configuration as Configuration
from atriumsports.datacore.openapi.exceptions import OpenApiException as OpenApiException
from atriumsports.datacore.openapi.exceptions import ApiTypeError as ApiTypeError
from atriumsports.datacore.openapi.exceptions import ApiValueError as ApiValueError
from atriumsports.datacore.openapi.exceptions import ApiKeyError as ApiKeyError
from atriumsports.datacore.openapi.exceptions import ApiAttributeError as ApiAttributeError
from atriumsports.datacore.openapi.exceptions import ApiException as ApiException

# import models into sdk package
from atriumsports.datacore.openapi.models.award_post_body import AwardPostBody as AwardPostBody
from atriumsports.datacore.openapi.models.award_put_body import AwardPutBody as AwardPutBody
from atriumsports.datacore.openapi.models.awards_model import AwardsModel as AwardsModel
from atriumsports.datacore.openapi.models.awards_model_organization import (
    AwardsModelOrganization as AwardsModelOrganization,
)
from atriumsports.datacore.openapi.models.awards_response import AwardsResponse as AwardsResponse
from atriumsports.datacore.openapi.models.blank_model_response import BlankModelResponse as BlankModelResponse
from atriumsports.datacore.openapi.models.broadcasts import Broadcasts as Broadcasts
from atriumsports.datacore.openapi.models.career_person_representational_statistics_model import (
    CareerPersonRepresentationalStatisticsModel as CareerPersonRepresentationalStatisticsModel,
)
from atriumsports.datacore.openapi.models.career_person_representational_statistics_model_organization import (
    CareerPersonRepresentationalStatisticsModelOrganization as CareerPersonRepresentationalStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.career_person_representational_statistics_response import (
    CareerPersonRepresentationalStatisticsResponse as CareerPersonRepresentationalStatisticsResponse,
)
from atriumsports.datacore.openapi.models.career_person_season_statistics_model import (
    CareerPersonSeasonStatisticsModel as CareerPersonSeasonStatisticsModel,
)
from atriumsports.datacore.openapi.models.career_person_season_statistics_model_organization import (
    CareerPersonSeasonStatisticsModelOrganization as CareerPersonSeasonStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.career_person_season_statistics_response import (
    CareerPersonSeasonStatisticsResponse as CareerPersonSeasonStatisticsResponse,
)
from atriumsports.datacore.openapi.models.career_person_statistics_model import (
    CareerPersonStatisticsModel as CareerPersonStatisticsModel,
)
from atriumsports.datacore.openapi.models.career_person_statistics_model_organization import (
    CareerPersonStatisticsModelOrganization as CareerPersonStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.career_person_statistics_response import (
    CareerPersonStatisticsResponse as CareerPersonStatisticsResponse,
)
from atriumsports.datacore.openapi.models.change_log_model import ChangeLogModel as ChangeLogModel
from atriumsports.datacore.openapi.models.change_log_model_organization import (
    ChangeLogModelOrganization as ChangeLogModelOrganization,
)
from atriumsports.datacore.openapi.models.change_log_response import ChangeLogResponse as ChangeLogResponse
from atriumsports.datacore.openapi.models.competition_entity_statistics_model import (
    CompetitionEntityStatisticsModel as CompetitionEntityStatisticsModel,
)
from atriumsports.datacore.openapi.models.competition_entity_statistics_model_organization import (
    CompetitionEntityStatisticsModelOrganization as CompetitionEntityStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.competition_entity_statistics_response import (
    CompetitionEntityStatisticsResponse as CompetitionEntityStatisticsResponse,
)
from atriumsports.datacore.openapi.models.competition_external_ids_model import (
    CompetitionExternalIdsModel as CompetitionExternalIdsModel,
)
from atriumsports.datacore.openapi.models.competition_external_ids_model_organization import (
    CompetitionExternalIdsModelOrganization as CompetitionExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.competition_external_ids_post_body import (
    CompetitionExternalIdsPostBody as CompetitionExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.competition_external_ids_put_body import (
    CompetitionExternalIdsPutBody as CompetitionExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.competition_external_ids_response import (
    CompetitionExternalIdsResponse as CompetitionExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.competition_historical_name import (
    CompetitionHistoricalName as CompetitionHistoricalName,
)
from atriumsports.datacore.openapi.models.competition_person_statistics_model import (
    CompetitionPersonStatisticsModel as CompetitionPersonStatisticsModel,
)
from atriumsports.datacore.openapi.models.competition_person_statistics_model_organization import (
    CompetitionPersonStatisticsModelOrganization as CompetitionPersonStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.competition_person_statistics_response import (
    CompetitionPersonStatisticsResponse as CompetitionPersonStatisticsResponse,
)
from atriumsports.datacore.openapi.models.competition_post_body import CompetitionPostBody as CompetitionPostBody
from atriumsports.datacore.openapi.models.competition_put_body import CompetitionPutBody as CompetitionPutBody
from atriumsports.datacore.openapi.models.competitions_model import CompetitionsModel as CompetitionsModel
from atriumsports.datacore.openapi.models.competitions_model_league import (
    CompetitionsModelLeague as CompetitionsModelLeague,
)
from atriumsports.datacore.openapi.models.competitions_model_organization import (
    CompetitionsModelOrganization as CompetitionsModelOrganization,
)
from atriumsports.datacore.openapi.models.competitions_response import CompetitionsResponse as CompetitionsResponse
from atriumsports.datacore.openapi.models.competitions_season_status_model import (
    CompetitionsSeasonStatusModel as CompetitionsSeasonStatusModel,
)
from atriumsports.datacore.openapi.models.competitions_season_status_model_league import (
    CompetitionsSeasonStatusModelLeague as CompetitionsSeasonStatusModelLeague,
)
from atriumsports.datacore.openapi.models.competitions_season_status_model_organization import (
    CompetitionsSeasonStatusModelOrganization as CompetitionsSeasonStatusModelOrganization,
)
from atriumsports.datacore.openapi.models.competitions_season_status_response import (
    CompetitionsSeasonStatusResponse as CompetitionsSeasonStatusResponse,
)
from atriumsports.datacore.openapi.models.conduct_model import ConductModel as ConductModel
from atriumsports.datacore.openapi.models.conduct_model_organization import (
    ConductModelOrganization as ConductModelOrganization,
)
from atriumsports.datacore.openapi.models.conduct_penalty_result import ConductPenaltyResult as ConductPenaltyResult
from atriumsports.datacore.openapi.models.conduct_post_body import ConductPostBody as ConductPostBody
from atriumsports.datacore.openapi.models.conduct_put_body import ConductPutBody as ConductPutBody
from atriumsports.datacore.openapi.models.conduct_response import ConductResponse as ConductResponse
from atriumsports.datacore.openapi.models.conference_external_ids_model import (
    ConferenceExternalIdsModel as ConferenceExternalIdsModel,
)
from atriumsports.datacore.openapi.models.conference_external_ids_model_organization import (
    ConferenceExternalIdsModelOrganization as ConferenceExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.conference_external_ids_post_body import (
    ConferenceExternalIdsPostBody as ConferenceExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.conference_external_ids_put_body import (
    ConferenceExternalIdsPutBody as ConferenceExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.conference_external_ids_response import (
    ConferenceExternalIdsResponse as ConferenceExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.conference_post_body import ConferencePostBody as ConferencePostBody
from atriumsports.datacore.openapi.models.conference_put_body import ConferencePutBody as ConferencePutBody
from atriumsports.datacore.openapi.models.conferences_model import ConferencesModel as ConferencesModel
from atriumsports.datacore.openapi.models.conferences_model_organization import (
    ConferencesModelOrganization as ConferencesModelOrganization,
)
from atriumsports.datacore.openapi.models.conferences_response import ConferencesResponse as ConferencesResponse
from atriumsports.datacore.openapi.models.contact_details import ContactDetails as ContactDetails
from atriumsports.datacore.openapi.models.division_external_ids_model import (
    DivisionExternalIdsModel as DivisionExternalIdsModel,
)
from atriumsports.datacore.openapi.models.division_external_ids_model_organization import (
    DivisionExternalIdsModelOrganization as DivisionExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.division_external_ids_post_body import (
    DivisionExternalIdsPostBody as DivisionExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.division_external_ids_put_body import (
    DivisionExternalIdsPutBody as DivisionExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.division_external_ids_response import (
    DivisionExternalIdsResponse as DivisionExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.division_post_body import DivisionPostBody as DivisionPostBody
from atriumsports.datacore.openapi.models.division_put_body import DivisionPutBody as DivisionPutBody
from atriumsports.datacore.openapi.models.divisions_model import DivisionsModel as DivisionsModel
from atriumsports.datacore.openapi.models.divisions_model_organization import (
    DivisionsModelOrganization as DivisionsModelOrganization,
)
from atriumsports.datacore.openapi.models.divisions_response import DivisionsResponse as DivisionsResponse
from atriumsports.datacore.openapi.models.entities_model import EntitiesModel as EntitiesModel
from atriumsports.datacore.openapi.models.entities_model_entity_group import (
    EntitiesModelEntityGroup as EntitiesModelEntityGroup,
)
from atriumsports.datacore.openapi.models.entities_model_organization import (
    EntitiesModelOrganization as EntitiesModelOrganization,
)
from atriumsports.datacore.openapi.models.entities_response import EntitiesResponse as EntitiesResponse
from atriumsports.datacore.openapi.models.entity_additional_details import (
    EntityAdditionalDetails as EntityAdditionalDetails,
)
from atriumsports.datacore.openapi.models.entity_address import EntityAddress as EntityAddress
from atriumsports.datacore.openapi.models.entity_external_ids_model import (
    EntityExternalIdsModel as EntityExternalIdsModel,
)
from atriumsports.datacore.openapi.models.entity_external_ids_model_organization import (
    EntityExternalIdsModelOrganization as EntityExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.entity_external_ids_post_body import (
    EntityExternalIdsPostBody as EntityExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.entity_external_ids_put_body import (
    EntityExternalIdsPutBody as EntityExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.entity_external_ids_response import (
    EntityExternalIdsResponse as EntityExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.entity_group_address import EntityGroupAddress as EntityGroupAddress
from atriumsports.datacore.openapi.models.entity_group_external_ids_model import (
    EntityGroupExternalIdsModel as EntityGroupExternalIdsModel,
)
from atriumsports.datacore.openapi.models.entity_group_external_ids_model_organization import (
    EntityGroupExternalIdsModelOrganization as EntityGroupExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.entity_group_external_ids_post_body import (
    EntityGroupExternalIdsPostBody as EntityGroupExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.entity_group_external_ids_put_body import (
    EntityGroupExternalIdsPutBody as EntityGroupExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.entity_group_external_ids_response import (
    EntityGroupExternalIdsResponse as EntityGroupExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.entity_group_historical_name import (
    EntityGroupHistoricalName as EntityGroupHistoricalName,
)
from atriumsports.datacore.openapi.models.entity_group_post_body import EntityGroupPostBody as EntityGroupPostBody
from atriumsports.datacore.openapi.models.entity_group_post_body_additional_names import (
    EntityGroupPostBodyAdditionalNames as EntityGroupPostBodyAdditionalNames,
)
from atriumsports.datacore.openapi.models.entity_group_post_body_colors import (
    EntityGroupPostBodyColors as EntityGroupPostBodyColors,
)
from atriumsports.datacore.openapi.models.entity_group_put_body import EntityGroupPutBody as EntityGroupPutBody
from atriumsports.datacore.openapi.models.entity_groups_model import EntityGroupsModel as EntityGroupsModel
from atriumsports.datacore.openapi.models.entity_groups_model_organization import (
    EntityGroupsModelOrganization as EntityGroupsModelOrganization,
)
from atriumsports.datacore.openapi.models.entity_groups_response import EntityGroupsResponse as EntityGroupsResponse
from atriumsports.datacore.openapi.models.entity_historical_name import EntityHistoricalName as EntityHistoricalName
from atriumsports.datacore.openapi.models.entity_post_body import EntityPostBody as EntityPostBody
from atriumsports.datacore.openapi.models.entity_post_body_additional_names import (
    EntityPostBodyAdditionalNames as EntityPostBodyAdditionalNames,
)
from atriumsports.datacore.openapi.models.entity_post_body_colors import EntityPostBodyColors as EntityPostBodyColors
from atriumsports.datacore.openapi.models.entity_put_body import EntityPutBody as EntityPutBody
from atriumsports.datacore.openapi.models.environmental_details import EnvironmentalDetails as EnvironmentalDetails
from atriumsports.datacore.openapi.models.error_list_model import ErrorListModel as ErrorListModel
from atriumsports.datacore.openapi.models.error_model import ErrorModel as ErrorModel
from atriumsports.datacore.openapi.models.fixture_competitor import FixtureCompetitor as FixtureCompetitor
from atriumsports.datacore.openapi.models.fixture_entities_model import FixtureEntitiesModel as FixtureEntitiesModel
from atriumsports.datacore.openapi.models.fixture_entities_model_conference import (
    FixtureEntitiesModelConference as FixtureEntitiesModelConference,
)
from atriumsports.datacore.openapi.models.fixture_entities_model_division import (
    FixtureEntitiesModelDivision as FixtureEntitiesModelDivision,
)
from atriumsports.datacore.openapi.models.fixture_entities_model_entity import (
    FixtureEntitiesModelEntity as FixtureEntitiesModelEntity,
)
from atriumsports.datacore.openapi.models.fixture_entities_model_organization import (
    FixtureEntitiesModelOrganization as FixtureEntitiesModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_entities_model_uniform import (
    FixtureEntitiesModelUniform as FixtureEntitiesModelUniform,
)
from atriumsports.datacore.openapi.models.fixture_entities_post_body import (
    FixtureEntitiesPostBody as FixtureEntitiesPostBody,
)
from atriumsports.datacore.openapi.models.fixture_entities_response import (
    FixtureEntitiesResponse as FixtureEntitiesResponse,
)
from atriumsports.datacore.openapi.models.fixture_entity_period_statistics_post_body import (
    FixtureEntityPeriodStatisticsPostBody as FixtureEntityPeriodStatisticsPostBody,
)
from atriumsports.datacore.openapi.models.fixture_entity_statistics_model import (
    FixtureEntityStatisticsModel as FixtureEntityStatisticsModel,
)
from atriumsports.datacore.openapi.models.fixture_entity_statistics_model_organization import (
    FixtureEntityStatisticsModelOrganization as FixtureEntityStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_entity_statistics_periods_model import (
    FixtureEntityStatisticsPeriodsModel as FixtureEntityStatisticsPeriodsModel,
)
from atriumsports.datacore.openapi.models.fixture_entity_statistics_periods_model_organization import (
    FixtureEntityStatisticsPeriodsModelOrganization as FixtureEntityStatisticsPeriodsModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_entity_statistics_periods_response import (
    FixtureEntityStatisticsPeriodsResponse as FixtureEntityStatisticsPeriodsResponse,
)
from atriumsports.datacore.openapi.models.fixture_entity_statistics_post_body import (
    FixtureEntityStatisticsPostBody as FixtureEntityStatisticsPostBody,
)
from atriumsports.datacore.openapi.models.fixture_entity_statistics_response import (
    FixtureEntityStatisticsResponse as FixtureEntityStatisticsResponse,
)
from atriumsports.datacore.openapi.models.fixture_external_ids_model import (
    FixtureExternalIdsModel as FixtureExternalIdsModel,
)
from atriumsports.datacore.openapi.models.fixture_external_ids_model_organization import (
    FixtureExternalIdsModelOrganization as FixtureExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_external_ids_post_body import (
    FixtureExternalIdsPostBody as FixtureExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.fixture_external_ids_put_body import (
    FixtureExternalIdsPutBody as FixtureExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.fixture_external_ids_response import (
    FixtureExternalIdsResponse as FixtureExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.fixture_live_summary_model import (
    FixtureLiveSummaryModel as FixtureLiveSummaryModel,
)
from atriumsports.datacore.openapi.models.fixture_live_summary_response import (
    FixtureLiveSummaryResponse as FixtureLiveSummaryResponse,
)
from atriumsports.datacore.openapi.models.fixture_pbp_event_post_body import (
    FixturePBPEventPostBody as FixturePBPEventPostBody,
)
from atriumsports.datacore.openapi.models.fixture_pbp_event_put_body import (
    FixturePBPEventPutBody as FixturePBPEventPutBody,
)
from atriumsports.datacore.openapi.models.fixture_participant import FixtureParticipant as FixtureParticipant
from atriumsports.datacore.openapi.models.fixture_pbp_event_model import FixturePbpEventModel as FixturePbpEventModel
from atriumsports.datacore.openapi.models.fixture_pbp_event_model_organization import (
    FixturePbpEventModelOrganization as FixturePbpEventModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_pbp_event_response import (
    FixturePbpEventResponse as FixturePbpEventResponse,
)
from atriumsports.datacore.openapi.models.fixture_pbp_external_model import (
    FixturePbpExternalModel as FixturePbpExternalModel,
)
from atriumsports.datacore.openapi.models.fixture_pbp_external_model_organization import (
    FixturePbpExternalModelOrganization as FixturePbpExternalModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_pbp_external_response import (
    FixturePbpExternalResponse as FixturePbpExternalResponse,
)
from atriumsports.datacore.openapi.models.fixture_pbp_model import FixturePbpModel as FixturePbpModel
from atriumsports.datacore.openapi.models.fixture_pbp_model_organization import (
    FixturePbpModelOrganization as FixturePbpModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_pbp_response import FixturePbpResponse as FixturePbpResponse
from atriumsports.datacore.openapi.models.fixture_person_statistics_model import (
    FixturePersonStatisticsModel as FixturePersonStatisticsModel,
)
from atriumsports.datacore.openapi.models.fixture_person_statistics_model_organization import (
    FixturePersonStatisticsModelOrganization as FixturePersonStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_person_statistics_periods_model import (
    FixturePersonStatisticsPeriodsModel as FixturePersonStatisticsPeriodsModel,
)
from atriumsports.datacore.openapi.models.fixture_person_statistics_periods_model_organization import (
    FixturePersonStatisticsPeriodsModelOrganization as FixturePersonStatisticsPeriodsModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_person_statistics_periods_post_body import (
    FixturePersonStatisticsPeriodsPostBody as FixturePersonStatisticsPeriodsPostBody,
)
from atriumsports.datacore.openapi.models.fixture_person_statistics_periods_response import (
    FixturePersonStatisticsPeriodsResponse as FixturePersonStatisticsPeriodsResponse,
)
from atriumsports.datacore.openapi.models.fixture_person_statistics_post_body import (
    FixturePersonStatisticsPostBody as FixturePersonStatisticsPostBody,
)
from atriumsports.datacore.openapi.models.fixture_person_statistics_response import (
    FixturePersonStatisticsResponse as FixturePersonStatisticsResponse,
)
from atriumsports.datacore.openapi.models.fixture_persons_model import FixturePersonsModel as FixturePersonsModel
from atriumsports.datacore.openapi.models.fixture_persons_model_organization import (
    FixturePersonsModelOrganization as FixturePersonsModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_persons_model_person import (
    FixturePersonsModelPerson as FixturePersonsModelPerson,
)
from atriumsports.datacore.openapi.models.fixture_persons_post_body import (
    FixturePersonsPostBody as FixturePersonsPostBody,
)
from atriumsports.datacore.openapi.models.fixture_persons_response import (
    FixturePersonsResponse as FixturePersonsResponse,
)
from atriumsports.datacore.openapi.models.fixture_post_body import FixturePostBody as FixturePostBody
from atriumsports.datacore.openapi.models.fixture_profiles_model import FixtureProfilesModel as FixtureProfilesModel
from atriumsports.datacore.openapi.models.fixture_profiles_model_organization import (
    FixtureProfilesModelOrganization as FixtureProfilesModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_profiles_post_body import (
    FixtureProfilesPostBody as FixtureProfilesPostBody,
)
from atriumsports.datacore.openapi.models.fixture_profiles_put_body import (
    FixtureProfilesPutBody as FixtureProfilesPutBody,
)
from atriumsports.datacore.openapi.models.fixture_profiles_response import (
    FixtureProfilesResponse as FixtureProfilesResponse,
)
from atriumsports.datacore.openapi.models.fixture_progression_post_body import (
    FixtureProgressionPostBody as FixtureProgressionPostBody,
)
from atriumsports.datacore.openapi.models.fixture_progression_put_body import (
    FixtureProgressionPutBody as FixtureProgressionPutBody,
)
from atriumsports.datacore.openapi.models.fixture_progressions_model import (
    FixtureProgressionsModel as FixtureProgressionsModel,
)
from atriumsports.datacore.openapi.models.fixture_progressions_model_fixture import (
    FixtureProgressionsModelFixture as FixtureProgressionsModelFixture,
)
from atriumsports.datacore.openapi.models.fixture_progressions_model_organization import (
    FixtureProgressionsModelOrganization as FixtureProgressionsModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_progressions_model_season import (
    FixtureProgressionsModelSeason as FixtureProgressionsModelSeason,
)
from atriumsports.datacore.openapi.models.fixture_progressions_response import (
    FixtureProgressionsResponse as FixtureProgressionsResponse,
)
from atriumsports.datacore.openapi.models.fixture_put_body import FixturePutBody as FixturePutBody
from atriumsports.datacore.openapi.models.fixture_roster_model import FixtureRosterModel as FixtureRosterModel
from atriumsports.datacore.openapi.models.fixture_roster_model_organization import (
    FixtureRosterModelOrganization as FixtureRosterModelOrganization,
)
from atriumsports.datacore.openapi.models.fixture_roster_post_body import FixtureRosterPostBody as FixtureRosterPostBody
from atriumsports.datacore.openapi.models.fixture_roster_response import FixtureRosterResponse as FixtureRosterResponse
from atriumsports.datacore.openapi.models.fixture_videosteam_post_body import (
    FixtureVideosteamPostBody as FixtureVideosteamPostBody,
)
from atriumsports.datacore.openapi.models.fixtures_by_competition_model import (
    FixturesByCompetitionModel as FixturesByCompetitionModel,
)
from atriumsports.datacore.openapi.models.fixtures_by_competition_response import (
    FixturesByCompetitionResponse as FixturesByCompetitionResponse,
)
from atriumsports.datacore.openapi.models.fixtures_by_entity_model import FixturesByEntityModel as FixturesByEntityModel
from atriumsports.datacore.openapi.models.fixtures_by_entity_response import (
    FixturesByEntityResponse as FixturesByEntityResponse,
)
from atriumsports.datacore.openapi.models.fixtures_model import FixturesModel as FixturesModel
from atriumsports.datacore.openapi.models.fixtures_model_fixture_profile import (
    FixturesModelFixtureProfile as FixturesModelFixtureProfile,
)
from atriumsports.datacore.openapi.models.fixtures_model_organization import (
    FixturesModelOrganization as FixturesModelOrganization,
)
from atriumsports.datacore.openapi.models.fixtures_model_round import FixturesModelRound as FixturesModelRound
from atriumsports.datacore.openapi.models.fixtures_model_series import FixturesModelSeries as FixturesModelSeries
from atriumsports.datacore.openapi.models.fixtures_model_venue import FixturesModelVenue as FixturesModelVenue
from atriumsports.datacore.openapi.models.fixtures_response import FixturesResponse as FixturesResponse
from atriumsports.datacore.openapi.models.game_log_entity_model import GameLogEntityModel as GameLogEntityModel
from atriumsports.datacore.openapi.models.game_log_entity_model_organization import (
    GameLogEntityModelOrganization as GameLogEntityModelOrganization,
)
from atriumsports.datacore.openapi.models.game_log_entity_response import GameLogEntityResponse as GameLogEntityResponse
from atriumsports.datacore.openapi.models.game_log_person_model import GameLogPersonModel as GameLogPersonModel
from atriumsports.datacore.openapi.models.game_log_person_model_organization import (
    GameLogPersonModelOrganization as GameLogPersonModelOrganization,
)
from atriumsports.datacore.openapi.models.game_log_person_response import GameLogPersonResponse as GameLogPersonResponse
from atriumsports.datacore.openapi.models.head_to_head_entity_model import (
    HeadToHeadEntityModel as HeadToHeadEntityModel,
)
from atriumsports.datacore.openapi.models.head_to_head_entity_model_organization import (
    HeadToHeadEntityModelOrganization as HeadToHeadEntityModelOrganization,
)
from atriumsports.datacore.openapi.models.head_to_head_entity_response import (
    HeadToHeadEntityResponse as HeadToHeadEntityResponse,
)
from atriumsports.datacore.openapi.models.head_to_head_identification import (
    HeadToHeadIdentification as HeadToHeadIdentification,
)
from atriumsports.datacore.openapi.models.head_to_head_identification_for_subsequent_checks import (
    HeadToHeadIdentificationForSubsequentChecks as HeadToHeadIdentificationForSubsequentChecks,
)
from atriumsports.datacore.openapi.models.head_to_head_resolution import HeadToHeadResolution as HeadToHeadResolution
from atriumsports.datacore.openapi.models.head_to_head_resolution_for_extra_depth_h2h_s import (
    HeadToHeadResolutionForExtraDepthH2hS as HeadToHeadResolutionForExtraDepthH2hS,
)
from atriumsports.datacore.openapi.models.images_model import ImagesModel as ImagesModel
from atriumsports.datacore.openapi.models.images_model_organization import (
    ImagesModelOrganization as ImagesModelOrganization,
)
from atriumsports.datacore.openapi.models.images_post_body import ImagesPostBody as ImagesPostBody
from atriumsports.datacore.openapi.models.images_put_body import ImagesPutBody as ImagesPutBody
from atriumsports.datacore.openapi.models.images_response import ImagesResponse as ImagesResponse
from atriumsports.datacore.openapi.models.included_data import IncludedData as IncludedData
from atriumsports.datacore.openapi.models.inline_object import InlineObject as InlineObject
from atriumsports.datacore.openapi.models.leader_criteria_model import LeaderCriteriaModel as LeaderCriteriaModel
from atriumsports.datacore.openapi.models.leader_criteria_model_organization import (
    LeaderCriteriaModelOrganization as LeaderCriteriaModelOrganization,
)
from atriumsports.datacore.openapi.models.leader_criteria_post_body import (
    LeaderCriteriaPostBody as LeaderCriteriaPostBody,
)
from atriumsports.datacore.openapi.models.leader_criteria_put_body import LeaderCriteriaPutBody as LeaderCriteriaPutBody
from atriumsports.datacore.openapi.models.leader_criteria_response import (
    LeaderCriteriaResponse as LeaderCriteriaResponse,
)
from atriumsports.datacore.openapi.models.leader_qualifier_post_body import (
    LeaderQualifierPostBody as LeaderQualifierPostBody,
)
from atriumsports.datacore.openapi.models.leader_qualifier_put_body import (
    LeaderQualifierPutBody as LeaderQualifierPutBody,
)
from atriumsports.datacore.openapi.models.leader_qualifiers_model import LeaderQualifiersModel as LeaderQualifiersModel
from atriumsports.datacore.openapi.models.leader_qualifiers_model_organization import (
    LeaderQualifiersModelOrganization as LeaderQualifiersModelOrganization,
)
from atriumsports.datacore.openapi.models.leader_qualifiers_response import (
    LeaderQualifiersResponse as LeaderQualifiersResponse,
)
from atriumsports.datacore.openapi.models.leader_summary_model import LeaderSummaryModel as LeaderSummaryModel
from atriumsports.datacore.openapi.models.leader_summary_response import LeaderSummaryResponse as LeaderSummaryResponse
from atriumsports.datacore.openapi.models.league_external_ids_model import (
    LeagueExternalIdsModel as LeagueExternalIdsModel,
)
from atriumsports.datacore.openapi.models.league_external_ids_model_league import (
    LeagueExternalIdsModelLeague as LeagueExternalIdsModelLeague,
)
from atriumsports.datacore.openapi.models.league_external_ids_model_organization import (
    LeagueExternalIdsModelOrganization as LeagueExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.league_external_ids_post_body import (
    LeagueExternalIdsPostBody as LeagueExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.league_external_ids_put_body import (
    LeagueExternalIdsPutBody as LeagueExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.league_external_ids_response import (
    LeagueExternalIdsResponse as LeagueExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.league_post_body import LeaguePostBody as LeaguePostBody
from atriumsports.datacore.openapi.models.league_put_body import LeaguePutBody as LeaguePutBody
from atriumsports.datacore.openapi.models.leagues_model import LeaguesModel as LeaguesModel
from atriumsports.datacore.openapi.models.leagues_model_organization import (
    LeaguesModelOrganization as LeaguesModelOrganization,
)
from atriumsports.datacore.openapi.models.leagues_response import LeaguesResponse as LeaguesResponse
from atriumsports.datacore.openapi.models.organization_post_body import OrganizationPostBody as OrganizationPostBody
from atriumsports.datacore.openapi.models.organization_put_body import OrganizationPutBody as OrganizationPutBody
from atriumsports.datacore.openapi.models.organizations_model import OrganizationsModel as OrganizationsModel
from atriumsports.datacore.openapi.models.organizations_response import OrganizationsResponse as OrganizationsResponse
from atriumsports.datacore.openapi.models.person_additional_details import (
    PersonAdditionalDetails as PersonAdditionalDetails,
)
from atriumsports.datacore.openapi.models.person_external_ids_model import (
    PersonExternalIdsModel as PersonExternalIdsModel,
)
from atriumsports.datacore.openapi.models.person_external_ids_model_organization import (
    PersonExternalIdsModelOrganization as PersonExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.person_external_ids_post_body import (
    PersonExternalIdsPostBody as PersonExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.person_external_ids_put_body import (
    PersonExternalIdsPutBody as PersonExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.person_external_ids_response import (
    PersonExternalIdsResponse as PersonExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.person_historical_name import PersonHistoricalName as PersonHistoricalName
from atriumsports.datacore.openapi.models.person_post_body import PersonPostBody as PersonPostBody
from atriumsports.datacore.openapi.models.person_post_body_additional_names_value import (
    PersonPostBodyAdditionalNamesValue as PersonPostBodyAdditionalNamesValue,
)
from atriumsports.datacore.openapi.models.person_put_body import PersonPutBody as PersonPutBody
from atriumsports.datacore.openapi.models.persons_model import PersonsModel as PersonsModel
from atriumsports.datacore.openapi.models.persons_model_organization import (
    PersonsModelOrganization as PersonsModelOrganization,
)
from atriumsports.datacore.openapi.models.persons_response import PersonsResponse as PersonsResponse
from atriumsports.datacore.openapi.models.pool_post_body import PoolPostBody as PoolPostBody
from atriumsports.datacore.openapi.models.pool_put_body import PoolPutBody as PoolPutBody
from atriumsports.datacore.openapi.models.response_links import ResponseLinks as ResponseLinks
from atriumsports.datacore.openapi.models.response_meta_data import ResponseMetaData as ResponseMetaData
from atriumsports.datacore.openapi.models.role_post_body import RolePostBody as RolePostBody
from atriumsports.datacore.openapi.models.role_put_body import RolePutBody as RolePutBody
from atriumsports.datacore.openapi.models.roles_model import RolesModel as RolesModel
from atriumsports.datacore.openapi.models.roles_model_organization import (
    RolesModelOrganization as RolesModelOrganization,
)
from atriumsports.datacore.openapi.models.roles_response import RolesResponse as RolesResponse
from atriumsports.datacore.openapi.models.round_post_body import RoundPostBody as RoundPostBody
from atriumsports.datacore.openapi.models.round_put_body import RoundPutBody as RoundPutBody
from atriumsports.datacore.openapi.models.seasonentity_placings_post_body import (
    SEASONENTITYPlacingsPostBody as SEASONENTITYPlacingsPostBody,
)
from atriumsports.datacore.openapi.models.seasonentity_placings_put_body import (
    SEASONENTITYPlacingsPutBody as SEASONENTITYPlacingsPutBody,
)
from atriumsports.datacore.openapi.models.seasonperson_placings_post_body import (
    SEASONPERSONPlacingsPostBody as SEASONPERSONPlacingsPostBody,
)
from atriumsports.datacore.openapi.models.seasonperson_placings_put_body import (
    SEASONPERSONPlacingsPutBody as SEASONPERSONPlacingsPutBody,
)
from atriumsports.datacore.openapi.models.seasonroster_configuration import (
    SEASONROSTERConfiguration as SEASONROSTERConfiguration,
)
from atriumsports.datacore.openapi.models.season_entities_list_model import (
    SeasonEntitiesListModel as SeasonEntitiesListModel,
)
from atriumsports.datacore.openapi.models.season_entities_list_model_organization import (
    SeasonEntitiesListModelOrganization as SeasonEntitiesListModelOrganization,
)
from atriumsports.datacore.openapi.models.season_entities_list_response import (
    SeasonEntitiesListResponse as SeasonEntitiesListResponse,
)
from atriumsports.datacore.openapi.models.season_entities_model import SeasonEntitiesModel as SeasonEntitiesModel
from atriumsports.datacore.openapi.models.season_entities_post_body import (
    SeasonEntitiesPostBody as SeasonEntitiesPostBody,
)
from atriumsports.datacore.openapi.models.season_entities_response import (
    SeasonEntitiesResponse as SeasonEntitiesResponse,
)
from atriumsports.datacore.openapi.models.season_entity_base_statistics_model import (
    SeasonEntityBaseStatisticsModel as SeasonEntityBaseStatisticsModel,
)
from atriumsports.datacore.openapi.models.season_entity_base_statistics_model_organization import (
    SeasonEntityBaseStatisticsModelOrganization as SeasonEntityBaseStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_entity_base_statistics_post_body import (
    SeasonEntityBaseStatisticsPostBody as SeasonEntityBaseStatisticsPostBody,
)
from atriumsports.datacore.openapi.models.season_entity_base_statistics_response import (
    SeasonEntityBaseStatisticsResponse as SeasonEntityBaseStatisticsResponse,
)
from atriumsports.datacore.openapi.models.season_entity_placings_model import (
    SeasonEntityPlacingsModel as SeasonEntityPlacingsModel,
)
from atriumsports.datacore.openapi.models.season_entity_placings_model_organization import (
    SeasonEntityPlacingsModelOrganization as SeasonEntityPlacingsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_entity_placings_response import (
    SeasonEntityPlacingsResponse as SeasonEntityPlacingsResponse,
)
from atriumsports.datacore.openapi.models.season_entity_statistics_model import (
    SeasonEntityStatisticsModel as SeasonEntityStatisticsModel,
)
from atriumsports.datacore.openapi.models.season_entity_statistics_model_organization import (
    SeasonEntityStatisticsModelOrganization as SeasonEntityStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_entity_statistics_response import (
    SeasonEntityStatisticsResponse as SeasonEntityStatisticsResponse,
)
from atriumsports.datacore.openapi.models.season_external_ids_model import (
    SeasonExternalIdsModel as SeasonExternalIdsModel,
)
from atriumsports.datacore.openapi.models.season_external_ids_model_organization import (
    SeasonExternalIdsModelOrganization as SeasonExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_external_ids_post_body import (
    SeasonExternalIdsPostBody as SeasonExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.season_external_ids_put_body import (
    SeasonExternalIdsPutBody as SeasonExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.season_external_ids_response import (
    SeasonExternalIdsResponse as SeasonExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.season_fixture_stages_pools_list_model import (
    SeasonFixtureStagesPoolsListModel as SeasonFixtureStagesPoolsListModel,
)
from atriumsports.datacore.openapi.models.season_fixture_stages_pools_list_model_organization import (
    SeasonFixtureStagesPoolsListModelOrganization as SeasonFixtureStagesPoolsListModelOrganization,
)
from atriumsports.datacore.openapi.models.season_fixture_stages_pools_list_model_pool import (
    SeasonFixtureStagesPoolsListModelPool as SeasonFixtureStagesPoolsListModelPool,
)
from atriumsports.datacore.openapi.models.season_fixture_stages_pools_list_model_stage import (
    SeasonFixtureStagesPoolsListModelStage as SeasonFixtureStagesPoolsListModelStage,
)
from atriumsports.datacore.openapi.models.season_fixture_stages_pools_list_response import (
    SeasonFixtureStagesPoolsListResponse as SeasonFixtureStagesPoolsListResponse,
)
from atriumsports.datacore.openapi.models.season_person_base_statistics_model import (
    SeasonPersonBaseStatisticsModel as SeasonPersonBaseStatisticsModel,
)
from atriumsports.datacore.openapi.models.season_person_base_statistics_model_organization import (
    SeasonPersonBaseStatisticsModelOrganization as SeasonPersonBaseStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_person_base_statistics_post_body import (
    SeasonPersonBaseStatisticsPostBody as SeasonPersonBaseStatisticsPostBody,
)
from atriumsports.datacore.openapi.models.season_person_base_statistics_response import (
    SeasonPersonBaseStatisticsResponse as SeasonPersonBaseStatisticsResponse,
)
from atriumsports.datacore.openapi.models.season_person_placings_model import (
    SeasonPersonPlacingsModel as SeasonPersonPlacingsModel,
)
from atriumsports.datacore.openapi.models.season_person_placings_model_organization import (
    SeasonPersonPlacingsModelOrganization as SeasonPersonPlacingsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_person_placings_response import (
    SeasonPersonPlacingsResponse as SeasonPersonPlacingsResponse,
)
from atriumsports.datacore.openapi.models.season_person_statistics_model import (
    SeasonPersonStatisticsModel as SeasonPersonStatisticsModel,
)
from atriumsports.datacore.openapi.models.season_person_statistics_model_organization import (
    SeasonPersonStatisticsModelOrganization as SeasonPersonStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_person_statistics_periods_model import (
    SeasonPersonStatisticsPeriodsModel as SeasonPersonStatisticsPeriodsModel,
)
from atriumsports.datacore.openapi.models.season_person_statistics_periods_response import (
    SeasonPersonStatisticsPeriodsResponse as SeasonPersonStatisticsPeriodsResponse,
)
from atriumsports.datacore.openapi.models.season_person_statistics_response import (
    SeasonPersonStatisticsResponse as SeasonPersonStatisticsResponse,
)
from atriumsports.datacore.openapi.models.season_person_total_statistics_model import (
    SeasonPersonTotalStatisticsModel as SeasonPersonTotalStatisticsModel,
)
from atriumsports.datacore.openapi.models.season_person_total_statistics_model_organization import (
    SeasonPersonTotalStatisticsModelOrganization as SeasonPersonTotalStatisticsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_person_total_statistics_response import (
    SeasonPersonTotalStatisticsResponse as SeasonPersonTotalStatisticsResponse,
)
from atriumsports.datacore.openapi.models.season_persons_list_model import (
    SeasonPersonsListModel as SeasonPersonsListModel,
)
from atriumsports.datacore.openapi.models.season_persons_list_model_organization import (
    SeasonPersonsListModelOrganization as SeasonPersonsListModelOrganization,
)
from atriumsports.datacore.openapi.models.season_persons_list_response import (
    SeasonPersonsListResponse as SeasonPersonsListResponse,
)
from atriumsports.datacore.openapi.models.season_persons_model import SeasonPersonsModel as SeasonPersonsModel
from atriumsports.datacore.openapi.models.season_persons_post_body import SeasonPersonsPostBody as SeasonPersonsPostBody
from atriumsports.datacore.openapi.models.season_persons_response import SeasonPersonsResponse as SeasonPersonsResponse
from atriumsports.datacore.openapi.models.season_pools_model import SeasonPoolsModel as SeasonPoolsModel
from atriumsports.datacore.openapi.models.season_pools_model_organization import (
    SeasonPoolsModelOrganization as SeasonPoolsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_pools_response import SeasonPoolsResponse as SeasonPoolsResponse
from atriumsports.datacore.openapi.models.season_post_body import SeasonPostBody as SeasonPostBody
from atriumsports.datacore.openapi.models.season_post_body_promotion_relegation_rules_inner import (
    SeasonPostBodyPromotionRelegationRulesInner as SeasonPostBodyPromotionRelegationRulesInner,
)
from atriumsports.datacore.openapi.models.season_put_body import SeasonPutBody as SeasonPutBody
from atriumsports.datacore.openapi.models.season_roster_model import SeasonRosterModel as SeasonRosterModel
from atriumsports.datacore.openapi.models.season_roster_model_organization import (
    SeasonRosterModelOrganization as SeasonRosterModelOrganization,
)
from atriumsports.datacore.openapi.models.season_roster_post_body import SeasonRosterPostBody as SeasonRosterPostBody
from atriumsports.datacore.openapi.models.season_roster_response import SeasonRosterResponse as SeasonRosterResponse
from atriumsports.datacore.openapi.models.season_rounds_model import SeasonRoundsModel as SeasonRoundsModel
from atriumsports.datacore.openapi.models.season_rounds_model_organization import (
    SeasonRoundsModelOrganization as SeasonRoundsModelOrganization,
)
from atriumsports.datacore.openapi.models.season_rounds_response import SeasonRoundsResponse as SeasonRoundsResponse
from atriumsports.datacore.openapi.models.season_series_competitor import (
    SeasonSeriesCompetitor as SeasonSeriesCompetitor,
)
from atriumsports.datacore.openapi.models.season_series_model import SeasonSeriesModel as SeasonSeriesModel
from atriumsports.datacore.openapi.models.season_series_model_organization import (
    SeasonSeriesModelOrganization as SeasonSeriesModelOrganization,
)
from atriumsports.datacore.openapi.models.season_series_response import SeasonSeriesResponse as SeasonSeriesResponse
from atriumsports.datacore.openapi.models.season_stage_post_body import SeasonStagePostBody as SeasonStagePostBody
from atriumsports.datacore.openapi.models.season_stage_put_body import SeasonStagePutBody as SeasonStagePutBody
from atriumsports.datacore.openapi.models.season_stages_model import SeasonStagesModel as SeasonStagesModel
from atriumsports.datacore.openapi.models.season_stages_model_organization import (
    SeasonStagesModelOrganization as SeasonStagesModelOrganization,
)
from atriumsports.datacore.openapi.models.season_stages_response import SeasonStagesResponse as SeasonStagesResponse
from atriumsports.datacore.openapi.models.season_standings_stages_pools_list_model import (
    SeasonStandingsStagesPoolsListModel as SeasonStandingsStagesPoolsListModel,
)
from atriumsports.datacore.openapi.models.season_standings_stages_pools_list_model_organization import (
    SeasonStandingsStagesPoolsListModelOrganization as SeasonStandingsStagesPoolsListModelOrganization,
)
from atriumsports.datacore.openapi.models.season_standings_stages_pools_list_response import (
    SeasonStandingsStagesPoolsListResponse as SeasonStandingsStagesPoolsListResponse,
)
from atriumsports.datacore.openapi.models.season_venues_address import SeasonVenuesAddress as SeasonVenuesAddress
from atriumsports.datacore.openapi.models.season_venues_list_model import SeasonVenuesListModel as SeasonVenuesListModel
from atriumsports.datacore.openapi.models.season_venues_list_model_organization import (
    SeasonVenuesListModelOrganization as SeasonVenuesListModelOrganization,
)
from atriumsports.datacore.openapi.models.season_venues_list_model_site import (
    SeasonVenuesListModelSite as SeasonVenuesListModelSite,
)
from atriumsports.datacore.openapi.models.season_venues_list_response import (
    SeasonVenuesListResponse as SeasonVenuesListResponse,
)
from atriumsports.datacore.openapi.models.seasons_model import SeasonsModel as SeasonsModel
from atriumsports.datacore.openapi.models.seasons_model_competition import (
    SeasonsModelCompetition as SeasonsModelCompetition,
)
from atriumsports.datacore.openapi.models.seasons_model_fixture_profile import (
    SeasonsModelFixtureProfile as SeasonsModelFixtureProfile,
)
from atriumsports.datacore.openapi.models.seasons_model_leaders_criteria import (
    SeasonsModelLeadersCriteria as SeasonsModelLeadersCriteria,
)
from atriumsports.datacore.openapi.models.seasons_model_organization import (
    SeasonsModelOrganization as SeasonsModelOrganization,
)
from atriumsports.datacore.openapi.models.seasons_model_standing_configuration import (
    SeasonsModelStandingConfiguration as SeasonsModelStandingConfiguration,
)
from atriumsports.datacore.openapi.models.seasons_response import SeasonsResponse as SeasonsResponse
from atriumsports.datacore.openapi.models.series_post_body import SeriesPostBody as SeriesPostBody
from atriumsports.datacore.openapi.models.series_put_body import SeriesPutBody as SeriesPutBody
from atriumsports.datacore.openapi.models.site_address import SiteAddress as SiteAddress
from atriumsports.datacore.openapi.models.site_external_ids_model import SiteExternalIdsModel as SiteExternalIdsModel
from atriumsports.datacore.openapi.models.site_external_ids_model_organization import (
    SiteExternalIdsModelOrganization as SiteExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.site_external_ids_model_site import (
    SiteExternalIdsModelSite as SiteExternalIdsModelSite,
)
from atriumsports.datacore.openapi.models.site_external_ids_post_body import (
    SiteExternalIdsPostBody as SiteExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.site_external_ids_put_body import (
    SiteExternalIdsPutBody as SiteExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.site_external_ids_response import (
    SiteExternalIdsResponse as SiteExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.site_post_body import SitePostBody as SitePostBody
from atriumsports.datacore.openapi.models.site_put_body import SitePutBody as SitePutBody
from atriumsports.datacore.openapi.models.sites_model import SitesModel as SitesModel
from atriumsports.datacore.openapi.models.sites_model_organization import (
    SitesModelOrganization as SitesModelOrganization,
)
from atriumsports.datacore.openapi.models.sites_response import SitesResponse as SitesResponse
from atriumsports.datacore.openapi.models.social_media import SocialMedia as SocialMedia
from atriumsports.datacore.openapi.models.social_media1 import SocialMedia1 as SocialMedia1
from atriumsports.datacore.openapi.models.sorting import Sorting as Sorting
from atriumsports.datacore.openapi.models.standing_adjustment_post_body import (
    StandingAdjustmentPostBody as StandingAdjustmentPostBody,
)
from atriumsports.datacore.openapi.models.standing_adjustment_put_body import (
    StandingAdjustmentPutBody as StandingAdjustmentPutBody,
)
from atriumsports.datacore.openapi.models.standing_adjustments_model import (
    StandingAdjustmentsModel as StandingAdjustmentsModel,
)
from atriumsports.datacore.openapi.models.standing_adjustments_model_organization import (
    StandingAdjustmentsModelOrganization as StandingAdjustmentsModelOrganization,
)
from atriumsports.datacore.openapi.models.standing_adjustments_response import (
    StandingAdjustmentsResponse as StandingAdjustmentsResponse,
)
from atriumsports.datacore.openapi.models.standing_building import StandingBuilding as StandingBuilding
from atriumsports.datacore.openapi.models.standing_configuration import StandingConfiguration as StandingConfiguration
from atriumsports.datacore.openapi.models.standing_configurations_model import (
    StandingConfigurationsModel as StandingConfigurationsModel,
)
from atriumsports.datacore.openapi.models.standing_configurations_model_organization import (
    StandingConfigurationsModelOrganization as StandingConfigurationsModelOrganization,
)
from atriumsports.datacore.openapi.models.standing_configurations_post_body import (
    StandingConfigurationsPostBody as StandingConfigurationsPostBody,
)
from atriumsports.datacore.openapi.models.standing_configurations_put_body import (
    StandingConfigurationsPutBody as StandingConfigurationsPutBody,
)
from atriumsports.datacore.openapi.models.standing_configurations_response import (
    StandingConfigurationsResponse as StandingConfigurationsResponse,
)
from atriumsports.datacore.openapi.models.standing_post_body import StandingPostBody as StandingPostBody
from atriumsports.datacore.openapi.models.standing_post_body_calculated_value import (
    StandingPostBodyCalculatedValue as StandingPostBodyCalculatedValue,
)
from atriumsports.datacore.openapi.models.standing_post_body_points_value import (
    StandingPostBodyPointsValue as StandingPostBodyPointsValue,
)
from atriumsports.datacore.openapi.models.standing_progressions_model import (
    StandingProgressionsModel as StandingProgressionsModel,
)
from atriumsports.datacore.openapi.models.standing_progressions_model_organization import (
    StandingProgressionsModelOrganization as StandingProgressionsModelOrganization,
)
from atriumsports.datacore.openapi.models.standing_progressions_post_body import (
    StandingProgressionsPostBody as StandingProgressionsPostBody,
)
from atriumsports.datacore.openapi.models.standing_progressions_put_body import (
    StandingProgressionsPutBody as StandingProgressionsPutBody,
)
from atriumsports.datacore.openapi.models.standing_progressions_response import (
    StandingProgressionsResponse as StandingProgressionsResponse,
)
from atriumsports.datacore.openapi.models.standing_put_body import StandingPutBody as StandingPutBody
from atriumsports.datacore.openapi.models.standings_model import StandingsModel as StandingsModel
from atriumsports.datacore.openapi.models.standings_model_organization import (
    StandingsModelOrganization as StandingsModelOrganization,
)
from atriumsports.datacore.openapi.models.standings_response import StandingsResponse as StandingsResponse
from atriumsports.datacore.openapi.models.success_model import SuccessModel as SuccessModel
from atriumsports.datacore.openapi.models.success_response import SuccessResponse as SuccessResponse
from atriumsports.datacore.openapi.models.transfer_component import TransferComponent as TransferComponent
from atriumsports.datacore.openapi.models.transfer_post_body import TransferPostBody as TransferPostBody
from atriumsports.datacore.openapi.models.transfer_put_body import TransferPutBody as TransferPutBody
from atriumsports.datacore.openapi.models.transfers_model import TransfersModel as TransfersModel
from atriumsports.datacore.openapi.models.transfers_model_organization import (
    TransfersModelOrganization as TransfersModelOrganization,
)
from atriumsports.datacore.openapi.models.transfers_response import TransfersResponse as TransfersResponse
from atriumsports.datacore.openapi.models.uniform_items_model import UniformItemsModel as UniformItemsModel
from atriumsports.datacore.openapi.models.uniform_items_model_organization import (
    UniformItemsModelOrganization as UniformItemsModelOrganization,
)
from atriumsports.datacore.openapi.models.uniform_items_post_body import UniformItemsPostBody as UniformItemsPostBody
from atriumsports.datacore.openapi.models.uniform_items_post_body_colors import (
    UniformItemsPostBodyColors as UniformItemsPostBodyColors,
)
from atriumsports.datacore.openapi.models.uniform_items_put_body import UniformItemsPutBody as UniformItemsPutBody
from atriumsports.datacore.openapi.models.uniform_items_response import UniformItemsResponse as UniformItemsResponse
from atriumsports.datacore.openapi.models.uniforms_model import UniformsModel as UniformsModel
from atriumsports.datacore.openapi.models.uniforms_model_organization import (
    UniformsModelOrganization as UniformsModelOrganization,
)
from atriumsports.datacore.openapi.models.uniforms_post_body import UniformsPostBody as UniformsPostBody
from atriumsports.datacore.openapi.models.uniforms_put_body import UniformsPutBody as UniformsPutBody
from atriumsports.datacore.openapi.models.uniforms_response import UniformsResponse as UniformsResponse
from atriumsports.datacore.openapi.models.venue_address import VenueAddress as VenueAddress
from atriumsports.datacore.openapi.models.venue_external_ids_model import VenueExternalIdsModel as VenueExternalIdsModel
from atriumsports.datacore.openapi.models.venue_external_ids_model_organization import (
    VenueExternalIdsModelOrganization as VenueExternalIdsModelOrganization,
)
from atriumsports.datacore.openapi.models.venue_external_ids_post_body import (
    VenueExternalIdsPostBody as VenueExternalIdsPostBody,
)
from atriumsports.datacore.openapi.models.venue_external_ids_put_body import (
    VenueExternalIdsPutBody as VenueExternalIdsPutBody,
)
from atriumsports.datacore.openapi.models.venue_external_ids_response import (
    VenueExternalIdsResponse as VenueExternalIdsResponse,
)
from atriumsports.datacore.openapi.models.venue_historical_name import VenueHistoricalName as VenueHistoricalName
from atriumsports.datacore.openapi.models.venue_post_body import VenuePostBody as VenuePostBody
from atriumsports.datacore.openapi.models.venue_put_body import VenuePutBody as VenuePutBody
from atriumsports.datacore.openapi.models.venues_model import VenuesModel as VenuesModel
from atriumsports.datacore.openapi.models.venues_model_organization import (
    VenuesModelOrganization as VenuesModelOrganization,
)
from atriumsports.datacore.openapi.models.venues_model_site import VenuesModelSite as VenuesModelSite
from atriumsports.datacore.openapi.models.venues_response import VenuesResponse as VenuesResponse
from atriumsports.datacore.openapi.models.video_file_post_body import VideoFilePostBody as VideoFilePostBody
from atriumsports.datacore.openapi.models.video_files_download_model import (
    VideoFilesDownloadModel as VideoFilesDownloadModel,
)
from atriumsports.datacore.openapi.models.video_files_download_response import (
    VideoFilesDownloadResponse as VideoFilesDownloadResponse,
)
from atriumsports.datacore.openapi.models.video_files_model import VideoFilesModel as VideoFilesModel
from atriumsports.datacore.openapi.models.video_files_model_organization import (
    VideoFilesModelOrganization as VideoFilesModelOrganization,
)
from atriumsports.datacore.openapi.models.video_files_response import VideoFilesResponse as VideoFilesResponse
from atriumsports.datacore.openapi.models.video_stream_inputs_model import (
    VideoStreamInputsModel as VideoStreamInputsModel,
)
from atriumsports.datacore.openapi.models.video_stream_inputs_model_organization import (
    VideoStreamInputsModelOrganization as VideoStreamInputsModelOrganization,
)
from atriumsports.datacore.openapi.models.video_stream_inputs_response import (
    VideoStreamInputsResponse as VideoStreamInputsResponse,
)
from atriumsports.datacore.openapi.models.video_stream_local_model import VideoStreamLocalModel as VideoStreamLocalModel
from atriumsports.datacore.openapi.models.video_stream_local_model_organization import (
    VideoStreamLocalModelOrganization as VideoStreamLocalModelOrganization,
)
from atriumsports.datacore.openapi.models.video_stream_local_post_body import (
    VideoStreamLocalPostBody as VideoStreamLocalPostBody,
)
from atriumsports.datacore.openapi.models.video_stream_local_put_body import (
    VideoStreamLocalPutBody as VideoStreamLocalPutBody,
)
from atriumsports.datacore.openapi.models.video_stream_local_response import (
    VideoStreamLocalResponse as VideoStreamLocalResponse,
)
from atriumsports.datacore.openapi.models.video_stream_outputs_model import (
    VideoStreamOutputsModel as VideoStreamOutputsModel,
)
from atriumsports.datacore.openapi.models.video_stream_outputs_model_organization import (
    VideoStreamOutputsModelOrganization as VideoStreamOutputsModelOrganization,
)
from atriumsports.datacore.openapi.models.video_stream_outputs_response import (
    VideoStreamOutputsResponse as VideoStreamOutputsResponse,
)
from atriumsports.datacore.openapi.models.video_subscription_post_body import (
    VideoSubscriptionPostBody as VideoSubscriptionPostBody,
)
from atriumsports.datacore.openapi.models.video_subscription_put_body import (
    VideoSubscriptionPutBody as VideoSubscriptionPutBody,
)
from atriumsports.datacore.openapi.models.video_subscriptions_model import (
    VideoSubscriptionsModel as VideoSubscriptionsModel,
)
from atriumsports.datacore.openapi.models.video_subscriptions_model_organization import (
    VideoSubscriptionsModelOrganization as VideoSubscriptionsModelOrganization,
)
from atriumsports.datacore.openapi.models.video_subscriptions_response import (
    VideoSubscriptionsResponse as VideoSubscriptionsResponse,
)
