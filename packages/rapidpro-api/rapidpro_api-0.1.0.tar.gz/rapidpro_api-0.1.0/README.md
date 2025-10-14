# RapidPro API Data analysis library 

This is a Python library for interacting with the RapidPro API. This library focuses in extracting data from one or multiple RapidPro workspaces and saving it in ready to analyze datasets from RapidPro workspaces. 

It is thought to be run in data pipelines.



### Installation

pip install rapidpro-api


### Development

First clone the repository:

```bash
git clone https://github.com/unicef/magasin-rapidpro-paquet 
```

Then create a virtual environment and install the dependencies:

```bash
cd rapidpro-api
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]

```

## Running the tests

```bash
pytest
```
To run the tests with coverage, you can use the following command:

```bash
pytest --cov=rapidpro_api
```

To run the tests with coverage and see which lines are missing, you can use the following command:
```bash
pytest --cov=rapidpro_api --cov-report=term-missing
```

## License
Apache2 license. See [LICENSE](LICENSE) for details.
