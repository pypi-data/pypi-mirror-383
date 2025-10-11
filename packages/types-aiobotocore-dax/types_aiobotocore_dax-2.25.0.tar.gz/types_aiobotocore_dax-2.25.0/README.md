<a id="types-aiobotocore-dax"></a>

# types-aiobotocore-dax

[![PyPI - types-aiobotocore-dax](https://img.shields.io/pypi/v/types-aiobotocore-dax.svg?color=blue)](https://pypi.org/project/types-aiobotocore-dax/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-aiobotocore-dax.svg?color=blue)](https://pypi.org/project/types-aiobotocore-dax/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/types_aiobotocore_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/types-aiobotocore-dax)](https://pypistats.org/packages/types-aiobotocore-dax)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for
[aiobotocore DAX 2.25.0](https://pypi.org/project/aiobotocore/) compatible with
[VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found on
[types-aiobotocore](https://pypi.org/project/types-aiobotocore/) page and in
[types-aiobotocore-dax docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dax/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [types-aiobotocore-dax](#types-aiobotocore-dax)
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
3. Add `DAX` service.
4. Use provided commands to install generated packages.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `types-aiobotocore` for `DAX` service.

```bash
# install with aiobotocore type annotations
python -m pip install 'types-aiobotocore[dax]'

# Lite version does not provide session.client/resource overloads
# it is more RAM-friendly, but requires explicit type annotations
python -m pip install 'types-aiobotocore-lite[dax]'

# standalone installation
python -m pip install types-aiobotocore-dax
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
python -m pip uninstall -y types-aiobotocore-dax
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
- Install `types-aiobotocore[dax]` in your environment:

```bash
python -m pip install 'types-aiobotocore[dax]'
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

Install `types-aiobotocore[dax]` in your environment:

```bash
python -m pip install 'types-aiobotocore[dax]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `types-aiobotocore` with services you use in your environment:

```bash
python -m pip install 'types-aiobotocore[dax]'
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

- Install `types-aiobotocore[dax]` with services you use in your environment:

```bash
python -m pip install 'types-aiobotocore[dax]'
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
- Install `types-aiobotocore[dax]` in your environment:

```bash
python -m pip install 'types-aiobotocore[dax]'
```

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `types-aiobotocore[dax]` in your environment:

```bash
python -m pip install 'types-aiobotocore[dax]'
```

Optionally, you can install `types-aiobotocore` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `aiobotocore` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid
`types-aiobotocore-dax` dependency in production. However, there is an issue in
`pylint` that it complains about undefined variables. To fix it, set all types
to `object` in non-`TYPE_CHECKING` mode.

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

`DAXClient` provides annotations for `session.create_client("dax")`.

```python
from aiobotocore.session import get_session

from types_aiobotocore_dax import DAXClient

session = get_session()
async with session.create_client("dax") as client:
    client: DAXClient
    # now client usage is checked by mypy and IDE should provide code completion
```

<a id="paginators-annotations"></a>

### Paginators annotations

`types_aiobotocore_dax.paginator` module contains type annotations for all
paginators.

```python
from aiobotocore.session import get_session

from types_aiobotocore_dax import DAXClient
from types_aiobotocore_dax.paginator import (
    DescribeClustersPaginator,
    DescribeDefaultParametersPaginator,
    DescribeEventsPaginator,
    DescribeParameterGroupsPaginator,
    DescribeParametersPaginator,
    DescribeSubnetGroupsPaginator,
    ListTagsPaginator,
)

session = get_session()
async with session.create_client("dax") as client:
    client: DAXClient

    # Explicit type annotations are optional here
    # Types should be correctly discovered by mypy and IDEs
    describe_clusters_paginator: DescribeClustersPaginator = client.get_paginator(
        "describe_clusters"
    )
    describe_default_parameters_paginator: DescribeDefaultParametersPaginator = (
        client.get_paginator("describe_default_parameters")
    )
    describe_events_paginator: DescribeEventsPaginator = client.get_paginator("describe_events")
    describe_parameter_groups_paginator: DescribeParameterGroupsPaginator = client.get_paginator(
        "describe_parameter_groups"
    )
    describe_parameters_paginator: DescribeParametersPaginator = client.get_paginator(
        "describe_parameters"
    )
    describe_subnet_groups_paginator: DescribeSubnetGroupsPaginator = client.get_paginator(
        "describe_subnet_groups"
    )
    list_tags_paginator: ListTagsPaginator = client.get_paginator("list_tags")
```

<a id="literals"></a>

### Literals

`types_aiobotocore_dax.literals` module contains literals extracted from shapes
that can be used in user code for type checking.

Full list of `DAX` Literals can be found in
[docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dax/literals/).

```python
from types_aiobotocore_dax.literals import ChangeTypeType


def check_value(value: ChangeTypeType) -> bool: ...
```

<a id="type-definitions"></a>

### Type definitions

`types_aiobotocore_dax.type_defs` module contains structures and shapes
assembled to typed dictionaries and unions for additional type checking.

Full list of `DAX` TypeDefs can be found in
[docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dax/type_defs/).

```python
# TypedDict usage example
from types_aiobotocore_dax.type_defs import EndpointTypeDef


def get_value() -> EndpointTypeDef:
    return {
        "Address": ...,
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

`types-aiobotocore-dax` version is the same as related `aiobotocore` version
and follows
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
[aiobotocore docs](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_dax/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.
