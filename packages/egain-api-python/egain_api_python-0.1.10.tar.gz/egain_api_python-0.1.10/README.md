# egain-api-python

Developer-friendly & type-safe Python SDK specifically catered to leverage *egain-api-python* API.

<div align="left">
    <a href="https://www.speakeasy.com/?utm_source=egain-api-python&utm_campaign=python"><img src="https://www.speakeasy.com/assets/badges/built-by-speakeasy.svg" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>

<!-- Start Summary [summary] -->
## Summary

Knowledge Portal Manager APIs: 
### License
  The following licenses are required to use the Knowledge Access APIs:
  * If the user is an agent, then the *Knowledge + AI* license is required.
  * If the user is a customer, the *Self-Service* and *Advanced Self-Service* licenses must be available.

### Tiers

| Tier	|Tier Name|	Named Users |	Description
| ---------- | ---------- | ---------- | ----------------------------
| Tier 1 |  Starter |	Up to 10|	Designed for small-scale implementations or pilot environments
| Tier 2 |	Growth	| Up to 1000|	Suitable for mid-scale deployments requiring moderate scalability
| Tier 3 |	Enterprise	| Greater than 1000|	Supports large-scale environments with extended configuration options

### API Resource Limits
The following Resources have predefined limits for specific access attributes for Starter, Growth and Enterprise use.

| Resource | Limits | Starter | Growth | Enterprise
| ---------------- | ---------------------------- | ---------- | ---------- | ----------
| Article Reference |Number of attachments used in any article | 25 | 50 |50
|  |Number of custom attributes in an article | 10 | 25| 50 
|  |Number of publish views used in an article version | 20 | 20 | 20
| Topic Reference |User-defined topics in a department| 1000| 5000 | 50000
|  |Depth of topics  | 5 | 20 | 20
|  |Topics at any level | 500 | 2500 | 2500
|  |Number of custom attributes in a topic | 10 | 10 | 10
| Portal Reference | Tag categories in a portal | 15 | 15 | 15
|  |Topics to be included in a portal | 100 | 500 | 5000 
|  |Number of articles to display in announcements | 10 | 25 | 25
|  |Usage links and link groups setup for a portal | 5 | 10 | 25
    
      


