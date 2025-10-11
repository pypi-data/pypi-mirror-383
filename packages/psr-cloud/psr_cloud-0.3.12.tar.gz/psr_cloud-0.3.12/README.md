# psr.cloud (pycloud) Module

## Installation

### From source (Recommended)

Copy `psr` folder and its contents to your work directory or add its parent path to `PYTHONPATH` environment variable before running it.

### pip

If you have pip installed and the correct git credentials run the command:

```python
pip install git+https://github.com/psrenergy/pycloud.git
```

## Usage

```python
import psr.cloud

client = psr.cloud.Client()

case = psr.cloud.Case(data_path=r"C:\PSR\Sddp17.3\Example\12_stages\Case21",
                      price_optimized=True,
                      program="SDDP",
                      program_version="17.3.7",
                      name="Test PyCloud",
                      execution_type="Default",
                      number_of_processes=64,
                      memory_per_process_ratio="2:1",
                      repository_duration=2 # Normal (1 month)
                      )

client.run_case(case)
```

## Authentication

#### Keyword argument specified in `Client` constructor:

- `username` - specify username string
- `password` - plain password string

```python
client = psr.cloud.Client(username="myuser", password=os.environ["MY_PASSWORD"])
```

The password will never be stored plainly, only its md5 hash will be used.

#### Read from environment variables

Prefered over keyword arguments:

- `PSR_CLOUD_USER` - specify username
- `PSR_CLOUD_PASSWORD_HASH` - md5 password hash

Password hash can be obtained by running the code below:

```python
import psr.cloud as pycloud
pycloud.hash_password("ExamplePassword")
```


#### Automatic

Will use PSR Cloud client auth data, if avaiblable.

## Querying PSR Cloud options

#### Available programs/models

```python
get_programs() -> list[str]
```

#### Available model versions

```python
get_program_versions(program: str) -> dict[int, str]
```

#### Available execution types

```python
get_execution_types(program: str, version: Union[str, int]) -> dict[int, str]
```

#### Available memory per process ratios

```python
get_memory_per_process_ratios() -> list[str]
```

#### Available repository durations

```python
get_repository_durations() -> dict[int, str]
```
