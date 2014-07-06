# clean up denorm_table.csv in https://github.com/luiscape/data-for-frog/tree/master/frog_data/csv
# and output it to data/value.csv

import csv

reader = csv.reader(open('frog_data/csv/denorm_table.csv'))
rows = [ row for row in reader ]
writer = csv.writer(open('data/value.csv', 'w'))

# fix up duplicate indicator id issue

# format: indicator_id, indicator_name, new_indicator_id
toupdate = [
    'CHD.O.PRO.01.T6','Number of IDPs','CHD.O.HUM.04.T6'
    'CHD.O.PRO.02.T6','Number of People in Camps','CHD.O.HUM.04.T6'
    'CHD.O.PRO.03.T6','Internally displaced by Country of Origin', 'CHD.O.PRO.04.T6'
    ]
for row in rows[1:]:
    indicator_id = row[1]
    indicator_name = row[7]
    for tmp in toupdate:
        if indicator_id == tmp[0] and indicator_name == tmp[1]:
            row[1] = toupdate[2]

# take first 5 columns
# dropping is_number,source,indicator_name,units,last_updated,last_scraped,source_name
rows = zip(*zip(*rows)[:5])
# previous operation changed lists to tuples so change them back
rows = [ list(row) for row in rows ]

headers = ['dataset_id', 'indicator_id', 'region', 'period', 'value']
rows[0] = headers

# fix up period field
# 2005-2006 => 2005
# athena-api,CHD.B.NUT.13.T6,HTI,2005-2006,5.1
# emdat,CHD.O.PRO.01.T6,NER,1989/P1Y,356.0
# worldaerodata,CHD.B.HTH.11.T6,NRU,2014-06-15,1.0
for row in rows[1:]:
    period = row[3]
    if period == '2014-06-15':
        row[3] = '2014'
    elif '-' in period:
        row[3] = period.split('-')[0]
    elif '/' in period:
        row[3] = period.split('/')[0]

writer.writerows(rows)

