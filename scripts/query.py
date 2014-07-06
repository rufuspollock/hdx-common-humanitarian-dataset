import ckanapi

remote = 'http://datahub.io'

ckan = ckanapi.RemoteCKAN(remote)

def query(dataset):
    resource = dataset['resources'][0]
    indicator_resource_id = dataset['resources'][1]['id']
    # cap amount received
    indicator = 'CHD.O.FUN.19.T6'

    examples = [
        'SELECT * FROM "%s" WHERE indicator_id = \'%s\' LIMIT 10;' % (
            resource['id'],
            indicator
            ),
        'SELECT region, indicator_id, period, value, name, units FROM "%s" JOIN "%s" ON indicator_id = id LIMIT 10;' % (
            resource['id'],
            indicator_resource_id
            )
        ]
    for sql in examples:
        print(sql)
        out = ckan.action.datastore_search_sql(sql=sql)
        print(out['records'][0])
        print('=======')

if __name__ == '__main__':
    name = 'hdx-common-humanitarian-dataset'
    dataset = ckan.action.package_show(id=name)
    query(dataset)

