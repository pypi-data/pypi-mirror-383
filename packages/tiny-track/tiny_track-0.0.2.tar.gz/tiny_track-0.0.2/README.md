# tiny-track

A minimalist, MLFlow-compatible, header-only C++ experiment tracking library with Python bindings.


## Usage

Logging via Python API:

```python
from ttrack.ttrack_cpp import LocalLogger, get_experiments

# start run
logger = LocalLogger(
    logging_dir='mlruns',                  # set your logging dir name (default used by mlflow is "mlruns")
    experiment_name='My experiment name',  # set your experiment name
    run_name='My run name',                # set your run name
    source=__file__,
)

# add tags
logger.add_tag(key='myTagName', value='myTagValue')

# add params
logger.log_param(key='myParamName', value='myParamValue')

# log metrics
for i in range(10):
    logger.log_metric(key='myMetric', value=i**2, step=i+1)
```
