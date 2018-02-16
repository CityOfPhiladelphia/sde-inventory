import os
import sys
from collections import OrderedDict
from datetime import datetime
import json
import yaml
import logging
import logging.config
import click

def fields_are_equal(a, b):
    """Utility to compare two field attribute dictionaries. Returns True/False.
    """

    types_are_equal = a['db_type'] == b['db_type']
    lengths_are_equal = a['length'] == b['length']

    return (types_are_equal and
            lengths_are_equal)

def indexes_are_equal(a, b):
    """Utility to compare two index attribute dictionaries. Returns True/False."""

    fields_are_equal = set(a['fields']) == set(b['fields'])

    return fields_are_equal

def changes_for_fields(old_fields, new_fields, user, table, timestamp):
    """Utility to compare two field/metadata objects and return changes."""

    # this is a new table? if so, don't do anything.
    if old_fields is None:
        return []

    changes = []

    # loop over old fields
    for old_field, old_field_attrs in old_fields.items():
        try:
            new_field_attrs = new_fields[old_field]

        # handle removed field
        except KeyError:
            changes.append({
                'type':     'REMOVE_FIELD',
                'date':     timestamp,
                'user':     user,
                'table':    table,
                'field':    old_field,
            })
            continue

        # check for updated field
        is_update = not fields_are_equal(old_field_attrs, new_field_attrs)

        if is_update:
            # REVIEW do we want to handle field updates as such, or just
            # as an add-remove? the only obvious consequence is: updates
            # can preserve row data; add-removes can't.
            changes.append({
                'type':     'REMOVE_FIELD',
                'date':     timestamp,
                'user':     user,
                'table':    table,
                'field':    old_field,
                'data':     old_field_attrs,
            })
            changes.append({
                'type':     'ADD_FIELD',
                'date':     timestamp,
                'user':     user,
                'table':    table,
                'field':    old_field,
                'data':     new_field_attrs,
            })

    # loop over new fields
    for new_field, new_field_attrs in new_fields.items():
        # if this is a new table or the field doesn't exist in the old fields
        if new_field not in old_fields:
            changes.append({
                'type':     'ADD_FIELD',
                'date':     timestamp,
                'user':     user,
                'table':    table,
                'field':    new_field,
                'data':     new_field_attrs,
            })

    return changes

def changes_for_privileges(old_privs, new_privs, user, table, timestamp):
    """Utility to compare two lists of privileges for a table and return
    differences."""

    changes = []

    is_new_table = old_privs is None

    if not is_new_table:
        for old_priv in old_privs:
            if old_priv not in new_privs:
                changes.append({
                    'type':     'REMOVE_PRIVILEGE',
                    'date':     timestamp,
                    'user':     user,
                    'table':    table,
                    'data':     old_priv,
                })
                continue

    for new_priv in new_privs:
        if is_new_table or new_priv not in old_privs:
            changes.append({
                'type':     'ADD_PRIVILEGE',
                'date':     timestamp,
                'user':     user,
                'table':    table,
                'data':     new_priv,
            })

    return changes

def changes_for_indexes(old_indexes, new_indexes, user, table, timestamp):
    """Utility to compare two lists of table indexes."""

    changes = []

    is_new_table = old_indexes is None

    if not is_new_table:
        for old_index_name, old_index_attrs in old_indexes.items():
            try:
                new_index_attrs = new_indexes[old_index_name]
            # handle index removes
            except KeyError:
                changes.append({
                    'type':     'REMOVE_INDEX',
                    'date':     timestamp,
                    'user':     user,
                    'table':    table,
                    'data':     old_index_attrs,
                })
                continue

        # get index updates - handling these as add/removes (see note
        # on field updates above)
        if not indexes_are_equal(old_index_attrs, new_index_attrs):
            changes.append({
                'type':     'REMOVE_INDEX',
                'date':     timestamp,
                'user':     user,
                'table':    table,
                'data':     old_index_attrs,
            })
            changes.append({
                'type':     'ADD_INDEX',
                'date':     timestamp,
                'user':     user,
                'table':    table,
                'data':     new_index_attrs
            })

    # loop over new indexes
    for new_index_name, new_index_attrs in new_indexes.items():
        if is_new_table or new_index_name not in old_indexes:
            changes.append({
                'type':     'ADD_INDEX',
                'date':     timestamp,
                'user':     user,
                'table':    table,
                'data':     new_index_attrs,
            })

    return changes

