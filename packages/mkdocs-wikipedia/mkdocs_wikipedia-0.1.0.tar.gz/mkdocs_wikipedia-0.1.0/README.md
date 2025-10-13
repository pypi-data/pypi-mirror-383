# MkDocs Wikipedia Plugin

[![CI](https://github.com/yves-chevallier/mkdocs-wikipedia/actions/workflows/ci.yml/badge.svg)](https://github.com/yves-chevallier/mkdocs-wikipedia/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/yves-chevallier/mkdocs-wikipedia/branch/main/graph/badge.svg)](https://codecov.io/gh/yves-chevallier/mkdocs-wikipedia)
[![PyPI](https://img.shields.io/pypi/v/mkdocs-wikipedia.svg)](https://pypi.org/project/mkdocs-wikipedia/)
[![Repo Size](https://img.shields.io/github/repo-size/yves-chevallier/mkdocs-wikipedia.svg)](https://github.com/yves-chevallier/mkdocs-wikipedia)
[![Python Versions](https://img.shields.io/pypi/pyversions/mkdocs-wikipedia.svg?logo=python)](https://pypi.org/project/mkdocs-wikipedia/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)

![MkDocs](https://img.shields.io/badge/MkDocs-1.6+-blue.svg?logo=mkdocs)
![MkDocs Material](https://img.shields.io/badge/MkDocs%20Material-supported-success.svg?logo=materialdesign)
![Wikipedia](https://img.shields.io/badge/Wikipedia-API-lightgrey.svg?logo=wikipedia)
![Python](https://img.shields.io/badge/Python-typed-blue.svg?logo=python)

This plugin allows you to fetch and display Wikipedia summaries in your MkDocs pages. It is compatible with MkDocs Material and MkDocs Books.

## Installation

```bash
pip install mkdocs-wikipedia
```

Activate the plugin in your `mkdocs.yml`:

```yaml
plugins:
  - wikipedia:
      language: "fr"
      timeout: 5
```

Install the plugin using pip:

```bash
pip install mkdocs-wikipedia
```

Activate the plugin in your `mkdocs.yml`:

```yaml
plugins:
  - wikipedia:
      language: "fr"
      timeout: 5
      filename: "links.yml"  # Optional, default is "links.yml"
```

## Usage

In you pages, when you add a wikipedia tag, it will be replaced by the summary of the corresponding Wikipedia page.

```md
[MkDocs](https://en.wikipedia.org/wiki/MkDocs)
```
