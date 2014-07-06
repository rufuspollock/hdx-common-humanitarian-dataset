HDX Common Humanitarian Dataset CKAN DataStore. This data is derived from that
at <https://github.com/luiscape/data-for-frog> with some tidying. In addition
scripts are provided for loading into a CKAN DataStore.

## Live Example

We've loaded this data into the DataHub.io CKAN instance:

<http://datahub.io/dataset/hdx-common-humanitarian-dataset>

Example DataStore queries against this data can be found in `scripts/query.py`. To run them (and see the output) do:

    python scripts/query.py

## Loading the Data into your CKAN instance

We've prepared a script `upload.py` to do this automatically.

The script will:

1. Create a dataset including 2 resources (one for values and one for indicators)
2. Upload all the data into the DataStore tables for those 2 resources

To run it do:

    python scripts/upload.py CKAN-INSTANCE-URL API-KEY

## Data

Data is in `data/` directory. 2 files:

* `value.csv`: complete set of values (minor tweaking - see below)
* `indicator.csv`: set of indicators (minor tweaking - see below)

## Data Preparation

Ultimately needed to do some prep work on the data to get denormalized file.
Working off `denorm_table.csv` from
<https://github.com/luiscape/data-for-frog/tree/master/frog_data/csv> (once that
appeared).

See `clean.py` for processing done.

* Remove all but first 5 columns going from 90Mb to 16Mb (drop
  `is_number,source,indicator_name,units,last_updated,last_scraped,source_name`)
    * there are ~844 rows where is_number is false in denorm data but all the
  values look to be numeric.
* clean up bad years so period is always a year
  * changed 2005-2006 to 2005
  * changed 1989/P1Y to 1989
  * changed 2014-06-15 to 2014 (one indicator only and date was always the
    same)
* updated field names (lowercased and expanded)

Also discovered that indicator list has 2 ids which are duplicated:

```
"CHD.O.PRO.01.T6","Number of IDPs","Count"
"CHD.O.PRO.02.T6","Number of People in Camps","Count"
"CHD.O.PRO.01.T6","Number of People of Concern by Country of Origin","People"
"CHD.O.PRO.02.T6","Number of People of Concern by Country of Residence","People"
```

And then what looks like a clear typo resulting in a duplicated id:

```
"CHD.O.PRO.03.T6","Internally displaced by Country of Residence","People"
"CHD.O.PRO.03.T6","Internally displaced by Country of Origin","People"
"CHD.O.PRO.05.T6","Returned IDPs by Country of Origin","People"
```

This is obviously a problem and before loading we had to fix this. We did this by changing IDs:

```
"CHD.O.PRO.01.T6","Number of IDPs" => CHD.O.HUM.04.T6
"CHD.O.PRO.02.T6","Number of People in Camps" => CHD.O.HUM.05.T6
```

And:

```
"CHD.O.PRO.03.T6","Internally displaced by Country of Origin" => CHD.O.PRO.04.T6
```

### Asides

Initially we'd looked to work with the value.csv but it seems this includes a
whole bunch of of non-numeric values (like wikipedia links and country names).
I'd have thought all indicator values would be numeric (at least those we use
for visualization purposes) plus this creates problems for the DB because we
would have to set value field to string which limits querying in various ways.

We therefore spent time creating our own cleaned version but once
`denorm_table.csv` appeared that was better to use.

