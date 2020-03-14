#!/bin/bash

python3 generate_transforms.py transforms.csv

cd mtz
zip -r ../transforms.mtz ./Servers ./TransformRepositories ./TransformSets
cd ../

# Add opencti configuration file next to transforms
cp config.py ./src/config.py
