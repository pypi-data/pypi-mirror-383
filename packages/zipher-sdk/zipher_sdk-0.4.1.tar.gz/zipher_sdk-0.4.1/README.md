
# Zipher SDK

The Zipher SDK is a Python library for interacting with Zipher's APIs.

- [Package Installation](#package-installation)
- [Granting access to Zipher](#providing-zipher-with-access-to-databricks-workspace)
- [Usage](#sdk-usage)

## Package Installation

You can install the Zipher SDK using pip:

```bash
pip install zipher-sdk
```

## Providing Zipher with access to Databricks workspace

After installing `zipher-sdk` package a cli tool to automatically create all necessary resources for Zipher is available.

### Setting up credentials

You need to provide credentials that will be used to create all necessary resources and permissions for Zipher.

Here are ways to set up credentials:
* `.databrickscfg` config (cli tool supports profile choice as an argument)
* `ZIPHER_DATABRICKS_HOST` and `ZIPHER_DATABRICKS_TOKEN` or `ZIPHER_DATABRICKS_CLIENT_ID`, `ZIPHER_DATABRICKS_CLIENT_SECRET` environment variables
* providing credentials as arguments to cli tool

### Cli tool usage examples

#### Providing Zipher with access to a list of jobs
```
zipher setup --jobs-list 12345678,87654321,12344321,21436587
```

#### Providing Zipher with access to n jobs from the workspace
```
zipher setup --max-jobs 50
```

#### Providing Zipher with readonly access to a list of jobs
```
zipher setup --readonly --jobs-list 12345678,87654321,12344321,21436587
```

### Full cli tool specification
```
usage: zipher setup [-h] [--workspace-host WORKSPACE_HOST] [--access-token ACCESS_TOKEN] [--client-id CLIENT_ID] [--client-secret CLIENT_SECRET] [--profile PROFILE] [--verbose] [--jobs-list JOBS_LIST] [--max-jobs MAX_JOBS]
                    [--max-runs MAX_RUNS] [--days-back DAYS_BACK] [--readonly] [--pat] [--skip-approval]

options:
  -h, --help            show this help message and exit
  --workspace-host WORKSPACE_HOST
                        Databricks workspace host URL.
  --access-token ACCESS_TOKEN
                        Databricks workspace access token.
  --client-id CLIENT_ID
                        Databricks workspace OAuth client id.
  --client-secret CLIENT_SECRET
                        Databricks workspace OAuth client secret.
  --profile PROFILE     Profile name from .databrickscfg.
  --verbose             Print full error message on fail.
  --jobs-list JOBS_LIST
                        Comma-separated list of jobs ids to provide access to.
  --max-jobs MAX_JOBS   Maximum number of jobs to consider when iterating over jobs to grant permissions (default: 2000).
  --max-runs MAX_RUNS   Maximum number of runs to consider when iterating over runs to grant permissions to relative jobs (default: 2000).
  --days-back DAYS_BACK
                        How many days back to fetch relevant job runs for permission updates (default: 7).
  --readonly            Provide Zipher with only CAN_VIEW permissions on listed jobs. When not provided will default to CAN_MANAGE permissions.
  --pat                 Generate Personal Access Token for Zipher instead of default OAuth client creds.
  --skip-approval       Skip user input approval.

```


## SDK Usage

Here are some basic examples of how you can use the Zipher SDK to optimize your databricks clusters using Zipher's ML-powered optimization engine:

### Update Existing Configuration

You can update an existing configuration by initializing a zipher Client and sending a JSON payload to the `update_existing_conf` function. Here's how you can do it:

```python
from zipher import Client

client = Client(customer_id="my_customer_id")  # assuming the zipher API key is stored in ZIPHER_API_KEY environment variable

# Your existing cluster config:
config_payload = {
    "new_cluster": {
        "autoscale": {
            "min_workers": 1,
            "max_workers": 30
        },
        "cluster_name": "my-cluster",
        "spark_version": "10.4.x-scala2.12",
        "spark_conf": {
            "spark.driver.maxResultSize": "4g"
        },
        "aws_attributes": {
            "first_on_demand": 0,
            "availability": "SPOT",
            "zone_id": "auto",
            "spot_bid_price_percent": 100,
            "ebs_volume_count": 0
        },
        "node_type_id": "rd-fleet.2xlarge",
        "driver_node_type_id": "rd-fleet.xlarge",
        "spark_env_vars": {},
        "enable_elastic_disk": "false"
    }
}

# Update configuration
optimized_cluster = client.update_existing_conf(job_id="my-job-id", existing_conf=config_payload)

# Continue with sending the optimized configuration to Databricks via the Databricks python SDK, Airflow operator, etc.

```

### Update Existing Multiple Tasks Configuration

You can update multiple databricks tasks by initializing a zipher Client and sending a JSON representing a list of dbx SubmitTask objects to
the `get_optimized_tasks` function. 

```python
from zipher import Client

client = Client(customer_id="my_customer_id")  # assuming the zipher API key is stored in ZIPHER_API_KEY environment variable

tasks_to_optimize = [
    {
        "task_key": "task_1",
        "description": "Test notebook task",
        "notebook_task": {
            "notebook_path": "/path/to/your/notebook",
            "base_parameters": {
                "param1": "value1"
            }
        },
        "new_cluster": {
            "spark_version": "14.3.x-scala2.12",
            "node_type_id": "m6id.large",
            "driver_node_type_id": "m6id.large",
            "num_workers": 2,
            "aws_attributes": {
                "first_on_demand": 0,
                "availability": "SPOT",
                "zone_id": "auto",
                "spot_bid_price_percent": 100,
                "ebs_volume_count": 0
            },
            "spark_conf": {
                "spark.driver.maxResultSize": "4g"
            }
        }
    },
    {
        "task_key": "task_2",
        "description": "Test Python task",
        "spark_python_task": {
            "python_file": "/path/to/your/python_file.py",
        },
        "new_cluster": {
            "spark_version": "14.3.x-scala2.12",
            "node_type_id": "m6id.large",
            "driver_node_type_id": "m6id.large",
            "num_workers": 2,
            "spark_conf": {
                "spark.driver.maxResultSize": "4g"
            }
        },
        "timeout_seconds": 3600,
        "depends_on": [
            {
                "task_key": "task_1"
            }
        ]
    }
]

# Update tasks
optimized_tasks = client.get_optimized_tasks(job_id="my-job-id", tasks=tasks_to_optimize)

# Continue with sending the optimized tasks to Databricks via the Databricks python SDK, Airflow operator, etc.
```