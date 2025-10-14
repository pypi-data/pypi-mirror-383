# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kipy',
 'kipy.proto',
 'kipy.proto.board',
 'kipy.proto.common',
 'kipy.proto.common.commands',
 'kipy.proto.common.types',
 'kipy.proto.schematic',
 'kipy.util']

package_data = \
{'': ['*']}

install_requires = \
['protobuf>=5.29,<6', 'pynng>=0.8.0,<0.9.0']

extras_require = \
{':python_version < "3.13"': ['typing_extensions>=4.13.2']}

setup_kwargs = {
    'name': 'kicad-python',
    'version': '0.5.0',
    'description': 'KiCad API Python Bindings',
    'long_description': '# KiCad API Python Bindings\n\n`kicad-python` is the official Python bindings for the [KiCad](https://kicad.org) IPC API.  This\nlibrary makes it possible to develop scripts and tools that interact with a running KiCad session.\n\nThe KiCad IPC API can be considered in "public beta" state with the release of KiCad 9 (currently\nplanned for on or around February 1, 2025).  The existing SWIG-based Python bindings for KiCad\'s\nPCB editor still exist in KiCad 9, but are in maintenance mode and will not be expanded.\n\nFor more information about the IPC API, please see the\n[KiCad developer documentation](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/index.html).\nSpecific documentation for developing add-ons is\n[also available](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/index.html).\n\n> Note: Version 0.0.2 and prior of this package are an obsolete earlier effort and are unrelated to\n> this codebase.\n\n## Requirements\n\nUsing the IPC API requires a suitable version of KiCad (9.0 or higher) and requires that KiCad be\nrunning with the API server enabled in Preferences > Plugins.  This package also depends on the\n`protobuf` and `pynng` packages for communication with KiCad.\n\n> Note: Unlike the SWIG-based Python bindings, the IPC API requires communication with a running\n> instance of KiCad.  It is not possible to use `kicad-python` to manipulate KiCad design files\n> without KiCad running.\n\n## Contributing\n\nPlease file bug reports and feature requests in this Gitlab project.  The team may move them to the\nmain KiCad repository depending on the nature of the request.\n\nMerge requests are welcome for minor fixes and improvements.  More significant changes should be\ndiscussed with the development team (via email, or in an issue) first.\n\n## Building from Source\n\nMost users should use `kicad-python` by installing the latest version from PyPI.  You can also\nbuild and install the library from this repository, to test unreleased changes or contribute to\nthe development.  For instructions on how to do so, please see `COMPILING.md`.\n\nNote that this library builds against the API definitions (`.proto` files) in the `kicad` submodule.\nOfficial releases of the library to PyPI should use a tagged release of KiCad, but the development\nbranch of `kicad-python` may sometimes move the submodule pointer to non-tagged commits during the\ncourse of development.  If you are using this library from source rather than from PyPI, remember\nto keep the submodule updated and to test against a suitable build of KiCad, which may need to be\na nightly or testing build in some situations.  You can use the method `KiCad.check_version` to\nmake sure you are using a compatible version of `kicad-python` for your installed version of KiCad.\n\n## Getting Started\n\nTo check that everything is working, install `kicad-python` (either follow the directions in\nCOMPILING.md or else install the latest version from PyPI using `pip install kicad-python`).\nLaunch KiCad, make sure the API server is enabled in Preferences > Plugins, and then you should be\nable to run:\n\n```sh\n$ python3 ./examples/hello.py\n```\n\nThis should print out the version of KiCad you have connected to.\n\n## Documentation\n\nThe documentation created from this repository (via the `docs` directory and the docstrings in the\nsource code) is hosted at https://docs.kicad.org/kicad-python-main\n\nMany things are still not documented or underdocumented -- contributions that expand the\ndocumentation or add docstrings are welcomed.\n\n## Examples\n\nCheck out the repository for some example scripts that may serve as a starting point.  Some of the\nexamples are snippets that can be run directly from a terminal or your Python development\nenvironment, and some are KiCad action plugins that can be loaded into the PCB editor.  For the\nplugins, copy or symlink them into the appropriate plugins path in order for KiCad to find them.\n\n## Release History\n\n### 0.5.0 (October 13, 2025)\n\n- Add `Pad.pad_to_die_length` (KiCad 9.0.4)\n- Add `Board.get_enabled_layers`, `Board.set_enabled_layers`, and `Board.get_copper_layer_count` (KiCad 9.0.5)\n- Autodetect default Flatpak socket path (Johannes Maibaum, !32)\n- Add support for `BoardCircle.rotate` (@modbw, !33)\n\n### 0.4.0 (July 8, 2025)\n\n- Fix ability to move and rotate footprints\n- Fix ArcTrack length calculation (Quentin Freimanis, !13)\n- Make it possible to add new `BoardPolygon`s in a more ergonomic way\n- Add `FootprintInstance.sheet_path` property (#37)\n- Add `board.check_padstack_presence_on_layers`, replacing FlashLayer in SWIG\n- Allow setting `Net.name` so that new nets can be created\n- Deprecate `Net.code` (net codes are an internal KiCad detail and API clients should ignore them)\n- Add `py.typed` type hinting indicator file (John Hagen, !16)\n- Fix `Vector2.from_xy_mm` type annotations (John Hagen, !17)\n- Add `Arc.angle` and `ArcTrack.angle`; some arc angle utilities (Quentin Freimanis, !14)\n- Add `remove_items_by_id` (Anthonypark, !20)\n- Allow assigning nets to `Zone` (#62)\n- Allow changing `Pad.pad_type` (#63)\n- Allow changing `Field.layer` (#64)\n\n### 0.3.0 (March 29, 2025)\n\n- Add support for footprint mounting style attribute (#19) (Thanh Duong, !10)\n- Added `visible` property to `Field` and deprecate it from `TextAttributes` to match KiCad changes\n- Improve version checking functions(Lucas Gerads, !11)\n- Add missing board layers User.10 through User.45 (#23)\n- Improve padstack-related APIs for creating new vias and pads (#21)\n- Change arc angle methods to return normalized angles; add degrees versions (#22)\n- Add `board.get_origin` and `board.set_origin` (#20)\n- Add `ArcTrack.length` (Thanh Duong, !12)\n- Add `Footprint.models` (#31)\n- Fix ability to create new graphic shapes on boards\n- Fix the return value of `Board.update_items` and document it (#35)\n\n### 0.2.0 (February 19, 2025)\n\n- Updates for KiCad 9.0.0 release\n- Fix `util.board_layer.canonical_name` names for technical layers\n- Add board item selection management APIs\n- Fix `requirements.txt` files in sample plugins\n- Fix RecursionError when calling `BoardCircle.__repr__` (#13)\n- Relicense as MIT\n\n### 0.1.2 (January 17, 2025)\n\n- Updates for KiCad 9.0.0-rc2 release\n- Fixes to plugin examples\n- Add support for various project settings, board stackup, board file management\n- Add helpers for board layer name conversions\n- Change thermal spoke settings to match updated KiCad API\n- Documentation improvements\n\n### 0.1.1 (December 24, 2024)\n\n- Bump dependency versions to fix compilation with newer protoc\n\n### 0.1.0 (December 21, 2024)\n\n*Corresponding KiCad version: 9.0.0-rc1*\n\nFirst formal release of the new IPC-API version of this package.  Contains support for most of the\nKiCad API functionality that is currently exposed, which is focused around the PCB editor to enable\na transition path from existing SWIG-based plugins.\n',
    'author': 'The KiCad Development Team',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://kicad.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
