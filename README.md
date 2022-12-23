# nyc-taxi-price-prediction
New York Taxi Trip Duration Prediction ML Project


## Prefect Cheatsheet

**Create a task**

```python
from prefect import task, flow, get_run_logger

# my_flow.py
@task
def greet(name: str) -> str:
    """This returns the greeting to the 
    specified name."""
    return f"Hello {name}. Nice to meet ya!"

@task
def respond_to_greeting() -> str:
    logger = get_run_logger()
    logger.info("Log anything here!")
    return "Thank you."

# Build a flow
@flow
def run_flow(name: str):
    greet(name)
    respond_to_greeting()


run_flow(name="Mike")
```

### Run the flow

```console
$ python my_flow.py
```

### Goto the Prefect Dashboard

```console
$ prefect orion start 
```

### Deploy The Flow

* This enables scheduling. You can check the [docs](https://docs.prefect.io/concepts/deployments/?h=deplo) for detailed info.
  
* To get help from the CLI

```console  
$ prefect deployment --help
```

* To `build` a deployment, run

```console  
$ prefect deployment build -n demo_deployment my_deployments.py:run_flow -q test
```

When you run this command, Prefect:

Creates a `run_flow-deployment.yaml` file for your deployment based on your flow code and options.
Uploads your flow files to the configured storage location (local by default).
Submit your deployment to the work queue `test`. The work queue `test` will be created if it doesn't exist.

* To `apply` the deployement from a yaml file, run:

```console  
$ prefect deployment apply run_flow-deployment.yaml
```

* To `build` and `apply` a deployment, run:

```console  
$ prefect deployment build -n <deployment_name> <entry_point>:<flow_func> -q <queue_name> -a
```

#### Note: `entry_point` is the path to the source code containing the flow.

* To start a Prefect `agent`, run:

```console
$ prefect agent start  --work-queue <"work_queue_name">
```

OR 

```console
$ prefect agent start  -q <"work_queue_name">
```

e.g

```console
$ prefect agent start  --work-queue "test"
```

### Clear Prefect database - This will delete all data in orion.db

```console
$ prefect orion database reset
```

### Deploy Prefect Deployments On Infrastructure

`Blocks` and `Processes` are used to store and run the deployed workflows respectively.

* Run deployments locally

```python
# blx.py
from prefect.filesystems import LocalFileSystem
from prefect.infrastructure import Process

# Create block
my_storage_block = LocalFileSystem(basepath="~/my-block")
my_storage_block.save(name="demo-storage-block", overwrite=True)

# Create process
my_process_infra = Process(working_dir="~/work")
my_process_infra.save(name="process-infra", overwrite=True)
```

* Display the `blocks` info. i.e ID, Type, Name, Slug

```console  
$ prefect blocks ls
```

* Deploy a workflow using the `storage block` and `infrastructure block`

```console  
$ prefect deployment build \
-n <name> \
-sb <storage_block_Slug> \
-ib <process_blocks_Slug> \
<entry_point>:<name_off_flow> -a
```

