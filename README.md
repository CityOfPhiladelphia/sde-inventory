# sde-inventory

A command-line utility for snapshotting the schema of an ArcSDE geodatabase and detecting changes. Generally speaking, this covers:
- users
- tables
  - fields
  - privileges
  - indexes
  - spatial reference ID
  - SDE type (e.g. Feature Class, Mosaic Dataset)
  - row count

## Installation

_optional, but recommended_: Do all this in a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

1. Install this repo: `pip install git+git://github.com/CityOfPhiladelphia/sde-inventory.git`
2. Install geopetl: `pip install git+git://github.com/CityOfPhiladelphia/geopetl.git`
3. Install requirements: `pip install -r requirements.txt`

## Configuration

See `sample.config.yaml` for available options.

## Usage

For a summary of commands and options, run `sde_inventory --help`.

### `create [--config/-c <config file>]`

Inventories an SDE database and outputs the contents as JSON to `stdout`.

### `get_changes OLD NEW [--config/-c <config file>]`

Compares two inventory files for changes and logs changes. See `config.yaml` to configure logging.
