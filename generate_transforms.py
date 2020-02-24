#!/usr/bin/env python3

import csv
import sys
import os
from config import *

input_name = sys.argv[1]
keys = [
    "Transform id",
    "Description",
    "Input type",
    "Sets",
    "Output"
]

t_template = ""
with open("./templates/template.transform","r") as i:
    t_template = i.read()

ts_template = ""
with open("./templates/template.transformsettings","r") as i:
    ts_template = i.read()

s_template = ""
with open("./templates/template.tas","r") as i:
    s_template = i.read()

set_template = ""
with open("./templates/template.set","r") as i:
    set_template = i.read()

csv_content = []
with open(input_name) as csvfile:
    r = csv.reader(csvfile, delimiter=",", quotechar="'")
    for line in r:
        csv_content.append(line)

transforms = ""
transforms_sets = {}

for row in csv_content[1:]:
    d = {}
    for key in keys:
    	if csv_content[0].index(key)>=0:
    		d[key] = csv_content[0].index(key)
    	else:
    		print("A key is missing, exiting...")
    		sys.exit(0)

    t_data = {
        "transformName": row[d["Transform id"]],
        "description": row[d["Description"]],
        "input_type": row[d["Input type"]]
    }
    t_output = t_template.format(**t_data)
    with open("./mtz/TransformRepositories/Local/"+row[d["Transform id"]]+".transform","w") as o:
        o.write(t_output)

    if row[d["Sets"]] != "":
        sets = row[d["Sets"]].split(",")
        for cset in sets:
            if cset not in transforms_sets:
                transforms_sets[cset] = []
            transforms_sets[cset].append(row[d["Transform id"]])

    options = ""
    if row[d["Output"]] != "":
        options = " --output " + row[d["Output"]]

    ts_data = {
        "python_path": python_path,
        "local_execution_path": local_execution_path,
        "transform_name": row[d["Transform id"]].split(".")[-1],
        "options": options
    }
    ts_output = ts_template.format(**ts_data)
    with open("./mtz/TransformRepositories/Local/"+row[d["Transform id"]]+".transformsettings","w") as o:
        o.write(ts_output)

    transforms += "      <Transform name=\""+row[d["Transform id"]]+"\"/>\n"

s_data = {
    "transforms": transforms[:-1]
}
s_output = s_template.format(**s_data)
with open("./mtz/Servers/"+"Local.tas","w") as o:
    o.write(s_output)

for cset, ctransforms in transforms_sets.items():
    set_data = {
        "transformSetName": cset,
        "transforms": "\n".join(list(map(lambda r: "      <Transform name=\""+r+"\"/>" , ctransforms)))      
    }
    set_output = set_template.format(**set_data)
    with open("./mtz/TransformSets/"+cset.lower().replace(' ', '').replace(':', '')+".set","w") as o:
        o.write(set_output)