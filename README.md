# Maltego OpenCTI Transforms

Use the OpenCTI platform in your Maltego application thanks to a set of transforms allowing you to explore the OpenCTI v6 data.

## Installation

```sh
$ git clone https://github.com/MaltegoTech/opencti-maltego.git
$ cd opencti-maltego
```

### Requirements

Please install the following requirements before generating the Maltego transforms:

- Python >= 3.6
- Libraries in requirements.txt
- Maltego [STIX2 entities](https://github.com/maltegotransforms/maltego-stix2) and python package maltego_stix2

> Warning: you have to import [Maltego STIX2](https://github.com/MaltegoTech/maltego-stix2) entities before installing these transforms.

```sh
$ pip3 install -r requirements.txt
```

This repository provides integration between OpenCTI and Maltego using the Maltego TRX library.

## OpenCTI versions

Even if some compatibility exists, each OpenCTI version should be queried with the corresponding pycti version. The Python requirements need to be adapted accordingly.

This repository tries to remain compatible with the latest version of OpenCTI. You can use the tags to run an older version of this integration against an older version of OpenCTI. Some features and bugs are solved in both projects regularly, so these older versions may not work entirely.

Please try pinning the pycti version to the respective OpenCTI version.

Please open an issue for any compatibility problem you may have.

## Installation

The local OpenCTI transforms leverage the Maltego TRX library. The first step is to create the configuration file:

```sh
$ cp config.py.sample config.py
```

Update the file according to your setup and then execute:

## Setting Up the Environment

To ensure a smooth setup and to overcome environment issues, you can use the provided `build_transforms.sh` script. This script will create and activate a virtual environment, set the `PYTHONPATH`, install dependencies, and run the CLI.

### Using build_transforms.sh

1. Make the script executable:

    ```sh
    $ chmod +x build_transforms.sh
    ```

2. Run the script from the root directory of the repository:

    ```sh
    $ ./build_transforms.sh
    ```

The `build_transforms.sh` script includes the following steps:

```bash
#!/bin/bash 
# build_transforms.sh

# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH

# Install dependencies
python3 -m pip install -r trx/gunicorn/requirements.txt

# Run the CLI
python3 cli.py

# Deactivate the virtual environment
deactivate
```

## Importing Transforms

If you use an iTDS, make sure to configure its URL in [./config.py](./config.py), generate specific configuration files by running:

Import the following files in your iTDS management platform:

- `output/config.mtz` for the main configuration.
- `output/settings.csv` for settings.
- `output/transforms_1-6.csv` to `output/transforms_6-6.csv` for transforms, in batches for easier import.

### Output Files

After running the script, the following files will be generated in the `output` directory:

- `local.mtz`: Configuration file to import locally into Maltego.
- `config.mtz`: Configuration file for iTDS.
- `settings.csv`: Settings for iTDS.
- `transforms_1-6.csv` to `transforms_6-6.csv`: Transform CSV files for importing to iTDS in batches.

## Import Local Transforms

To import the local transforms into Maltego, follow these steps:

Import the file `output/local.mtz` in Maltego using the "Import config" menu.

## Importing Transforms into iTDS

To import the transforms into iTDS, follow these steps:

1. Import the file `output/config.mtz` in iTDS using the "Import config" menu.
2. Import the file `output/settings.csv` in iTDS using the "Import settings" menu.
3. Import the files `output/transforms_1-6.csv` to `output/transforms_6-6.csv` in iTDS using the "Import transforms" menu.

Make sure to configure the iTDS URL in the `config.py` file as shown below:

```python
HOST_URL = os.environ.get("HOST_URL", "https://localhost:8088")

opencti_url_setting = TransformSetting('opencti_url', 'OpenCTI URL', setting_type='string', default_value="", popup=True)
opencti_token_setting = TransformSetting('opencti_token', 'OpenCTI Token', setting_type='string', default_value="", popup=True)
ssl_verify_setting = TransformSetting('opencti_ssl_verify', 'SSL Verify', setting_type='boolean', default_value="false", popup=False)
http_proxies_setting = TransformSetting('opencti_http_proxies', 'HTTP Proxies', setting_type='string', optional=True, popup=False)

global_settings = [
    opencti_url_setting,
    opencti_token_setting,
    ssl_verify_setting,
    http_proxies_setting
]

global_registry = TransformRegistry(
    owner='Maltego Technologies GmbH - OpenCTI On-Premise',
    author='Maltego Technologies GmbH - OpenCTI On-Premise',
    host_url=HOST_URL,
    seed_ids=['opencti'],
    global_settings=global_settings
)
```

## Running the Transform Server

The transform server can be run with or without SSL support. By default, it runs without SSL.

### Without SSL

```sh
python project.py runserver --port 8080
```

### With SSL

To run the server with SSL, make sure you have your `cert.pem` and `key.pem` files in the `trx/gunicorn` directory, the folder contains a sample certificate and key file. Then run the following command:

```sh
python project.py runserver --port 8080 --ssl
```

## Contributing

### Code of Conduct

We follow a standard [Code of Conduct](CODE_OF_CONDUCT.md) that we expect project participants to adhere to. Please read the [full text](CODE_OF_CONDUCT.md) so that you can understand what actions will and will not be tolerated.

### How to contribute

This module is not a huge project with an intense roadmap. Feel free to contribute through issues linked to pull requests for new features and bug solving.

### TODO: Known wanted enhancements

- Handle errors and display messages in Maltego
- Add a Maltego machine to generate a knowledge graph from one report
```