<a id="types-aiobotocore-quicksight"></a>

# types-aiobotocore-quicksight

[![PyPI - types-aiobotocore-quicksight](https://img.shields.io/pypi/v/types-aiobotocore-quicksight.svg?color=blue)](https://pypi.org/project/types-aiobotocore-quicksight/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-aiobotocore-quicksight.svg?color=blue)](https://pypi.org/project/types-aiobotocore-quicksight/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/types_aiobotocore_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/types-aiobotocore-quicksight)](https://pypistats.org/packages/types-aiobotocore-quicksight)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for
[aiobotocore QuickSight 2.25.0](https://pypi.org/project/aiobotocore/)
compatible with [VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found on
[types-aiobotocore](https://pypi.org/project/types-aiobotocore/) page and in
[types-aiobotocore-quicksight docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_quicksight/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [types-aiobotocore-quicksight](#types-aiobotocore-quicksight)
  - [How to install](#how-to-install)
    - [Generate locally (recommended)](<#generate-locally-(recommended)>)
    - [From PyPI with pip](#from-pypi-with-pip)
  - [How to uninstall](#how-to-uninstall)
  - [Usage](#usage)
    - [VSCode](#vscode)
    - [PyCharm](#pycharm)
    - [Emacs](#emacs)
    - [Sublime Text](#sublime-text)
    - [Other IDEs](#other-ides)
    - [mypy](#mypy)
    - [pyright](#pyright)
    - [Pylint compatibility](#pylint-compatibility)
  - [Explicit type annotations](#explicit-type-annotations)
    - [Client annotations](#client-annotations)
    - [Paginators annotations](#paginators-annotations)
    - [Literals](#literals)
    - [Type definitions](#type-definitions)
  - [How it works](#how-it-works)
  - [What's new](#what's-new)
    - [Implemented features](#implemented-features)
    - [Latest changes](#latest-changes)
  - [Versioning](#versioning)
  - [Thank you](#thank-you)
  - [Documentation](#documentation)
  - [Support and contributing](#support-and-contributing)

<a id="how-to-install"></a>

## How to install

<a id="generate-locally-(recommended)"></a>

### Generate locally (recommended)

You can generate type annotations for `aiobotocore` package locally with
`mypy-boto3-builder`. Use
[uv](https://docs.astral.sh/uv/getting-started/installation/) for build
isolation.

1. Run mypy-boto3-builder in your package root directory:
   `uvx --with 'aiobotocore==2.25.0' mypy-boto3-builder`
2. Select `aiobotocore` AWS SDK.
3. Add `QuickSight` service.
4. Use provided commands to install generated packages.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `types-aiobotocore` for `QuickSight` service.

```bash
# install with aiobotocore type annotations
python -m pip install 'types-aiobotocore[quicksight]'

# Lite version does not provide session.client/resource overloads
# it is more RAM-friendly, but requires explicit type annotations
python -m pip install 'types-aiobotocore-lite[quicksight]'

# standalone installation
python -m pip install types-aiobotocore-quicksight
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
python -m pip uninstall -y types-aiobotocore-quicksight
```

<a id="usage"></a>

## Usage

<a id="vscode"></a>

### VSCode

- Install
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- Install
  [Pylance extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- Set `Pylance` as your Python Language Server
- Install `types-aiobotocore[quicksight]` in your environment:

```bash
python -m pip install 'types-aiobotocore[quicksight]'
```

Both type checking and code completion should now work. No explicit type
annotations required, write your `aiobotocore` code as usual.

<a id="pycharm"></a>

### PyCharm

> ⚠️ Due to slow PyCharm performance on `Literal` overloads (issue
> [PY-40997](https://youtrack.jetbrains.com/issue/PY-40997)), it is recommended
> to use
> [types-aiobotocore-lite](https://pypi.org/project/types-aiobotocore-lite/)
> until the issue is resolved.

> ⚠️ If you experience slow performance and high CPU usage, try to disable
> `PyCharm` type checker and use [mypy](https://github.com/python/mypy) or
> [pyright](https://github.com/microsoft/pyright) instead.

> ⚠️ To continue using `PyCharm` type checker, you can try to replace
> `types-aiobotocore` with
> [types-aiobotocore-lite](https://pypi.org/project/types-aiobotocore-lite/):

```bash
pip uninstall types-aiobotocore
pip install types-aiobotocore-lite
```

Install `types-aiobotocore[quicksight]` in your environment:

```bash
python -m pip install 'types-aiobotocore[quicksight]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `types-aiobotocore` with services you use in your environment:

```bash
python -m pip install 'types-aiobotocore[quicksight]'
```

- Install [use-package](https://github.com/jwiegley/use-package),
  [lsp](https://github.com/emacs-lsp/lsp-mode/),
  [company](https://github.com/company-mode/company-mode) and
  [flycheck](https://github.com/flycheck/flycheck) packages
- Install [lsp-pyright](https://github.com/emacs-lsp/lsp-pyright) package

```elisp
(use-package lsp-pyright
  :ensure t
  :hook (python-mode . (lambda ()
                          (require 'lsp-pyright)
                          (lsp)))  ; or lsp-deferred
  :init (when (executable-find "python3")
          (setq lsp-pyright-python-executable-cmd "python3"))
  )
```

- Make sure emacs uses the environment where you have installed
  `types-aiobotocore`

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="sublime-text"></a>

### Sublime Text

- Install `types-aiobotocore[quicksight]` with services you use in your
  environment:

```bash
python -m pip install 'types-aiobotocore[quicksight]'
```

- Install [LSP-pyright](https://github.com/sublimelsp/LSP-pyright) package

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="other-ides"></a>

### Other IDEs

Not tested, but as long as your IDE supports `mypy` or `pyright`, everything
should work.

<a id="mypy"></a>

### mypy

- Install `mypy`: `python -m pip install mypy`
- Install `types-aiobotocore[quicksight]` in your environment:

```bash
python -m pip install 'types-aiobotocore[quicksight]'
```

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `types-aiobotocore[quicksight]` in your environment:

```bash
python -m pip install 'types-aiobotocore[quicksight]'
```

Optionally, you can install `types-aiobotocore` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid
`types-aiobotocore-quicksight` dependency in production. However, there is an
issue in `pylint` that it complains about undefined variables. To fix it, set
all types to `object` in non-`TYPE_CHECKING` mode.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types_aiobotocore_ec2 import EC2Client, EC2ServiceResource
    from types_aiobotocore_ec2.waiters import BundleTaskCompleteWaiter
    from types_aiobotocore_ec2.paginators import DescribeVolumesPaginator
else:
    EC2Client = object
    EC2ServiceResource = object
    BundleTaskCompleteWaiter = object
    DescribeVolumesPaginator = object

...
```

<a id="explicit-type-annotations"></a>

## Explicit type annotations

<a id="client-annotations"></a>

### Client annotations

`QuickSightClient` provides annotations for
`session.create_client("quicksight")`.

```python
from aiobotocore.session import get_session

from types_aiobotocore_quicksight import QuickSightClient

session = get_session()
async with session.create_client("quicksight") as client:
    client: QuickSightClient
    # now client usage is checked by mypy and IDE should provide code completion
```

<a id="paginators-annotations"></a>

### Paginators annotations

`types_aiobotocore_quicksight.paginator` module contains type annotations for
all paginators.

```python
from aiobotocore.session import get_session

from types_aiobotocore_quicksight import QuickSightClient
from types_aiobotocore_quicksight.paginator import (
    DescribeFolderPermissionsPaginator,
    DescribeFolderResolvedPermissionsPaginator,
    ListActionConnectorsPaginator,
    ListAnalysesPaginator,
    ListAssetBundleExportJobsPaginator,
    ListAssetBundleImportJobsPaginator,
    ListBrandsPaginator,
    ListCustomPermissionsPaginator,
    ListDashboardVersionsPaginator,
    ListDashboardsPaginator,
    ListDataSetsPaginator,
    ListDataSourcesPaginator,
    ListFlowsPaginator,
    ListFolderMembersPaginator,
    ListFoldersForResourcePaginator,
    ListFoldersPaginator,
    ListGroupMembershipsPaginator,
    ListGroupsPaginator,
    ListIAMPolicyAssignmentsForUserPaginator,
    ListIAMPolicyAssignmentsPaginator,
    ListIngestionsPaginator,
    ListNamespacesPaginator,
    ListRoleMembershipsPaginator,
    ListTemplateAliasesPaginator,
    ListTemplateVersionsPaginator,
    ListTemplatesPaginator,
    ListThemeVersionsPaginator,
    ListThemesPaginator,
    ListUserGroupsPaginator,
    ListUsersPaginator,
    SearchActionConnectorsPaginator,
    SearchAnalysesPaginator,
    SearchDashboardsPaginator,
    SearchDataSetsPaginator,
    SearchDataSourcesPaginator,
    SearchFlowsPaginator,
    SearchFoldersPaginator,
    SearchGroupsPaginator,
    SearchTopicsPaginator,
)

session = get_session()
async with session.create_client("quicksight") as client:
    client: QuickSightClient

    # Explicit type annotations are optional here
    # Types should be correctly discovered by mypy and IDEs
    describe_folder_permissions_paginator: DescribeFolderPermissionsPaginator = (
        client.get_paginator("describe_folder_permissions")
    )
    describe_folder_resolved_permissions_paginator: DescribeFolderResolvedPermissionsPaginator = (
        client.get_paginator("describe_folder_resolved_permissions")
    )
    list_action_connectors_paginator: ListActionConnectorsPaginator = client.get_paginator(
        "list_action_connectors"
    )
    list_analyses_paginator: ListAnalysesPaginator = client.get_paginator("list_analyses")
    list_asset_bundle_export_jobs_paginator: ListAssetBundleExportJobsPaginator = (
        client.get_paginator("list_asset_bundle_export_jobs")
    )
    list_asset_bundle_import_jobs_paginator: ListAssetBundleImportJobsPaginator = (
        client.get_paginator("list_asset_bundle_import_jobs")
    )
    list_brands_paginator: ListBrandsPaginator = client.get_paginator("list_brands")
    list_custom_permissions_paginator: ListCustomPermissionsPaginator = client.get_paginator(
        "list_custom_permissions"
    )
    list_dashboard_versions_paginator: ListDashboardVersionsPaginator = client.get_paginator(
        "list_dashboard_versions"
    )
    list_dashboards_paginator: ListDashboardsPaginator = client.get_paginator("list_dashboards")
    list_data_sets_paginator: ListDataSetsPaginator = client.get_paginator("list_data_sets")
    list_data_sources_paginator: ListDataSourcesPaginator = client.get_paginator(
        "list_data_sources"
    )
    list_flows_paginator: ListFlowsPaginator = client.get_paginator("list_flows")
    list_folder_members_paginator: ListFolderMembersPaginator = client.get_paginator(
        "list_folder_members"
    )
    list_folders_for_resource_paginator: ListFoldersForResourcePaginator = client.get_paginator(
        "list_folders_for_resource"
    )
    list_folders_paginator: ListFoldersPaginator = client.get_paginator("list_folders")
    list_group_memberships_paginator: ListGroupMembershipsPaginator = client.get_paginator(
        "list_group_memberships"
    )
    list_groups_paginator: ListGroupsPaginator = client.get_paginator("list_groups")
    list_iam_policy_assignments_for_user_paginator: ListIAMPolicyAssignmentsForUserPaginator = (
        client.get_paginator("list_iam_policy_assignments_for_user")
    )
    list_iam_policy_assignments_paginator: ListIAMPolicyAssignmentsPaginator = client.get_paginator(
        "list_iam_policy_assignments"
    )
    list_ingestions_paginator: ListIngestionsPaginator = client.get_paginator("list_ingestions")
    list_namespaces_paginator: ListNamespacesPaginator = client.get_paginator("list_namespaces")
    list_role_memberships_paginator: ListRoleMembershipsPaginator = client.get_paginator(
        "list_role_memberships"
    )
    list_template_aliases_paginator: ListTemplateAliasesPaginator = client.get_paginator(
        "list_template_aliases"
    )
    list_template_versions_paginator: ListTemplateVersionsPaginator = client.get_paginator(
        "list_template_versions"
    )
    list_templates_paginator: ListTemplatesPaginator = client.get_paginator("list_templates")
    list_theme_versions_paginator: ListThemeVersionsPaginator = client.get_paginator(
        "list_theme_versions"
    )
    list_themes_paginator: ListThemesPaginator = client.get_paginator("list_themes")
    list_user_groups_paginator: ListUserGroupsPaginator = client.get_paginator("list_user_groups")
    list_users_paginator: ListUsersPaginator = client.get_paginator("list_users")
    search_action_connectors_paginator: SearchActionConnectorsPaginator = client.get_paginator(
        "search_action_connectors"
    )
    search_analyses_paginator: SearchAnalysesPaginator = client.get_paginator("search_analyses")
    search_dashboards_paginator: SearchDashboardsPaginator = client.get_paginator(
        "search_dashboards"
    )
    search_data_sets_paginator: SearchDataSetsPaginator = client.get_paginator("search_data_sets")
    search_data_sources_paginator: SearchDataSourcesPaginator = client.get_paginator(
        "search_data_sources"
    )
    search_flows_paginator: SearchFlowsPaginator = client.get_paginator("search_flows")
    search_folders_paginator: SearchFoldersPaginator = client.get_paginator("search_folders")
    search_groups_paginator: SearchGroupsPaginator = client.get_paginator("search_groups")
    search_topics_paginator: SearchTopicsPaginator = client.get_paginator("search_topics")
```

<a id="literals"></a>

### Literals

`types_aiobotocore_quicksight.literals` module contains literals extracted from
shapes that can be used in user code for type checking.

Full list of `QuickSight` Literals can be found in
[docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_quicksight/literals/).

```python
from types_aiobotocore_quicksight.literals import ActionConnectorErrorTypeType


def check_value(value: ActionConnectorErrorTypeType) -> bool: ...
```

<a id="type-definitions"></a>

### Type definitions

`types_aiobotocore_quicksight.type_defs` module contains structures and shapes
assembled to typed dictionaries and unions for additional type checking.

Full list of `QuickSight` TypeDefs can be found in
[docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_quicksight/type_defs/).

```python
# TypedDict usage example
from types_aiobotocore_quicksight.type_defs import APIKeyConnectionMetadataTypeDef


def get_value() -> APIKeyConnectionMetadataTypeDef:
    return {
        "BaseEndpoint": ...,
    }
```

<a id="how-it-works"></a>

## How it works

Fully automated
[mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder) carefully
generates type annotations for each service, patiently waiting for
`aiobotocore` updates. It delivers drop-in type annotations for you and makes
sure that:

- All available `aiobotocore` services are covered.
- Each public class and method of every `aiobotocore` service gets valid type
  annotations extracted from `botocore` schemas.
- Type annotations include up-to-date documentation.
- Link to documentation is provided for every method.
- Code is processed by [ruff](https://docs.astral.sh/ruff/) for readability.

<a id="what's-new"></a>

## What's new

<a id="implemented-features"></a>

### Implemented features

- Fully type annotated `boto3`, `botocore`, `aiobotocore` and `aioboto3`
  libraries
- `mypy`, `pyright`, `VSCode`, `PyCharm`, `Sublime Text` and `Emacs`
  compatibility
- `Client`, `ServiceResource`, `Resource`, `Waiter` `Paginator` type
  annotations for each service
- Generated `TypeDefs` for each service
- Generated `Literals` for each service
- Auto discovery of types for `boto3.client` and `boto3.resource` calls
- Auto discovery of types for `session.client` and `session.resource` calls
- Auto discovery of types for `client.get_waiter` and `client.get_paginator`
  calls
- Auto discovery of types for `ServiceResource` and `Resource` collections
- Auto discovery of types for `aiobotocore.Session.create_client` calls

<a id="latest-changes"></a>

### Latest changes

Builder changelog can be found in
[Releases](https://github.com/youtype/mypy_boto3_builder/releases).

<a id="versioning"></a>

## Versioning

`types-aiobotocore-quicksight` version is the same as related `aiobotocore`
version and follows
[Python Packaging version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/).

<a id="thank-you"></a>

## Thank you

- [Allie Fitter](https://github.com/alliefitter) for
  [boto3-type-annotations](https://pypi.org/project/boto3-type-annotations/),
  this package is based on top of his work
- [black](https://github.com/psf/black) developers for an awesome formatting
  tool
- [Timothy Edmund Crosley](https://github.com/timothycrosley) for
  [isort](https://github.com/PyCQA/isort) and how flexible it is
- [mypy](https://github.com/python/mypy) developers for doing all dirty work
  for us
- [pyright](https://github.com/microsoft/pyright) team for the new era of typed
  Python

<a id="documentation"></a>

## Documentation

All services type annotations can be found in
[aiobotocore docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_quicksight/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.
