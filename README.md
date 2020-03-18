# Maltego OpenCTI Transforms

Use the OpenCTI platform in your Maltego application thanks to a set of transforms allowing you to explore the OpenCTI data.

## Installation

```
$ git clone https://github.com/amr-cossi/OpenCTI-Maltego
$ cd OpenCTI-Maltego
$ git submodule init
```

### Requirements

Please install the following requirements before generating the Maltego transforms:

- Python >= 3.6
- Libraries in requirements.txt

```
$ pip3 install -r requirements.txt
```

On Windows, please execute the following after installing the requirements:

```
$ pip3 uninstall python-magic
$ pip3 install python-magic-bin
```

> Warning: you have to import Maltego STIX2 entities before installing these transforms.

### Installation

The local OpenCTI transforms are leveraging the Maltego TRX library. The first step is to create the configuration file:

```
$ cp config.yml.sample config.yml
```

Update the file according to your setup and then execute:

```
$ ./build.sh
```

If you specified a different path for the `src` directory of thie repository, please copy the content in it:

```
$ cp -a src /path/to/your/project/OpenCTI-Maltego/src
```

Finally just import the file `output/transforms.mtz` in Maltego using the "Import config" menu.

## TODO

- Add a virtual env capability