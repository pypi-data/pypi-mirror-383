# coBib Zotero

[![pipeline](https://gitlab.com/cobib/cobib-zotero/badges/master/pipeline.svg)](https://gitlab.com/cobib/cobib-zotero/-/pipelines)
[![coverage](https://gitlab.com/cobib/cobib-zotero/badges/master/coverage.svg)](https://gitlab.com/cobib/cobib-zotero/-/graphs/master/charts)
[![Release](https://img.shields.io/gitlab/v/release/cobib/cobib-zotero?label=Release&logo=gitlab)](https://gitlab.com/cobib/cobib-zotero/-/releases/)
[![AUR](https://img.shields.io/aur/version/cobib-zotero?label=AUR&logo=archlinux)](https://aur.archlinux.org/packages/cobib-zotero)
[![PyPI](https://img.shields.io/pypi/v/cobib-zotero?label=PyPI&logo=pypi)](https://pypi.org/project/cobib-zotero/)
[![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https://gitlab.com/cobib/cobib-zotero/-/raw/master/pyproject.toml?ref_type=heads?label=Python&label=Python&logo=python)](https://gitlab.com/cobib/cobib-zotero/-/blob/master/pyproject.toml)
[![License](https://img.shields.io/gitlab/license/cobib/cobib-zotero?label=License)](https://gitlab.com/cobib/cobib-zotero/-/blob/master/LICENSE.txt)

A coBib Zotero importer plugin.


## Installation

For all common purposes you can install coBib via `pip`:

```
pip install cobib-zotero
```


### Arch Linux

This coBib plugin is packaged in the AUR.
* [cobib-zotero](https://aur.archlinux.org/packages/cobib-zotero/)
* [cobib-zotero-git](https://aur.archlinux.org/packages/cobib-zotero-git/)

## Usage

After installing this plugin, you can simply import a Zotero library via its `ID` and `type`, for example like so:
```bash
cobib import --zotero -- 8608002 "user"
```
When accessing a private library, you also need to specify an `--api-key`.


## Documentation

`cobib-zotero`'s documentation is hosted [here](https://cobib.gitlab.io/cobib-zotero/cobib_zotero.html).

### Changelog

You can find the detailed changes in [the Changelog](https://gitlab.com/cobib/cobib-zotero/-/blob/master/CHANGELOG.md).


## License

`cobib-zotero` is licensed under the [MIT License](https://gitlab.com/cobib/cobib-zotero/-/blob/master/LICENSE.txt).

[//]: # ( vim: set ft=markdown tw=0: )
