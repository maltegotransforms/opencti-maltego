# Maltego OpenCTI Transforms

Use the OpenCTI platform in your Maltego application thanks to a set of transforms allowing you to explore the OpenCTI data.

## Installation

### Requirements

Please install the following requirements before generating the Maltego transforms:

- Python >= 3.6
- Libraries in requirements.txt
- Import Maltego STIX2 entities

### Installation

The local OpenCTI transforms are leveraging the Maltego TRX library.

- Update the configuration file : config.py
- Run build.sh
- Copy the content of src/ to the execution directory specified in config.py
- Import transforms.mtz

## TODO

- Add a virtual env capability