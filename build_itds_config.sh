#!/bin/bash
echo "Clear old results"
rm output/itds-config.mtz 2> /dev/null

echo "Create iTDS MTZ package"
# this renaming shuffle is needed because transform names differ slightly between local and remote tranforms
cd mtz
mv ./TransformSets ./TransformSetsBackup
mv ./TransformSetsTDS ./TransformSets
zip -q -x .empty -r ../output/itds-config.mtz ./TransformSets
mv ./TransformSets ./TransformSetsTDS
mv ./TransformSetsBackup ./TransformSets
cd ../

echo "All done. MTZ package can be imported to TDS."
