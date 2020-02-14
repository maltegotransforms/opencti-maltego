#!/bin/bash

cd mtz
zip -r ../transforms.mtz ./Servers ./TransformRepositories ./TransformSets
cd ../

# Add opencti configuration file next to transforms
cp config.py ./src/transforms/config.py