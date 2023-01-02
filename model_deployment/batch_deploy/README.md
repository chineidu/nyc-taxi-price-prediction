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

* To `build` a deployment using CLI, run

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
