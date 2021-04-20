#!/bin/bash
echo "Clear old results"
rm output/itds-config-with-stix2.mtz 2> /dev/null

echo "Create iTDS MTZ package"
# this renaming shuffle is needed because transform names differ slightly between local and remote tranforms
cp stix2_entities.mtz.sample mtz/stix2_entities.mtz
cd mtz
unzip -o stix2_entities.mtz  && rm stix2_entities.mtz
mv ./TransformSets ./TransformSetsBackup
mv ./TransformSetsTDS ./TransformSets
zip -q -x .empty -r ../output/itds-config-with-stix2.mtz ./TransformSets ./Entities ./EntityCategories ./Icons
mv ./TransformSets ./TransformSetsTDS
mv ./TransformSetsBackup ./TransformSets
cd ../

echo "All done. MTZ package can be imported to TDS."
