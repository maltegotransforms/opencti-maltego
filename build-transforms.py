#!/usr/bin/env python3

import csv
import sys
import os
from config import *

VERSION = "2.0"


def row_to_itds_row(row, transform_function_name):
    description = row["description"]
    ui_name = description.split(":")[1].strip()
    ui_name = f"{ui_name} [OpenCTI]"
    input_type = row["input_type"]
    host = trx_server_host
    if host.endswith("/"):
        host = host[:-1]

    return {
        "Owner": "ANSSI",
        "Author": "Maltego, ANSSI",
        "Disclaimer": "",
        "Description": description,
        "Version": VERSION,
        "Name": transform_function_name,
        "UIName": ui_name,
        "URL": f"{host}/run/{transform_function_name}",
        "entityName": input_type,
        "oAuthSettingId": "",
        "transformSettingIDs": "OpenCTIURL;OpenCTIToken;SSLVerify;HTTPProxies",
        "seedIDs": itds_seed_name,
    }



input_name = sys.argv[1]
keys = ["Transform id", "Description", "Input type", "Sets", "Output"]

t_template = ""
with open("./templates/template.transform", "r") as i:
    t_template = i.read()

ts_template = ""
with open("./templates/template.transformsettings", "r") as i:
    ts_template = i.read()

s_template = ""
with open("./templates/template.tas", "r") as i:
    s_template = i.read()

set_template = ""
with open("./templates/template.set", "r") as i:
    set_template = i.read()

python_template_file = ""
with open("./templates/transform.py", "r") as i:
    python_template_file = i.read()

csv_content = []
with open(input_name) as csvfile:
    r = csv.reader(csvfile, delimiter=",", quotechar="'")
    for line in r:
        csv_content.append(line)

transforms = ""
transforms_sets = {}
itds_transforms_rows = []

for row in csv_content[1:]:
    d = {}
    for key in keys:
        if csv_content[0].index(key) >= 0:
            d[key] = csv_content[0].index(key)
        else:
            print("A key is missing, exiting...")
            sys.exit(0)

    t_data = {
        "transformName": row[d["Transform id"]],
        "description": row[d["Description"]],
        "input_type": row[d["Input type"]],
    }
    t_output = t_template.format(**t_data)
    with open(
        "./mtz/TransformRepositories/Local/" + row[d["Transform id"]] + ".transform",
        "w",
    ) as o:
        o.write(t_output)

    if row[d["Sets"]] != "":
        sets = row[d["Sets"]].split(",")
        for cset in sets:
            if cset not in transforms_sets:
                transforms_sets[cset] = []
            transforms_sets[cset].append(row[d["Transform id"]])

    transform_function = row[d["Transform id"]].replace(".","").replace("-","").replace("_","")

    itds_row = row_to_itds_row(t_data, transform_function)
    itds_transforms_rows.append(itds_row)

    ts_data = {
        "python_path": python_path,
        "local_execution_path": local_execution_path,
        "transform_function": transform_function,
    }
    ts_output = ts_template.format(**ts_data)
    with open(
        "./mtz/TransformRepositories/Local/"
        + row[d["Transform id"]]
        + ".transformsettings",
        "w",
    ) as o:
        o.write(ts_output)

    transforms += '      <Transform name="' + row[d["Transform id"]] + '"/>\n'

    with open("./trx/gunicorn/transforms/" + transform_function + ".py", "w") as o:
        o.write(python_template_file.format(
            functionName=transform_function,
            transformName=row[d["Transform id"]].split(".")[-1],
            output=('"' + row[d["Output"]] + '"') if row[d["Output"]] != "" else 'None'
        ))

s_data = {"transforms": transforms[:-1]}
s_output = s_template.format(**s_data)
with open("./mtz/Servers/" + "Local.tas", "w") as o:
    o.write(s_output)

for cset, ctransforms in transforms_sets.items():
    set_data = {
        "transformSetName": cset,
        "transforms": "\n".join(
            list(map(lambda r: '      <Transform name="' + r + '"/>', ctransforms))
        ),
    }
    set_output = set_template.format(**set_data)
    with open(
        "./mtz/TransformSets/"
        + cset.lower().replace(" ", "").replace(":", "")
        + ".set",
        "w",
    ) as o:
        o.write(set_output)

    tds_set_data = {
        "transformSetName": cset,
        "transforms": "\n".join(
            list(map(lambda r: '      <Transform name="paterva.v2.' + r.replace(".","").replace("-","").replace("_","") + '"/>', ctransforms))
        ),
    }
    tds_set_output = set_template.format(**tds_set_data)

    with open(
        "./mtz/TransformSetsTDS/"
        + cset.lower().replace(" ", "").replace(":", "")
        + ".set",
        "w",
    ) as o:
        o.write(tds_set_output)

if itds_transforms_rows:
    with open("output/importable_itds_config.csv", "w") as outf:
        writer = csv.DictWriter(
            outf, fieldnames=list(itds_transforms_rows[0].keys()), delimiter=",", quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        for data in itds_transforms_rows:
            writer.writerow(data)
