# LakePipe

**Modern data transfer for cloud data lakes**

LakePipe is a high-performance data pipeline framework for moving data between data lakes and warehouses via object storage. Think of it as **Sqoop for the cloud era** - optimized for modern cloud architectures with vendor-specific bulk loaders.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Why LakePipe?

- **Cloud-native**: Uses object storage (S3/GCS/Azure/OBS) as intermediate layer
- **Fast**: Leverages vendor-optimized bulk loaders (TPT, Snowpipe, BigQuery Storage API)
- **Observable**: Real-time progress, validation, and actionable error messages
- **Flexible**: YAML configs, Python SDK, or CLI - your choice
- **Extensible**: Plugin architecture for sources, targets, and transformations

## Quick Start

### Installation

```bash
pip install lakepipe
```

### Simple Transfer

```yaml
# lakepipe.yml
version: 1.0
name: my_pipeline

source:
  type: hive
  database: my_db
  table: my_table
  partition_by: date

storage:
  type: s3
  bucket: my-bucket
  path: /staging

target:
  type: teradata
  host: td-host
  database: target_db
  table: target_table
  loader: tpt

validation:
  row_count:
    enabled: true
    max_variance: 0.01
```

```bash
lakepipe run lakepipe.yml --params date=2025-01-15
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Examples](examples/)

## Supported Connectors

### Sources
- Hive (beeline)
- PostgreSQL (planned)
- MySQL (planned)
- MongoDB (planned)

### Storage
- S3 (AWS)
- GCS (Google Cloud)
- Azure Blob Storage
- OBS (Huawei Cloud)

### Targets
- Teradata (TPT)
- Snowflake (planned)
- BigQuery (planned)
- Redshift (planned)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by Apache Sqoop, built for the cloud era.

---

**Author**: Md. Rakibul Hasan
**Status**: Alpha - Active Development
