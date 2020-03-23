#!/bin/bash

echo "Clear old results"
rm output/transforms.mtz 2> /dev/null
rm -R mtz/Servers/* mtz/TransformSets/* mtz/TransformRepositories/Local/* 2> /dev/null
mkdir mtz/ 2> /dev/null
mkdir mtz/Servers/
mkdir mtz/TransformSets/
mkdir mtz/TransformRepositories/
mkdir mtz/TransformRepositories/Local/
mkdir output/ 2> /dev/null

echo "Generate Maltego transforms config"
python3 generate_transforms.py transforms.csv

echo "Create MTZ package"
cd mtz
zip -q -x .empty -r ../output/transforms.mtz ./Servers ./TransformRepositories ./TransformSets
cd ../

# Add opencti configuration file next to transforms
echo "Copy config.py in ./src"
cp config.py ./src/config.py

echo "All done"
