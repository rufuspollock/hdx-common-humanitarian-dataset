import os
import csv
import json

import ckanapi

remote = 'http://datahub.io'
APIKey = 'XXXXX'

ckan = None

# #########################
# Objects to create in CKAN

dataset = {
    'name': 'hdx-common-humanitarian-dataset',
    'title': 'Common Humanitarian Dataset',
    # change this your preferred org
    'owner_org': 'rufuspollock',
    'resources': []
}
resources = [
    {
        'name': 'value',
        'title': 'Indicator Values',
        # not needed but for us locally
        'path': 'data/value.csv',
        'schema': {
            'fields': [
                {'id': 'dataset_id', 'type': 'text'},
                {'id': 'region', 'type': 'text'},
                {'id': 'indicator_id', 'type': 'text'},
                {'id': 'period', 'type': 'int'},
                {'id': 'value', 'type': 'float'}
            ]
        },
        # empty url as just stored in datastore
        # we are running against v2.1 so we can't create resource when doing
        # datastore_create (see below)
        'url': 'empty',
        'url_type': 'datastore'
    },
    {
        'name': 'indicator',
        'title': 'Indicators List',
        # not needed but for us locally
        'path': 'data/indicator.csv',
        'schema': {
            'fields': [
                    {'id': 'id', 'type': 'text'},
                    {'id': 'name', 'type': 'text'},
                    {'id': 'units', 'type': 'text'}
                ],
            'primary_key': 'id'
        },
    }
]

# #########################
# Code

def create_dataset(overwrite=True):
    exists = False
    try:
        out = ckan.action.package_show(id=dataset['name'])
        # already exists
        exists = True
    except ckanapi.errors.NotFound:
        pass

    for r in resources:
        ckanresource = {
            'name': r['name'],
            'description': r['title'],
            # empty url as just stored in datastore
            # we are running against v2.1 so we can't create resource when doing
            # datastore_create (see below)
            'url': 'empty',
            'url_type': 'datastore'
            }
        dataset['resources'].append(ckanresource)

    if not exists:
        ckan.action.package_create(**dataset)

    if overwrite and exists:
        ckan.action.package_update(**dataset)

    # load the data so we get stuff like resource_id
    created = ckan.action.package_show(id=dataset['name'])
    return created

# note due to this bug https://github.com/ckan/ckan/pull/1652 prior to to ckan
# v2.2.1 you'll need to create the resource first (as we have done)
# ckan.action.datastore_create(package_id=dataset['name'], resource=resources[0])
# as datahub uses ckan v2.1 atm we have to explicitly create the resource
def upload_data_to_datastore(ckan_resource_id, resource):
    # let's delete any existing data before we upload again
    try:
        ckan.action.datastore_delete(resource_id=ckan_resource_id)
    except:
        pass

    ckan.action.datastore_create(
            resource_id=ckan_resource_id,
            fields=resource['schema']['fields'],
            primary_key=resource['schema'].get('primary_key'))

    reader = csv.DictReader(open(resource['path']))
    rows = [ row for row in reader ]
    chunksize = 10000
    offset = 0
    print('Uploading data for file: %s' % resource['path'])
    while offset < len(rows):
        rowset = rows[offset:offset+chunksize]
        ckan.action.datastore_upsert(
                resource_id=ckan_resource_id,
                method='insert',
                records=rowset)
        offset += chunksize
        print('Done: %s' % offset)


import sys
if __name__ == '__main__':
    if len(sys.argv) <= 2:
        usage = '''python scripts/upload.py {ckan-instance} {api-key}

e.g.

python scripts/upload.py http://datahub.io/ MY-API-KEY
'''
        print(usage)
        sys.exit(1)

    remote = sys.argv[1]
    apikey = sys.argv[2]
    ckan = ckanapi.RemoteCKAN(remote, apikey=apikey)

    created = create_dataset(overwrite=False)
    for idx, resource in enumerate(created['resources']):
        upload_data_to_datastore(resource['id'], resources[idx])

