# Maltego OpenCTI Transforms

Use the OpenCTI platform in your Maltego application thanks to a set of transforms allowing you to explore the OpenCTI v4 data.

## Installation

```
$ git clone https://github.com/amr-cossi/opencti-maltego
$ cd opencti-maltego
```

### Requirements

Please install the following requirements before generating the Maltego transforms:

- Python >= 3.6
- Libraries in requirements.txt
- Maltego [STIX2 entities](https://github.com/amr-cossi/maltego-stix2) and python package maltego_stix2

> Warning: you have to import [Maltego STIX2](https://github.com/amr-cossi/maltego-stix2) entities before installing these transforms.

```
$ pip3 install -r requirements.txt
```

On Windows, please execute the following after installing the requirements:

```
$ pip3 uninstall python-magic
$ pip3 install python-magic-bin
```

#### OpenCTI versions

Even if some compatibility exists, each OpenCTI version should be queried with the corresponding pycti version. The Python requirements need to be adapted accordingly.  

This repository tries to remain compatible with the lastest version of OpenCTI.  You can use the tags to run an older version of this integration against an older version of OpenCTI. Some features and bugs are solved in both projects regularly so these older versions may not work entirely.  

Please open an issue for any compatibility problem you may have.  

### Installation

The local OpenCTI transforms are leveraging the Maltego TRX library. The first step is to create the configuration file:

```
$ cp config.py.sample config.py
```

Update the file according to your setup and then execute:

```
$ ./build_transforms.sh
```

To run the transforms locally, make sure the path to TRX `project.py` is set up in [./config.py](./config.py)

Finally just import the file `output/transforms.mtz` in Maltego using the "Import config" menu.

If you use an iTDS, make sure to configure its URL in [./config.py](./config.py), generate specific configuration files:

```
$ ./build_itds_config.sh
```

And import the file `output/importable_itds_config.csv` in your iTDS management platform as well as the `output/itds-config.mtz`.

You can also optionally build this config including the STIX 2 Entities. A version of these, current as of April 20, 2021, 
is included in the stix2_entities.mtz.sample file. You may want to refer the [Maltego STIX2 entities](https://github.com/amr-cossi/maltego-stix2)
repository and rebuild them to make sure you are including the latest version (replace the included sample file with your new build).

To build the iTDS config including the STIX Entities:

```
$ ./build_itds_config_with_stix2.sh
```

## Contributing

### Code of Conduct

We follow a standard [Code of Conduct](CODE_OF_CONDUCT.md) that we expect project participants to adhere to. Please read the [full text](CODE_OF_CONDUCT.md) so that you can understand what actions will and will not be tolerated.

### How to contribute

This module is not a huge project with an intense roadmap. Feel free to contribute through issues linked to pull requests for new features and bug solving.

### TODO: known wanted enhancements

- Handle errors and display messages in Maltego
- Add a Maltego machine to generate a knowledge graph from one report