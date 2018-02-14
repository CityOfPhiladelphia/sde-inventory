import os
import sys
from datetime import datetime
import json
import yaml
import click
from geopetl.oracle_sde import OracleSdeDatabase

def filter_names(names=[], include=[], exclude=[]):
    """Utility to filter a list of names (strings). Multiple include tokens
    are treated as OR conditions."""
    include_names = []

    remaining_include_candidates = names

    for include_token in include:
        for name in remaining_include_candidates:
            if include_token in name:
                include_names.append(name)
                remaining_include_candidates.remove(name)

    out_names = []

    for exclude_token in exclude:
        for name in include_names:
            if exclude_token not in name:
                out_names.append(name)

    return out_names

@click.command()
@click.option('--config', '-c', default='config.yaml', help='Path to a configuration file')
@click.option('--debug', '-d', is_flag=True, help='Run on a subset of data with verbose logging')
def create(config, debug):
    """Creates an inventory (snapshot) of all objects in an SDE database. This
    includes tables, fields, privileges, and indexes. Outputs to stdout by
    default, or pickles to a file if an --output flag was specified."""

    start = datetime.now()

    # read config
    config_path = config
    with open(config_path, 'r') as config_yaml:
        config = yaml.load(config_yaml).get('create')

    # get the gis db connection string
    # TODO handle arg
    dsn = config.get('sde', {}).get('db')

    # connect to the db
    # TODO make this work with databases other than oracle
    db = OracleSdeDatabase(dsn)

    # get all users
    db_users = db.users

    # filter users if there are include/exclude options
    users_config = config.get('users', {})
    include = users_config.get('include')
    exclude = users_config.get('exclude')
    users = filter_names(names=db_users, include=include, exclude=exclude)

    # debug: work on subset
    if debug: users = users[:1]

    # this is the big inventory map: users => tables => fields, privs, indexes, etc.
    inventory = {}

    # loop over gis users
    for user in users:
        if debug: sys.stderr.write('\n** {} **\n'.format(user))

        # this is a map of tables for the user => table details
        user_tables = {}

        # get tables names for user
        table_names = db.tables_for_user(user)

        # prepend table names with the user (e.g. CASES => GIS_311.CASES)
        table_names = ['.'.join([user, x]) for x in table_names]

        # wrap tables in a nice, friendly geopetl table object
        tables = [db.table(x) for x in table_names]

        # debug: work on subset
        if debug: tables = tables[:2]

        # loop over tables
        for table in tables:
            # this is where the fields, privs, and indexes will go
            table_details = {}

            # get fields and process
            metadata_items = table.metadata.items()
            fields = {}

            for field_name, field_attrs in metadata_items:
                # uppercase field name
                field_name = field_name.upper()

                # suppress geopetl field types
                field_attrs.pop('type')

                # TODO add a field that concatenates the db type and length?

                fields[field_name] = field_attrs

            table_details['fields'] = fields

            # get other table attributes
            table_details['privileges'] = table.privileges
            table_details['indexes'] = table.indexes
            table_details['row_count'] = table.count
            table_details['sde_type'] = table.sde_type
            table_details['srid'] = table.srid

            # add it to the inventory
            user_tables[table.name] = table_details

        # add to inventory
        inventory[user] = user_tables

    # output
    inventory_string = json.dumps(inventory, indent=2, sort_keys=True)
    sys.stdout.write(inventory_string)

    if debug: sys.stderr.write('\nFinished. Took {} seconds.'.format(datetime.now() - start))
