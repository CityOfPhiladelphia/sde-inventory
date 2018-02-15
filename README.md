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

_recommended_: Do all this in a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

1. Install this repo: `pip install git+git://github.com/CityOfPhiladelphia/sde-inventory.git`
2. Install geopetl: `pip install git+git://github.com/CityOfPhiladelphia/geopetl.git`. You'll also want to install extras for the database you're using
3. Install geopetl extras for the database you'll be using. For example, to inventory an Oracle SDE database: `pip install git+git://github.com/CityOfPhiladelphia/geopetl.git[oracle_sde]`
4. Install requirements: `pip install -r requirements.txt`

## Configuration

Rename `sample.config.yaml` to `config.yaml` and configure as needed.

## Usage

For a summary of commands and options, run `sde_inventory --help`.

### `gis_inventory create [--config/-c <config file>]`

Inventories an SDE database and outputs the contents as JSON to `stdout`. To capture this in a file, use the `>` operator (e.g. `gis_inventory create > inventory.json`).

### `gis_inventory get_changes OLD NEW [--config/-c <config file>]`

Compares two inventory files for changes and logs changes. See `config.yaml` to configure logging.
