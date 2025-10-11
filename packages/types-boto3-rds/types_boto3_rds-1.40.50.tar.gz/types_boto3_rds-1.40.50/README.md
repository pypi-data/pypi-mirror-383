<a id="types-boto3-rds"></a>

# types-boto3-rds

[![PyPI - types-boto3-rds](https://img.shields.io/pypi/v/types-boto3-rds.svg?color=blue)](https://pypi.org/project/types-boto3-rds/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-boto3-rds.svg?color=blue)](https://pypi.org/project/types-boto3-rds/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/types_boto3_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/types-boto3-rds)](https://pypistats.org/packages/types-boto3-rds)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for [boto3 RDS 1.40.50](https://pypi.org/project/boto3/)
compatible with [VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found on
[types-boto3](https://pypi.org/project/types-boto3/) page and in
[types-boto3-rds docs](https://youtype.github.io/types_boto3_docs/types_boto3_rds/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [types-boto3-rds](#types-boto3-rds)
  - [How to install](#how-to-install)
    - [Generate locally (recommended)](<#generate-locally-(recommended)>)
    - [VSCode extension](#vscode-extension)
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

You can generate type annotations for `boto3` package locally with
`mypy-boto3-builder`. Use
[uv](https://docs.astral.sh/uv/getting-started/installation/) for build
isolation.

1. Run mypy-boto3-builder in your package root directory:
   `uvx --with 'boto3==1.40.50' mypy-boto3-builder`
2. Select `boto3` AWS SDK.
3. Add `RDS` service.
4. Use provided commands to install generated packages.

<a id="vscode-extension"></a>

### VSCode extension

Add
[AWS Boto3](https://marketplace.visualstudio.com/items?itemName=Boto3typed.boto3-ide)
extension to your VSCode and run `AWS boto3: Quick Start` command.

Click `Modify` and select `boto3 common` and `RDS`.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `types-boto3` for `RDS` service.

```bash
# install with boto3 type annotations
python -m pip install 'types-boto3[rds]'

# Lite version does not provide session.client/resource overloads
# it is more RAM-friendly, but requires explicit type annotations
python -m pip install 'types-boto3-lite[rds]'

# standalone installation
python -m pip install types-boto3-rds
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
python -m pip uninstall -y types-boto3-rds
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
- Install `types-boto3[rds]` in your environment:

```bash
python -m pip install 'types-boto3[rds]'
```

Both type checking and code completion should now work. No explicit type
annotations required, write your `boto3` code as usual.

<a id="pycharm"></a>

### PyCharm

> ⚠️ Due to slow PyCharm performance on `Literal` overloads (issue
> [PY-40997](https://youtrack.jetbrains.com/issue/PY-40997)), it is recommended
> to use [types-boto3-lite](https://pypi.org/project/types-boto3-lite/) until
> the issue is resolved.

> ⚠️ If you experience slow performance and high CPU usage, try to disable
> `PyCharm` type checker and use [mypy](https://github.com/python/mypy) or
> [pyright](https://github.com/microsoft/pyright) instead.

> ⚠️ To continue using `PyCharm` type checker, you can try to replace
> `types-boto3` with
> [types-boto3-lite](https://pypi.org/project/types-boto3-lite/):

```bash
pip uninstall types-boto3
pip install types-boto3-lite
```

Install `types-boto3[rds]` in your environment:

```bash
python -m pip install 'types-boto3[rds]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `types-boto3` with services you use in your environment:

```bash
python -m pip install 'types-boto3[rds]'
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

- Make sure emacs uses the environment where you have installed `types-boto3`

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="sublime-text"></a>

### Sublime Text

- Install `types-boto3[rds]` with services you use in your environment:

```bash
python -m pip install 'types-boto3[rds]'
```

- Install [LSP-pyright](https://github.com/sublimelsp/LSP-pyright) package

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="other-ides"></a>

### Other IDEs

Not tested, but as long as your IDE supports `mypy` or `pyright`, everything
should work.

<a id="mypy"></a>

### mypy

- Install `mypy`: `python -m pip install mypy`
- Install `types-boto3[rds]` in your environment:

```bash
python -m pip install 'types-boto3[rds]'
```

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `types-boto3[rds]` in your environment:

```bash
python -m pip install 'types-boto3[rds]'
```

Optionally, you can install `types-boto3` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid
`types-boto3-rds` dependency in production. However, there is an issue in
`pylint` that it complains about undefined variables. To fix it, set all types
to `object` in non-`TYPE_CHECKING` mode.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types_boto3_ec2 import EC2Client, EC2ServiceResource
    from types_boto3_ec2.waiters import BundleTaskCompleteWaiter
    from types_boto3_ec2.paginators import DescribeVolumesPaginator
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

`RDSClient` provides annotations for `boto3.client("rds")`.

```python
from boto3.session import Session

from types_boto3_rds import RDSClient

client: RDSClient = Session().client("rds")

# now client usage is checked by mypy and IDE should provide code completion
```

<a id="paginators-annotations"></a>

### Paginators annotations

`types_boto3_rds.paginator` module contains type annotations for all
paginators.

```python
from boto3.session import Session

from types_boto3_rds import RDSClient
from types_boto3_rds.paginator import (
    DescribeBlueGreenDeploymentsPaginator,
    DescribeCertificatesPaginator,
    DescribeDBClusterAutomatedBackupsPaginator,
    DescribeDBClusterBacktracksPaginator,
    DescribeDBClusterEndpointsPaginator,
    DescribeDBClusterParameterGroupsPaginator,
    DescribeDBClusterParametersPaginator,
    DescribeDBClusterSnapshotsPaginator,
    DescribeDBClustersPaginator,
    DescribeDBEngineVersionsPaginator,
    DescribeDBInstanceAutomatedBackupsPaginator,
    DescribeDBInstancesPaginator,
    DescribeDBLogFilesPaginator,
    DescribeDBMajorEngineVersionsPaginator,
    DescribeDBParameterGroupsPaginator,
    DescribeDBParametersPaginator,
    DescribeDBProxiesPaginator,
    DescribeDBProxyEndpointsPaginator,
    DescribeDBProxyTargetGroupsPaginator,
    DescribeDBProxyTargetsPaginator,
    DescribeDBRecommendationsPaginator,
    DescribeDBSecurityGroupsPaginator,
    DescribeDBSnapshotTenantDatabasesPaginator,
    DescribeDBSnapshotsPaginator,
    DescribeDBSubnetGroupsPaginator,
    DescribeEngineDefaultClusterParametersPaginator,
    DescribeEngineDefaultParametersPaginator,
    DescribeEventSubscriptionsPaginator,
    DescribeEventsPaginator,
    DescribeExportTasksPaginator,
    DescribeGlobalClustersPaginator,
    DescribeIntegrationsPaginator,
    DescribeOptionGroupOptionsPaginator,
    DescribeOptionGroupsPaginator,
    DescribeOrderableDBInstanceOptionsPaginator,
    DescribePendingMaintenanceActionsPaginator,
    DescribeReservedDBInstancesOfferingsPaginator,
    DescribeReservedDBInstancesPaginator,
    DescribeSourceRegionsPaginator,
    DescribeTenantDatabasesPaginator,
    DownloadDBLogFilePortionPaginator,
)

client: RDSClient = Session().client("rds")

# Explicit type annotations are optional here
# Types should be correctly discovered by mypy and IDEs
describe_blue_green_deployments_paginator: DescribeBlueGreenDeploymentsPaginator = (
    client.get_paginator("describe_blue_green_deployments")
)
describe_certificates_paginator: DescribeCertificatesPaginator = client.get_paginator(
    "describe_certificates"
)
describe_db_cluster_automated_backups_paginator: DescribeDBClusterAutomatedBackupsPaginator = (
    client.get_paginator("describe_db_cluster_automated_backups")
)
describe_db_cluster_backtracks_paginator: DescribeDBClusterBacktracksPaginator = (
    client.get_paginator("describe_db_cluster_backtracks")
)
describe_db_cluster_endpoints_paginator: DescribeDBClusterEndpointsPaginator = client.get_paginator(
    "describe_db_cluster_endpoints"
)
describe_db_cluster_parameter_groups_paginator: DescribeDBClusterParameterGroupsPaginator = (
    client.get_paginator("describe_db_cluster_parameter_groups")
)
describe_db_cluster_parameters_paginator: DescribeDBClusterParametersPaginator = (
    client.get_paginator("describe_db_cluster_parameters")
)
describe_db_cluster_snapshots_paginator: DescribeDBClusterSnapshotsPaginator = client.get_paginator(
    "describe_db_cluster_snapshots"
)
describe_db_clusters_paginator: DescribeDBClustersPaginator = client.get_paginator(
    "describe_db_clusters"
)
describe_db_engine_versions_paginator: DescribeDBEngineVersionsPaginator = client.get_paginator(
    "describe_db_engine_versions"
)
describe_db_instance_automated_backups_paginator: DescribeDBInstanceAutomatedBackupsPaginator = (
    client.get_paginator("describe_db_instance_automated_backups")
)
describe_db_instances_paginator: DescribeDBInstancesPaginator = client.get_paginator(
    "describe_db_instances"
)
describe_db_log_files_paginator: DescribeDBLogFilesPaginator = client.get_paginator(
    "describe_db_log_files"
)
describe_db_major_engine_versions_paginator: DescribeDBMajorEngineVersionsPaginator = (
    client.get_paginator("describe_db_major_engine_versions")
)
describe_db_parameter_groups_paginator: DescribeDBParameterGroupsPaginator = client.get_paginator(
    "describe_db_parameter_groups"
)
describe_db_parameters_paginator: DescribeDBParametersPaginator = client.get_paginator(
    "describe_db_parameters"
)
describe_db_proxies_paginator: DescribeDBProxiesPaginator = client.get_paginator(
    "describe_db_proxies"
)
describe_db_proxy_endpoints_paginator: DescribeDBProxyEndpointsPaginator = client.get_paginator(
    "describe_db_proxy_endpoints"
)
describe_db_proxy_target_groups_paginator: DescribeDBProxyTargetGroupsPaginator = (
    client.get_paginator("describe_db_proxy_target_groups")
)
describe_db_proxy_targets_paginator: DescribeDBProxyTargetsPaginator = client.get_paginator(
    "describe_db_proxy_targets"
)
describe_db_recommendations_paginator: DescribeDBRecommendationsPaginator = client.get_paginator(
    "describe_db_recommendations"
)
describe_db_security_groups_paginator: DescribeDBSecurityGroupsPaginator = client.get_paginator(
    "describe_db_security_groups"
)
describe_db_snapshot_tenant_databases_paginator: DescribeDBSnapshotTenantDatabasesPaginator = (
    client.get_paginator("describe_db_snapshot_tenant_databases")
)
describe_db_snapshots_paginator: DescribeDBSnapshotsPaginator = client.get_paginator(
    "describe_db_snapshots"
)
describe_db_subnet_groups_paginator: DescribeDBSubnetGroupsPaginator = client.get_paginator(
    "describe_db_subnet_groups"
)
describe_engine_default_cluster_parameters_paginator: DescribeEngineDefaultClusterParametersPaginator = client.get_paginator(
    "describe_engine_default_cluster_parameters"
)
describe_engine_default_parameters_paginator: DescribeEngineDefaultParametersPaginator = (
    client.get_paginator("describe_engine_default_parameters")
)
describe_event_subscriptions_paginator: DescribeEventSubscriptionsPaginator = client.get_paginator(
    "describe_event_subscriptions"
)
describe_events_paginator: DescribeEventsPaginator = client.get_paginator("describe_events")
describe_export_tasks_paginator: DescribeExportTasksPaginator = client.get_paginator(
    "describe_export_tasks"
)
describe_global_clusters_paginator: DescribeGlobalClustersPaginator = client.get_paginator(
    "describe_global_clusters"
)
describe_integrations_paginator: DescribeIntegrationsPaginator = client.get_paginator(
    "describe_integrations"
)
describe_option_group_options_paginator: DescribeOptionGroupOptionsPaginator = client.get_paginator(
    "describe_option_group_options"
)
describe_option_groups_paginator: DescribeOptionGroupsPaginator = client.get_paginator(
    "describe_option_groups"
)
describe_orderable_db_instance_options_paginator: DescribeOrderableDBInstanceOptionsPaginator = (
    client.get_paginator("describe_orderable_db_instance_options")
)
describe_pending_maintenance_actions_paginator: DescribePendingMaintenanceActionsPaginator = (
    client.get_paginator("describe_pending_maintenance_actions")
)
describe_reserved_db_instances_offerings_paginator: DescribeReservedDBInstancesOfferingsPaginator = client.get_paginator(
    "describe_reserved_db_instances_offerings"
)
describe_reserved_db_instances_paginator: DescribeReservedDBInstancesPaginator = (
    client.get_paginator("describe_reserved_db_instances")
)
describe_source_regions_paginator: DescribeSourceRegionsPaginator = client.get_paginator(
    "describe_source_regions"
)
describe_tenant_databases_paginator: DescribeTenantDatabasesPaginator = client.get_paginator(
    "describe_tenant_databases"
)
download_db_log_file_portion_paginator: DownloadDBLogFilePortionPaginator = client.get_paginator(
    "download_db_log_file_portion"
)
```

<a id="waiters-annotations"></a>

### Waiters annotations

`types_boto3_rds.waiter` module contains type annotations for all waiters.

```python
from boto3.session import Session

from types_boto3_rds import RDSClient
from types_boto3_rds.waiter import (
    DBClusterAvailableWaiter,
    DBClusterDeletedWaiter,
    DBClusterSnapshotAvailableWaiter,
    DBClusterSnapshotDeletedWaiter,
    DBInstanceAvailableWaiter,
    DBInstanceDeletedWaiter,
    DBSnapshotAvailableWaiter,
    DBSnapshotCompletedWaiter,
    DBSnapshotDeletedWaiter,
    TenantDatabaseAvailableWaiter,
    TenantDatabaseDeletedWaiter,
)

client: RDSClient = Session().client("rds")

# Explicit type annotations are optional here
# Types should be correctly discovered by mypy and IDEs
db_cluster_available_waiter: DBClusterAvailableWaiter = client.get_waiter("db_cluster_available")
db_cluster_deleted_waiter: DBClusterDeletedWaiter = client.get_waiter("db_cluster_deleted")
db_cluster_snapshot_available_waiter: DBClusterSnapshotAvailableWaiter = client.get_waiter(
    "db_cluster_snapshot_available"
)
db_cluster_snapshot_deleted_waiter: DBClusterSnapshotDeletedWaiter = client.get_waiter(
    "db_cluster_snapshot_deleted"
)
db_instance_available_waiter: DBInstanceAvailableWaiter = client.get_waiter("db_instance_available")
db_instance_deleted_waiter: DBInstanceDeletedWaiter = client.get_waiter("db_instance_deleted")
db_snapshot_available_waiter: DBSnapshotAvailableWaiter = client.get_waiter("db_snapshot_available")
db_snapshot_completed_waiter: DBSnapshotCompletedWaiter = client.get_waiter("db_snapshot_completed")
db_snapshot_deleted_waiter: DBSnapshotDeletedWaiter = client.get_waiter("db_snapshot_deleted")
tenant_database_available_waiter: TenantDatabaseAvailableWaiter = client.get_waiter(
    "tenant_database_available"
)
tenant_database_deleted_waiter: TenantDatabaseDeletedWaiter = client.get_waiter(
    "tenant_database_deleted"
)
```

<a id="literals"></a>

### Literals

`types_boto3_rds.literals` module contains literals extracted from shapes that
can be used in user code for type checking.

Full list of `RDS` Literals can be found in
[docs](https://youtype.github.io/types_boto3_docs/types_boto3_rds/literals/).

```python
from types_boto3_rds.literals import ActivityStreamModeType


def check_value(value: ActivityStreamModeType) -> bool: ...
```

<a id="type-definitions"></a>

### Type definitions

`types_boto3_rds.type_defs` module contains structures and shapes assembled to
typed dictionaries and unions for additional type checking.

Full list of `RDS` TypeDefs can be found in
[docs](https://youtype.github.io/types_boto3_docs/types_boto3_rds/type_defs/).

```python
# TypedDict usage example
from types_boto3_rds.type_defs import AccountQuotaTypeDef


def get_value() -> AccountQuotaTypeDef:
    return {
        "AccountQuotaName": ...,
    }
```

<a id="how-it-works"></a>

## How it works

Fully automated
[mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder) carefully
generates type annotations for each service, patiently waiting for `boto3`
updates. It delivers drop-in type annotations for you and makes sure that:

- All available `boto3` services are covered.
- Each public class and method of every `boto3` service gets valid type
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

`types-boto3-rds` version is the same as related `boto3` version and follows
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
[boto3 docs](https://youtype.github.io/types_boto3_docs/types_boto3_rds/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.
