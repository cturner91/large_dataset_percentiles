# large_dataset_percentiles

Testing the performance of different methods of calculating percentiles on massive datasets.

## Getting started

### Loading data

Use the management command to pre-load data: `python manage.py load_data --value --indexed_value --count=10_000_000 --func=random`
* `--count` is how many rows to create in the database
* `--value` and `--indexed_value` define which models to load data for. 
  * Both are very simple single-field models, one indexed and the other not.
  * Must specify models using flags, command will not asume either by default.
* `--func` is the function to use to create the random values. 
  * Supports `random` and `normal` by default. 
  * Customizable via `FUNCS` variable in the management script. 

### Calculating percentiles

Once the data has been loaded, different techniques can be used by accessing the `/api/percentile/` endpoint. this endpoint accepts some arguments:
* `percentile` - int. The percentile to calculate, in range 0-100.
* `model` - str. Either `ValueEntry` or `IndexedValueEntry`. 
* `method` - str. Either `1` or `2` by default. Can add new techniques in `views.py`.

The response contains the calculated percentile and the amount of time taken to calculate them, plus other debug info.

## Results

