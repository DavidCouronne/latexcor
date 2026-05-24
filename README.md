# latexcor

[![PyPI version](https://badge.fury.io/py/latexcor.svg)](https://badge.fury.io/py/latexcor)
[![Python Versions](https://img.shields.io/pypi/pyversions/latexcor.svg)](https://pypi.org/project/latexcor/)
[![Downloads](https://pepy.tech/badge/latexcor)](https://pepy.tech/project/latexcor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LaTeX Compiler and File Manager - Automate your LaTeX workflow

## Features

- Clean auxiliary LaTeX files
- Convert .tex files to UTF-8 encoding
- Recompile LaTeX files automatically
- Slugify file and directory names
- Watch directory for changes and auto-compile
- Support for XeLaTeX and LuaLaTeX engines

## Installation

Nécessite podman:

Arch linux:

```bash
sudo pacman -S podman
```
Nécessite l'image docker:

``bash
podman pull docker.io/infocornouaille/tools:perso
````


Nécessite uv:

```bash
sudo pacman -S uv
```

```bash
uv tool install git+https://github.com/davidcouronne/latexcor.git --force
```

## Usage

```console
$ latexcor [OPTIONS] COMMAND [ARGS]...
```

### Global Options

- `--install-completion`: Install completion for the current shell
- `--show-completion`: Show completion for the current shell
- `--help`: Show help message and exit

### Commands

#### Clean (`clean`)

Clean auxiliary LaTeX files in a directory.

```console
$ latexcor clean [OPTIONS]

Options:
  -p, --path DIRECTORY  Path to clean (defaults to current directory)
  --help               Show this message and exit
```

#### Convert to UTF-8 (`convert-utf8`)

Convert .tex files to UTF-8 encoding.

```console
$ latexcor convert-utf8 [OPTIONS]

Options:
  -p, --path DIRECTORY  Path to process (defaults to current directory)
  --help               Show this message and exit
```

#### Recompile (`recompile`)

Recompile all LaTeX files in a directory.

```console
$ latexcor recompile [OPTIONS]

Options:
  -e, --engine [xelatex|lualatex]  LaTeX engine to use [default: xelatex]
  -p, --path DIRECTORY            Path to process (defaults to current directory)
  -c, --confirm                   Confirm before recompiling each file
  --help                          Show this message and exit
```

#### Slugify (`slugify`)

Rename files and directories using slug format.

```console
$ latexcor slugify [OPTIONS]

Options:
  -p, --path DIRECTORY           Path to process (defaults to current directory)
  -c, --confirm / -C, --no-confirm  Confirm before renaming [default: confirm]
  -v, --preview / -V, --no-preview  Show preview of changes [default: preview]
  --help                         Show this message and exit
```

#### Version (`version`)

Display the current version of latexcor.

```console
$ latexcor version [OPTIONS]

Options:
  --help  Show this message and exit
```

#### Watch (`watch`)

Watch a directory and automatically compile LaTeX files when changes are detected.

```console
$ latexcor watch [OPTIONS]

Options:
  -e, --engine [xelatex|lualatex]  LaTeX engine to use [default: xelatex]
  -p, --path DIRECTORY            Path to watch (defaults to current directory)
  --help                          Show this message and exit
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.