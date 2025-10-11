# Apache Airflow Provider for Anomalo
A set of native Airflow operators for [Anomalo](https://www.anomalo.com/)

### Requirements

python >=3.9.0
airflow >=2.8.0


### Installation


```
pip install apache-airflow-providers-anomalo
```
You can validate that it is correctly installed by running `airflow providers list` on the command line and seeing if `apache-airflow-providers-anomalo` is a listed providers package.

### Airflow Setup

From the airflow UI, go to Admin > Connections and hit the `+` button at the top to add a new connection.

From the "Connection Type" drop down, select "Anomalo".
![connection](https://github.com/anomalo-hq/anomalo-airflow-provider/blob/main/docs/connection.png?raw=True)
Then fill in the fields for "Connection Id" (`anomalo-default` is the default connection id), "Host", and "API Secret Token".

## Usage

1. Obtain Anomalo table name from GUI. For example
   ![table](https://github.com/anomalo-hq/anomalo-airflow-provider/blob/main/docs/table.png?raw=True)
   would be `public-bq.covid19_nyt.us_counties`

2. This package includes 3 different operators. You can find documentation for them on the operator code itself.
   1. Run checks Operator: `airflow.providers.anomalo.operators.anomalo.AnomaloRunCheckOperator`
   2. Job Sensor `airflow.providers.anomalo.sensors.anomalo.AnomaloJobCompleteSensor`
   3. Validate table checks: `airflow.providers.anomalo.operators.anomalo.AnomaloPassFailOperator`

3. See `example_anomalo.py` for usage example

## Releasing to PyPi

To release a new version to PyPi, you will need to

1. Configure your pypi token by running:
   ```poetry config pypi-token.pypi [token here]```
   The token can be found in the AWS secrets manager
2. Bump the version number in pyproject.toml. Make sure that this change is committed.
3. run
   ```poetry publish --build```

