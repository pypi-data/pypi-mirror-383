<p align="center">
  <img src="builder-ui/public/logo.png" alt="Polymo" width="220">
</p>

<p align="center">
    <em>Turn REST APIs into Spark DataFrames with just a YAML file
</em>
</p>

<p align="center">
  <a href="https://github.com/dan1elt0m/polymo/actions/workflows/test.yml"><img alt="test" src="https://github.com/dan1elt0m/polymo/actions/workflows/test.yml/badge.svg"></a>
  <a href="https://github.com/dan1elt0m/polymo/actions/workflows/gh-pages.yml"><img alt="docs" src="https://github.com/dan1elt0m/polymo/actions/workflows/gh-pages.yml/badge.svg"></a>
  <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/polymo">
  <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/polymo">
  <img alt="License BSD 3" src="https://img.shields.io/badge/license-BSD--3--Clause-blue?style=flat-square">
</p>

# Welcome to Polymo

Polymo makes it super easy to ingest APIs with Pyspark. You only need to define a YAML file or a Pydantic config.

My vision is that API ingestion doesn't need heavy, third party tools or hard to maintain custom code.
The heck, you don't even need Pyspark skills.


<!-- Centered clickable screenshot -->
<p align="center">
  <a href="docs/ui.png">
    <img src="docs/ui.png" alt="Polymo Builder UI - connector preview screen" width="860">
  </a>
</p>

## How does it work?

Define a config file manually or use the recommended, lightweight builder UI. 
Once you are happy with your config, all you need to do is register the Polymo reader and tell Spark where to find the config:

```python
from pyspark.sql import SparkSession
from polymo import ApiReader

spark = SparkSession.builder.getOrCreate()
spark.dataSource.register(ApiReader)

df = (
    spark.read.format("polymo")
    .option("config_path", "./config.yml")  # YAML you saved from the Builder
    .option("token", "YOUR_TOKEN")  # Only if the API needs one
    .load()
)

df.show()
```
Streaming works too:
```python
spark.readStream.format("polymo")
```

Prefer everything in the code? Build the config with PolymoConfig model.
```python
from pyspark.sql import SparkSession
from polymo import ApiReader, PolymoConfig

spark = SparkSession.builder.getOrCreate()
spark.dataSource.register(ApiReader)

jp_posts = PolymoConfig(
    base_url="https://jsonplaceholder.typicode.com",
    path="/posts",
)

df = (
    spark.read.format("polymo")
    .option("config_json", jp_posts.config_json())
    .load()
)
df.show()
```

Does it perform? Polymo can read in batches (pages in parallel) and therefore is much faster than row based solutions like UDFs.

## How to start?
Locally you probably want to install polymo along with the Builder UI: 

```bash
pip install "polymo[builder]"
```

This comes with all UI deps such as pyspark

Running Polymo on a spark cluster usually doesn't require these UI deps.
In that case, just install the bare minimum deps with
```bash
pip install polymo
```

## Launch the builder UI 

```bash 
polymo builder
```

#### (Optional) Run the Builder in Docker

```bash
docker compose up --build builder
```

- The service listens on port `8000`; open <http://localhost:8000> once Uvicorn reports it is running.

## Where to Next
Read the docs [here](https://dan1elt0m.github.io/polymo/)

## Contributing
It's still early days, but Polymo already supports a lot of features!
Is there something missing? Raise an issue or contribute!

Contributions and early feedback welcome!
