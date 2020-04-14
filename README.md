# Maltego OpenCTI Transforms

Use the OpenCTI platform in your Maltego application thanks to a set of transforms allowing you to explore the OpenCTI data.

## Installation

```
$ git clone https://github.com/amr-cossi/opencti-maltego
$ cd opencti-maltego
```

### Requirements

Please install the following requirements before generating the Maltego transforms:

- Python >= 3.6
- Libraries in requirements.txt
- Maltego [STIX2 entities](https://github.com/OpenCTI-Platform/maltego-stix2)

> Warning: you have to import [Maltego STIX2](https://github.com/OpenCTI-Platform/maltego-stix2) entities before installing these transforms.

```
$ pip3 install -r requirements.txt
```

On Windows, please execute the following after installing the requirements:

```
$ pip3 uninstall python-magic
$ pip3 install python-magic-bin
```

### Installation

The local OpenCTI transforms are leveraging the Maltego TRX library. The first step is to create the configuration file:

```
$ cp config.py.sample config.py
```

Update the file according to your setup and then execute:

```
$ ./build_transforms.sh
```

If you specified a different path for the `src` directory of thie repository, please copy the content in it:

```
$ cp -a src /path/to/your/project/opencti-maltego/src
```

Finally just import the file `output/transforms.mtz` in Maltego using the "Import config" menu.

## Contributing

### Code of Conduct

We follow a standard [Code of Conduct](CODE_OF_CONDUCT.md) that we expect project participants to adhere to. Please read the [full text](CODE_OF_CONDUCT.md) so that you can understand what actions will and will not be tolerated.

### How to contribute

This module is not a huge project with an intense roadmap. Feel free to contribute through issues linked to pull requests for new features and bug solving.

### TODO: known wanted enhancements

- Implement an "explain inference" transform
- Handle sectors
- Use a less strict sanitize function on entity names (TRX functions ?)
- Handle errors and display messages in Maltego
