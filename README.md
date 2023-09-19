# Multi Page Tile Printing

> Work In Progress

This tool provide you to make tiles for print one image on multiple pages.

## Installation

### Linux

For sending images to printer on linux you need to install CUSP. 

```shell
sudo apt install -y libcups2-dev python3-dev gcc
```

#### Install Poetry if not installed yet

Documentation https://python-poetry.org/docs/

#### Clone the project

```shell
git clone https://github.com/paulwinex/pw_tile_printing.git
cd pw_tile_printing
```

#### install requirements

```shell
poetry install
```

#### Run

```shell
poetry run ./start.sh
```

### Windows

TODO...


### TODO

- support transparent PNG
- optimize for big images
- autofit tools (image to current pages, to N pages, to viewport)  
- set fixed image size
- save ui options
- add custom page size
- print current page
- page contour over image
- more resize handles
- support Windows
- drag&drop image support