For more information about the API: [Full SDK Documentation](https://github.com/eGain/egain-api-python)
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [egain-api-python](#egain-api-python)
  * [SDK Installation](#sdk-installation)
  * [IDE Support](#ide-support)
  * [SDK Example Usage](#sdk-example-usage)
  * [Authentication](#authentication)
  * [Available Resources and Operations](#available-resources-and-operations)
  * [File uploads](#file-uploads)
  * [Retries](#retries)
  * [Error Handling](#error-handling)
  * [Server Selection](#server-selection)
  * [Custom HTTP Client](#custom-http-client)
  * [Resource Management](#resource-management)
  * [Debugging](#debugging)
* [Development](#development)
  * [Maturity](#maturity)
  * [Contributions](#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with *uv*, *pip*, or *poetry* package managers.

### uv

*uv* is a fast Python package installer and resolver, designed as a drop-in replacement for pip and pip-tools. It's recommended for its speed and modern Python tooling capabilities.

```bash
uv add egain-api-python
```

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install egain-api-python
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add egain-api-python
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from egain-api-python python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "egain-api-python",
# ]
# ///

from egain_api_python import Egain

sdk = Egain(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
# Synchronous Example
from egain_api_python import Egain
import os


with Egain(
    access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
) as egain:

    res = egain.aiservices.retrieve.retrieve_chunks(q="fair lending", portal_id="PROD-1000", language="en-US", filter_user_profile_id="PROD-3210", filter_tags={
        "PROD-1234": [
            "PROD-2000",
            "PROD-2003",
        ],
        "PROD-2005": [
            "PROD-2007",
        ],
    }, channel={
        "name": "Eight Bank Website",
    })

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.

```python
# Asynchronous Example
import asyncio
from egain_api_python import Egain
import os

async def main():

    async with Egain(
        access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
    ) as egain:

        res = await egain.aiservices.retrieve.retrieve_chunks_async(q="fair lending", portal_id="PROD-1000", language="en-US", filter_user_profile_id="PROD-3210", filter_tags={
            "PROD-1234": [
                "PROD-2000",
                "PROD-2003",
            ],
            "PROD-2005": [
                "PROD-2007",
            ],
        }, channel={
            "name": "Eight Bank Website",
        })

        # Handle response
        print(res)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name           | Type | Scheme      | Environment Variable |
| -------------- | ---- | ----------- | -------------------- |
| `access_token` | http | HTTP Bearer | `EGAIN_ACCESS_TOKEN` |

To authenticate with the API the `access_token` parameter must be set when initializing the SDK client instance. For example:
```python
from egain_api_python import Egain
import os


with Egain(
    access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
) as egain:

    res = egain.aiservices.retrieve.retrieve_chunks(q="fair lending", portal_id="PROD-1000", language="en-US", filter_user_profile_id="PROD-3210", filter_tags={
        "PROD-1234": [
            "PROD-2000",
            "PROD-2003",
        ],
        "PROD-2005": [
            "PROD-2007",
        ],
    }, channel={
        "name": "Eight Bank Website",
    })

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

#### [aiservices.answers](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/answers/README.md)

* [get_best_answer](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/answers/README.md#get_best_answer) - Get the best answer for a user query

#### [aiservices.retrieve](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/retrieve/README.md)

* [retrieve_chunks](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/retrieve/README.md#retrieve_chunks) - Retrieve Chunks

#### [content.import_](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/import/README.md)

* [create_import_job](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/import/README.md#create_import_job) - Import content from external sources by creating an import job
* [get_import_status](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/import/README.md#get_import_status) - Get the current status of an import or validation job
* [create_import_validation_job](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/import/README.md#create_import_validation_job) - Validate content structure and format before import by creating an import validation job
* [cancel_import](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/import/README.md#cancel_import) - Cancel an import or validation job

#### [portal.article](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md)

* [get_article_by_id](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_article_by_id) - Get Article by ID
* [get_article_by_id_with_editions](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_article_by_id_with_editions) - Get Article By ID with Editions
* [get_article_edition_details](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_article_edition_details) - Get Article Edition Details
* [add_to_reply](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#add_to_reply) - Add Article to Reply
* [add_as_reference](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#add_as_reference) - Add as Reference
* [get_articles_in_topic](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_articles_in_topic) - Get Articles in Topic
* [get_article_attachment_by_id](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_article_attachment_by_id) - Get Article Attachment By ID
* [get_attachment_by_id_in_portal](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_attachment_by_id_in_portal) - Get Article Attachment in Portal
* [get_related_articles](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_related_articles) - Get Related Articles
* [get_announcement_articles](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_announcement_articles) - Get Announcement Articles
* [get_article_ratings](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_article_ratings) - Get Article Ratings
* [rate_article](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#rate_article) - Rate an Article
* [get_pending_compliance_articles](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_pending_compliance_articles) - Get Pending Article Compliances
* [get_acknowledged_compliance_articles](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_acknowledged_compliance_articles) - Get Acknowledged Article Compliances
* [comply_article](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#comply_article) - Comply With an Article
* [get_my_subscription](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_my_subscription) - My Subscription
* [subscribe_article](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#subscribe_article) - Subscribe to an Article
* [unsubscribe_article](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#unsubscribe_article) - Unsubscribe to an Article
* [get_article_permissions_by_id](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_article_permissions_by_id) - Get Article Permissions By ID
* [get_article_personalization](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalarticle/README.md#get_article_personalization) - Get Article Personalization Details

#### [portal.articlelists](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/articlelists/README.md)

* [get_all_article_lists](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/articlelists/README.md#get_all_article_lists) - Get All Article Lists
* [get_article_list_details](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/articlelists/README.md#get_article_list_details) - Get Article List by ID

#### [portal.attachment](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalattachment/README.md)

* [create_signed_url](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalattachment/README.md#create_signed_url) - Generate Signed URL to Upload API
* [upload_attachment](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalattachment/README.md#upload_attachment) - Upload Attachment

#### [portal.bookmark](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalbookmark/README.md)

* [addbookmark](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalbookmark/README.md#addbookmark) - Add a Bookmark
* [getbookmark](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalbookmark/README.md#getbookmark) - Get All Bookmarks for a Portal
* [deletebookmark](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalbookmark/README.md#deletebookmark) - Delete a Bookmark

#### [portal.connectorssearchevents](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/connectorssearchevents/README.md)

* [create_search_result_event_for_connectors](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/connectorssearchevents/README.md#create_search_result_event_for_connectors) - Event for Search Using Connectors
* [create_viewed_search_results_event_for_connectors](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/connectorssearchevents/README.md#create_viewed_search_results_event_for_connectors) - Event for Viewed Search Results Using Connectors

#### [portal.escalation](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/escalation/README.md)

* [start_customer_escalation](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/escalation/README.md#start_customer_escalation) - Start Customer Escalation
* [search_prior_to_escalation](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/escalation/README.md#search_prior_to_escalation) - Search Prior To Customer Escalation
* [complete_customer_escalation](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/escalation/README.md#complete_customer_escalation) - Complete Customer Escalation
* [avert_customer_escalation](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/escalation/README.md#avert_customer_escalation) - Avert Customer Escalation

#### [portal.export](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/export/README.md)

* [export_content](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/export/README.md#export_content) - Export Knowledge
* [export_status](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/export/README.md#export_status) - Get Export Job Status

#### [portal.federatedsearchevent](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/federatedsearchevent/README.md)

* [create_federated_search_result_event](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/federatedsearchevent/README.md#create_federated_search_result_event) - Event For Viewed Federated Search Result

#### [portal.general](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/general/README.md)

* [get_all_portals](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/general/README.md#get_all_portals) - Get All Portals
* [get_my_portals](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/general/README.md#get_my_portals) - Get All Portals Accessible To User
* [get_portal_details_by_id](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/general/README.md#get_portal_details_by_id) - Get Portal Details By ID
* [get_tag_categories_for_interest_for_portal](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/general/README.md#get_tag_categories_for_interest_for_portal) - Get Tag Categories for Interest for a Portal

#### [portal.guidedhelp](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md)

* [get_all_casebases_releases](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#get_all_casebases_releases) - Get Available Casebases Releases
* [get_casebase_release_by_id](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#get_casebase_release_by_id) - Get Details of a Casebase Release
* [get_cluster_by_casebase_release_id](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#get_cluster_by_casebase_release_id) - Get Cluster Details of a Casebase Release
* [get_all_profiles_in_portal](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#get_all_profiles_in_portal) - Get All Profiles Available in Portal
* [start_gh_search](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#start_gh_search) - Start a Guided Help Search
* [step_gh_search](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#step_gh_search) - Perform a Step in a Guided Help Search
* [get_all_cases](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#get_all_cases) - Get All Cases of a Cluster in Release
* [get_case_by_id](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#get_case_by_id) - Get Details of a Case
* [accept_gh_solution](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#accept_gh_solution) - Accept Solution
* [reject_gh_solution](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#reject_gh_solution) - Reject Solution
* [create_quickpick](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#create_quickpick) - Create Quickpick
* [get_all_quick_picks](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#get_all_quick_picks) - Get All Quickpicks for a Portal
* [restore_quickpick](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/guidedhelp/README.md#restore_quickpick) - Resume a Quickpick

#### [portal.populararticles](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/populararticles/README.md)

* [getpopulararticles](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/populararticles/README.md#getpopulararticles) - Get Popular Articles

#### [portal.search](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/search/README.md)

* [ai_search](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/search/README.md#ai_search) - Get the best search results for a user query

#### [portal.suggestion](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md)

* [make_suggestion](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#make_suggestion) - Make a Suggestion
* [modify_suggestions](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#modify_suggestions) - Modify Suggestion
* [search_suggestion](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#search_suggestion) - Get Suggestion by Status
* [get_suggestion](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#get_suggestion) - Get Suggestion by ID
* [delete_suggestion](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#delete_suggestion) - Delete a Suggestion
* [get_related_articles_for_suggestion](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#get_related_articles_for_suggestion) - Get Related Articles for Suggestion
* [get_suggestion_comments](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#get_suggestion_comments) - Get Suggestion Comments
* [get_suggestion_attachments](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#get_suggestion_attachments) - Get Suggestion Attachments
* [get_suggestion_attachment_by_id](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portalsuggestion/README.md#get_suggestion_attachment_by_id) - Get Suggestion Attachment by ID

#### [portal.topic](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaltopic/README.md)

* [get_topic_breadcrumb_for_article](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaltopic/README.md#get_topic_breadcrumb_for_article) - Get Topic Breadcrumb for Article
* [getchildtopics](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaltopic/README.md#getchildtopics) - Get Immediate Child Topics
* [getancestortopics](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaltopic/README.md#getancestortopics) - Get All Ancestor Topics
* [getalltopics](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaltopic/README.md#getalltopics) - Get All Topics

#### [portal.userdetails](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaluserdetails/README.md)

* [get_user_details](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaluserdetails/README.md#get_user_details) - Get User Details

#### [portal.usermilestones](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/usermilestones/README.md)

* [get_user_milestones](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/usermilestones/README.md#get_user_milestones) - Get User Milestones

#### [portal.userprofile](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaluserprofile/README.md)

* [get_all_user_profiles](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaluserprofile/README.md#get_all_user_profiles) - Get All User Profiles Assigned to User
* [select_user_profile](https://github.com/eGain/egain-api-typescript/blob/main/docs/sdks/portaluserprofile/README.md#select_user_profile) - Select User Profile

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start File uploads [file-upload] -->
## File uploads

Certain SDK methods accept file objects as part of a request body or multi-part request. It is possible and typically recommended to upload files as a stream rather than reading the entire contents into memory. This avoids excessive memory consumption and potentially crashing with out-of-memory errors when working with very large files. The following example demonstrates how to attach a file stream to a request.

> [!TIP]
>
> For endpoints that handle file uploads bytes arrays can also be used. However, using streams is recommended for large files.
>

```python
from egain_api_python import Egain
import os


with Egain(
    access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
) as egain:

    egain.portal.attachment.upload_attachment(accept_language="en-US", signature="<value>", request_body=open("example.file", "rb"))

    # Use the SDK ...

```
<!-- End File uploads [file-upload] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from egain_api_python import Egain
from egain_api_python.utils import BackoffStrategy, RetryConfig
import os


with Egain(
    access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
) as egain:

    res = egain.aiservices.retrieve.retrieve_chunks(q="fair lending", portal_id="PROD-1000", language="en-US", filter_user_profile_id="PROD-3210", filter_tags={
        "PROD-1234": [
            "PROD-2000",
            "PROD-2003",
        ],
        "PROD-2005": [
            "PROD-2007",
        ],
    }, channel={
        "name": "Eight Bank Website",
    },
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from egain_api_python import Egain
from egain_api_python.utils import BackoffStrategy, RetryConfig
import os


with Egain(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
) as egain:

    res = egain.aiservices.retrieve.retrieve_chunks(q="fair lending", portal_id="PROD-1000", language="en-US", filter_user_profile_id="PROD-3210", filter_tags={
        "PROD-1234": [
            "PROD-2000",
            "PROD-2003",
        ],
        "PROD-2005": [
            "PROD-2007",
        ],
    }, channel={
        "name": "Eight Bank Website",
    })

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`EgainError`](./src/egain_api_python/errors/egainerror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](#error-classes). |

### Example
```python
from egain_api_python import Egain, errors
from egain_api_python.utils import parse_datetime
import os


with Egain(
    access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
) as egain:
    res = None
    try:

        res = egain.content.import_.create_import_job(data_source={
            "type": "AWS S3 bucket",
            "path": "s3://mybucket/myfolder/",
            "region": "us-east-1",
            "credentials": {},
        }, operation="import", schedule_time={
            "date_": parse_datetime("2024-03-01T10:00:00.000Z"),
        })

        # Handle response
        print(res)


    except errors.EgainError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, errors.WSErrorCommon):
            print(e.data.code)  # str
            print(e.data.developer_message)  # str
            print(e.data.details)  # Optional[List[models.WSErrorCommonDetail]]
            print(e.data.user_message)  # Optional[str]
```

### Error Classes
**Primary errors:**
* [`EgainError`](./src/egain_api_python/errors/egainerror.py): The base class for HTTP error responses.
  * [`WSErrorCommon`](./src/egain_api_python/errors/wserrorcommon.py): Bad Request. *

<details><summary>Less common errors (6)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`EgainError`](./src/egain_api_python/errors/egainerror.py)**:
* [`SchemasWSErrorCommon`](./src/egain_api_python/errors/schemaswserrorcommon.py): Preconditions failed. Status code `412`. Applicable to 2 of 78 methods.*
* [`ResponseValidationError`](./src/egain_api_python/errors/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>

\* Check [the method documentation](#available-resources-and-operations) to see if the error is applicable.
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from egain_api_python import Egain
import os


with Egain(
    server_url="https://api.aidev.egain.cloud/knowledge/portalmgr/v4",
    access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
) as egain:

    res = egain.aiservices.retrieve.retrieve_chunks(q="fair lending", portal_id="PROD-1000", language="en-US", filter_user_profile_id="PROD-3210", filter_tags={
        "PROD-1234": [
            "PROD-2000",
            "PROD-2003",
        ],
        "PROD-2005": [
            "PROD-2007",
        ],
    }, channel={
        "name": "Eight Bank Website",
    })

    # Handle response
    print(res)

```

### Override Server URL Per-Operation

The server URL can also be overridden on a per-operation basis, provided a server list was specified for the operation. For example:
```python
from egain_api_python import Egain
import os


with Egain(
    access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
) as egain:

    res = egain.aiservices.retrieve.retrieve_chunks(q="fair lending", portal_id="PROD-1000", language="en-US", filter_user_profile_id="PROD-3210", filter_tags={
        "PROD-1234": [
            "PROD-2000",
            "PROD-2003",
        ],
        "PROD-2005": [
            "PROD-2007",
        ],
    }, channel={
        "name": "Eight Bank Website",
    }, server_url="https://api.aidev.egain.cloud/core/aiservices/v4")

    # Handle response
    print(res)

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from egain_api_python import Egain
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = Egain(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from egain_api_python import Egain
from egain_api_python.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = Egain(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `Egain` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from egain_api_python import Egain
import os
def main():

    with Egain(
        access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
    ) as egain:
        # Rest of application here...


# Or when using async:
async def amain():

    async with Egain(
        access_token=os.getenv("EGAIN_ACCESS_TOKEN", ""),
    ) as egain:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from egain_api_python import Egain
import logging

logging.basicConfig(level=logging.DEBUG)
s = Egain(debug_logger=logging.getLogger("egain_api_python"))
```

You can also enable a default debug logger by setting an environment variable `EGAIN_DEBUG` to true.
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation. 
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release. 

### SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=egain-api-python&utm_campaign=python)