def changes_for_table(old_table_attrs, new_table_attrs, user, table, timestamp):
    """Utility to compare two table attribute dictionaries. Returns list of
    changes as dictionaries."""

    changes = []

    # is this a new table?
    is_new_table = old_table_attrs is None

    # FIELDS
    old_fields = old_table_attrs['fields'] if not is_new_table else None
    new_fields = new_table_attrs['fields']

    field_changes = changes_for_fields(old_fields, new_fields, user, table,
                                       timestamp)
    changes.extend(field_changes)

    # PRIVS
    old_privs = old_table_attrs['privileges'] if not is_new_table else None
    new_privs = new_table_attrs['privileges']

    priv_changes = changes_for_privileges(old_privs, new_privs, user, table, timestamp)
    changes.extend(priv_changes)

    # INDEXES
    old_indexes = old_table_attrs['indexes'] if not is_new_table else None
    new_indexes = new_table_attrs['indexes']

    index_changes = changes_for_indexes(old_indexes, new_indexes, user, table, timestamp)
    changes.extend(index_changes)

    return changes

def changes_for_user(old_tables, new_tables, user, timestamp):
    """Utility to compare two database users and return changes."""

    changes = []

    # is this a new user? we can tell if old_tables exists or not
    is_new_user = old_tables is None

    # if it's an existing user
    if not is_new_user:
        # loop over old tables
        for old_table, old_table_attrs in old_tables.items():
            try:
                new_table_attrs = new_tables[old_table]

                # get changes for the table
                table_changes = changes_for_table(old_table_attrs, new_table_attrs,
                                                       user, old_table, timestamp)
                changes.extend(table_changes)

            # if the old table doens't exist in the new tables
            except KeyError:
                changes.append({
                    'type':     'REMOVE_TABLE',
                    'date':     timestamp,
                    'user':     user,
                    'table':    old_table,
                })

    # loop over tables
    for new_table, new_table_attrs in new_tables.items():
        # if it's a new user or just a new table
        if is_new_user or new_table not in old_tables:
            changes.append({
                'type':         'ADD_TABLE',
                'date':         timestamp,
                'user':         user,
                'table':        new_table,
            })

            # get child changes for the table (privs, indexes, etc.)
            table_changes = changes_for_table(None, new_table_attrs, user,
                                              new_table, timestamp)
            changes.extend(table_changes)

    return changes

def changes_for_inventory(old_users, new_users, timestamp):
    """Utility to compare two snapshots of an inventory and return user add/
    deletes. User adds must also return child changes, e.g. tables, fields,
    indexes."""

    changes = []

    # loop over old users
    for old_user, old_tables in old_users.items():
        try:
            new_tables = new_users[old_user]

            # get table changes for old user who still exists
            user_changes = changes_for_user(old_tables, new_tables, old_user,
                                            timestamp)

            changes.extend(user_changes)

        # if old user not in new users
        except KeyError:
            changes.append({
                'type':     'REMOVE_USER',
                'date':     timestamp,
                'user':     old_user,
            })

    # loop over new users
    for new_user, new_tables in new_users.items():
        try:
            old_tables = old_users[new_user]
        # if new user not in old users
        except KeyError:
            changes.append({
                'type':     'ADD_USER',
                'date':     timestamp,
                'user':     new_user,
            })

            # get child changes for new user (tables, indexes, privs)
            user_changes = changes_for_user(None, new_tables, new_user, timestamp)
            changes.extend(user_changes)

    return changes

@click.command()
@click.argument('old')
@click.argument('new')
@click.option('--config', '-c', default='config.yaml', help='Path to a configuration file')
def get_changes(old, new, config):
    """Compares two inventory snapshots to detect schema changes."""

    # read config
    config_path = config
    with open(config_path, 'r') as config_yaml:
        config = yaml.load(config_yaml).get('get_changes')

    # read and parse both inventories
    old_path = old
    with open(old_path, 'r') as old_file:
        old = json.load(old_file)

    new_path = new
    with open(new_path, 'r') as new_file:
        new = json.load(new_file)
        # get modified time of new inventory. this is what will be used as the
        # timestamp in the change table.
        timestamp_epoch = os.path.getmtime(new_path)
        timestamp = datetime.fromtimestamp(timestamp_epoch)

    changes = changes_for_inventory(old, new, timestamp)

    # set up logging
    logging_config = config['logging']
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger()

    # log changes
    for change in changes:
        logger.info({
            'change_type': change.pop('type'),
            'inventory_time': change.pop('date'),
            'change_data': change,
        })

    sys.stderr.write('Total changes: {}'.format(len(changes)))
