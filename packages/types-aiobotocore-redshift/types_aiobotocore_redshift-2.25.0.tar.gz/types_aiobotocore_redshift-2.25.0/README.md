<a id="types-aiobotocore-redshift"></a>

# types-aiobotocore-redshift

[![PyPI - types-aiobotocore-redshift](https://img.shields.io/pypi/v/types-aiobotocore-redshift.svg?color=blue)](https://pypi.org/project/types-aiobotocore-redshift/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-aiobotocore-redshift.svg?color=blue)](https://pypi.org/project/types-aiobotocore-redshift/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/types_aiobotocore_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/types-aiobotocore-redshift)](https://pypistats.org/packages/types-aiobotocore-redshift)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for
[aiobotocore Redshift 2.25.0](https://pypi.org/project/aiobotocore/) compatible
with [VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found on
[types-aiobotocore](https://pypi.org/project/types-aiobotocore/) page and in
[types-aiobotocore-redshift docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_redshift/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [types-aiobotocore-redshift](#types-aiobotocore-redshift)
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
    - [Waiters annotations](#waiters-annotations)
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
3. Add `Redshift` service.
4. Use provided commands to install generated packages.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `types-aiobotocore` for `Redshift` service.

```bash
# install with aiobotocore type annotations
python -m pip install 'types-aiobotocore[redshift]'

# Lite version does not provide session.client/resource overloads
# it is more RAM-friendly, but requires explicit type annotations
python -m pip install 'types-aiobotocore-lite[redshift]'

# standalone installation
python -m pip install types-aiobotocore-redshift
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
python -m pip uninstall -y types-aiobotocore-redshift
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
- Install `types-aiobotocore[redshift]` in your environment:

```bash
python -m pip install 'types-aiobotocore[redshift]'
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

Install `types-aiobotocore[redshift]` in your environment:

```bash
python -m pip install 'types-aiobotocore[redshift]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `types-aiobotocore` with services you use in your environment:

```bash
python -m pip install 'types-aiobotocore[redshift]'
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

- Install `types-aiobotocore[redshift]` with services you use in your
  environment:

```bash
python -m pip install 'types-aiobotocore[redshift]'
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
- Install `types-aiobotocore[redshift]` in your environment:

```bash
python -m pip install 'types-aiobotocore[redshift]'
```

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `types-aiobotocore[redshift]` in your environment:

```bash
python -m pip install 'types-aiobotocore[redshift]'
```

Optionally, you can install `types-aiobotocore` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid
`types-aiobotocore-redshift` dependency in production. However, there is an
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

`RedshiftClient` provides annotations for `session.create_client("redshift")`.

```python
from aiobotocore.session import get_session

from types_aiobotocore_redshift import RedshiftClient

session = get_session()
async with session.create_client("redshift") as client:
    client: RedshiftClient
    # now client usage is checked by mypy and IDE should provide code completion
```

<a id="paginators-annotations"></a>

### Paginators annotations

`types_aiobotocore_redshift.paginator` module contains type annotations for all
paginators.

```python
from aiobotocore.session import get_session

from types_aiobotocore_redshift import RedshiftClient
from types_aiobotocore_redshift.paginator import (
    DescribeClusterDbRevisionsPaginator,
    DescribeClusterParameterGroupsPaginator,
    DescribeClusterParametersPaginator,
    DescribeClusterSecurityGroupsPaginator,
    DescribeClusterSnapshotsPaginator,
    DescribeClusterSubnetGroupsPaginator,
    DescribeClusterTracksPaginator,
    DescribeClusterVersionsPaginator,
    DescribeClustersPaginator,
    DescribeCustomDomainAssociationsPaginator,
    DescribeDataSharesForConsumerPaginator,
    DescribeDataSharesForProducerPaginator,
    DescribeDataSharesPaginator,
    DescribeDefaultClusterParametersPaginator,
    DescribeEndpointAccessPaginator,
    DescribeEndpointAuthorizationPaginator,
    DescribeEventSubscriptionsPaginator,
    DescribeEventsPaginator,
    DescribeHsmClientCertificatesPaginator,
    DescribeHsmConfigurationsPaginator,
    DescribeInboundIntegrationsPaginator,
    DescribeIntegrationsPaginator,
    DescribeNodeConfigurationOptionsPaginator,
    DescribeOrderableClusterOptionsPaginator,
    DescribeRedshiftIdcApplicationsPaginator,
    DescribeReservedNodeExchangeStatusPaginator,
    DescribeReservedNodeOfferingsPaginator,
    DescribeReservedNodesPaginator,
    DescribeScheduledActionsPaginator,
    DescribeSnapshotCopyGrantsPaginator,
    DescribeSnapshotSchedulesPaginator,
    DescribeTableRestoreStatusPaginator,
    DescribeTagsPaginator,
    DescribeUsageLimitsPaginator,
    GetReservedNodeExchangeConfigurationOptionsPaginator,
    GetReservedNodeExchangeOfferingsPaginator,
    ListRecommendationsPaginator,
)

session = get_session()
async with session.create_client("redshift") as client:
    client: RedshiftClient

    # Explicit type annotations are optional here
    # Types should be correctly discovered by mypy and IDEs
    describe_cluster_db_revisions_paginator: DescribeClusterDbRevisionsPaginator = (
        client.get_paginator("describe_cluster_db_revisions")
    )
    describe_cluster_parameter_groups_paginator: DescribeClusterParameterGroupsPaginator = (
        client.get_paginator("describe_cluster_parameter_groups")
    )
    describe_cluster_parameters_paginator: DescribeClusterParametersPaginator = (
        client.get_paginator("describe_cluster_parameters")
    )
    describe_cluster_security_groups_paginator: DescribeClusterSecurityGroupsPaginator = (
        client.get_paginator("describe_cluster_security_groups")
    )
    describe_cluster_snapshots_paginator: DescribeClusterSnapshotsPaginator = client.get_paginator(
        "describe_cluster_snapshots"
    )
    describe_cluster_subnet_groups_paginator: DescribeClusterSubnetGroupsPaginator = (
        client.get_paginator("describe_cluster_subnet_groups")
    )
    describe_cluster_tracks_paginator: DescribeClusterTracksPaginator = client.get_paginator(
        "describe_cluster_tracks"
    )
    describe_cluster_versions_paginator: DescribeClusterVersionsPaginator = client.get_paginator(
        "describe_cluster_versions"
    )
    describe_clusters_paginator: DescribeClustersPaginator = client.get_paginator(
        "describe_clusters"
    )
    describe_custom_domain_associations_paginator: DescribeCustomDomainAssociationsPaginator = (
        client.get_paginator("describe_custom_domain_associations")
    )
    describe_data_shares_for_consumer_paginator: DescribeDataSharesForConsumerPaginator = (
        client.get_paginator("describe_data_shares_for_consumer")
    )
    describe_data_shares_for_producer_paginator: DescribeDataSharesForProducerPaginator = (
        client.get_paginator("describe_data_shares_for_producer")
    )
    describe_data_shares_paginator: DescribeDataSharesPaginator = client.get_paginator(
        "describe_data_shares"
    )
    describe_default_cluster_parameters_paginator: DescribeDefaultClusterParametersPaginator = (
        client.get_paginator("describe_default_cluster_parameters")
    )
    describe_endpoint_access_paginator: DescribeEndpointAccessPaginator = client.get_paginator(
        "describe_endpoint_access"
    )
    describe_endpoint_authorization_paginator: DescribeEndpointAuthorizationPaginator = (
        client.get_paginator("describe_endpoint_authorization")
    )
    describe_event_subscriptions_paginator: DescribeEventSubscriptionsPaginator = (
        client.get_paginator("describe_event_subscriptions")
    )
    describe_events_paginator: DescribeEventsPaginator = client.get_paginator("describe_events")
    describe_hsm_client_certificates_paginator: DescribeHsmClientCertificatesPaginator = (
        client.get_paginator("describe_hsm_client_certificates")
    )
    describe_hsm_configurations_paginator: DescribeHsmConfigurationsPaginator = (
        client.get_paginator("describe_hsm_configurations")
    )
    describe_inbound_integrations_paginator: DescribeInboundIntegrationsPaginator = (
        client.get_paginator("describe_inbound_integrations")
    )
    describe_integrations_paginator: DescribeIntegrationsPaginator = client.get_paginator(
        "describe_integrations"
    )
    describe_node_configuration_options_paginator: DescribeNodeConfigurationOptionsPaginator = (
        client.get_paginator("describe_node_configuration_options")
    )
    describe_orderable_cluster_options_paginator: DescribeOrderableClusterOptionsPaginator = (
        client.get_paginator("describe_orderable_cluster_options")
    )
    describe_redshift_idc_applications_paginator: DescribeRedshiftIdcApplicationsPaginator = (
        client.get_paginator("describe_redshift_idc_applications")
    )
    describe_reserved_node_exchange_status_paginator: DescribeReservedNodeExchangeStatusPaginator = client.get_paginator(
        "describe_reserved_node_exchange_status"
    )
    describe_reserved_node_offerings_paginator: DescribeReservedNodeOfferingsPaginator = (
        client.get_paginator("describe_reserved_node_offerings")
    )
    describe_reserved_nodes_paginator: DescribeReservedNodesPaginator = client.get_paginator(
        "describe_reserved_nodes"
    )
    describe_scheduled_actions_paginator: DescribeScheduledActionsPaginator = client.get_paginator(
        "describe_scheduled_actions"
    )
    describe_snapshot_copy_grants_paginator: DescribeSnapshotCopyGrantsPaginator = (
        client.get_paginator("describe_snapshot_copy_grants")
    )
    describe_snapshot_schedules_paginator: DescribeSnapshotSchedulesPaginator = (
        client.get_paginator("describe_snapshot_schedules")
    )
    describe_table_restore_status_paginator: DescribeTableRestoreStatusPaginator = (
        client.get_paginator("describe_table_restore_status")
    )
    describe_tags_paginator: DescribeTagsPaginator = client.get_paginator("describe_tags")
    describe_usage_limits_paginator: DescribeUsageLimitsPaginator = client.get_paginator(
        "describe_usage_limits"
    )
    get_reserved_node_exchange_configuration_options_paginator: GetReservedNodeExchangeConfigurationOptionsPaginator = client.get_paginator(
        "get_reserved_node_exchange_configuration_options"
    )
    get_reserved_node_exchange_offerings_paginator: GetReservedNodeExchangeOfferingsPaginator = (
        client.get_paginator("get_reserved_node_exchange_offerings")
    )
    list_recommendations_paginator: ListRecommendationsPaginator = client.get_paginator(
        "list_recommendations"
    )
```

<a id="waiters-annotations"></a>

### Waiters annotations

`types_aiobotocore_redshift.waiter` module contains type annotations for all
waiters.

```python
from aiobotocore.session import get_session

from types_aiobotocore_redshift.client import RedshiftClient
from types_aiobotocore_redshift.waiter import (
    ClusterAvailableWaiter,
    ClusterDeletedWaiter,
    ClusterRestoredWaiter,
    SnapshotAvailableWaiter,
)

session = get_session()
async with session.create_client("redshift") as client:
    client: RedshiftClient

    # Explicit type annotations are optional here
    # Types should be correctly discovered by mypy and IDEs
    cluster_available_waiter: ClusterAvailableWaiter = client.get_waiter("cluster_available")
    cluster_deleted_waiter: ClusterDeletedWaiter = client.get_waiter("cluster_deleted")
    cluster_restored_waiter: ClusterRestoredWaiter = client.get_waiter("cluster_restored")
    snapshot_available_waiter: SnapshotAvailableWaiter = client.get_waiter("snapshot_available")
```

<a id="literals"></a>

### Literals

`types_aiobotocore_redshift.literals` module contains literals extracted from
shapes that can be used in user code for type checking.

Full list of `Redshift` Literals can be found in
[docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_redshift/literals/).

```python
from types_aiobotocore_redshift.literals import ActionTypeType


def check_value(value: ActionTypeType) -> bool: ...
```

<a id="type-definitions"></a>

### Type definitions

`types_aiobotocore_redshift.type_defs` module contains structures and shapes
assembled to typed dictionaries and unions for additional type checking.

Full list of `Redshift` TypeDefs can be found in
[docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_redshift/type_defs/).

```python
# TypedDict usage example
from types_aiobotocore_redshift.type_defs import AcceptReservedNodeExchangeInputMessageTypeDef


def get_value() -> AcceptReservedNodeExchangeInputMessageTypeDef:
    return {
        "ReservedNodeId": ...,
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

`types-aiobotocore-redshift` version is the same as related `aiobotocore`
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
[aiobotocore docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_redshift/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.
