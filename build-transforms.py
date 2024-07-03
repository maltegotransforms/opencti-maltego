#!/usr/bin/env python3


VERSION = "2.0"


def generate():
    import csv
    input_name = "transforms.csv"
    keys = ["Transform id", "Description", "Input type", "Sets", "Output"]

    csv_content = []
    with open(input_name) as csvfile:
        r = csv.reader(csvfile, delimiter=",", quotechar="'")
        for line in r:
            csv_content.append(line)

    import csv
    import sys

    csv_content = []
    with open(input_name) as csvfile:
        r = csv.reader(csvfile, delimiter=",", quotechar="'")
        for line in r:
            csv_content.append(line)
    transforms = ""
    for row in csv_content[1:]:
        d = {}
        for key in keys:
            if csv_content[0].index(key) >= 0:
                d[key] = csv_content[0].index(key)
            else:
                print("A key is missing, exiting...")
                sys.exit(0)

        output_entities = []
        output = row[d["Output"]] or None
        if o_entity := row[d["Output"]]:

            output_entities=  [f"maltego.STIX2.{o_entity}"] if o_entity != "maltego.Unknown" else [o_entity]
        elif row[d["Sets"]] == "To Details [OpenCTI]":
            output_entities = [row[d["Input type"]]]

        transformName = row[d["Transform id"]].split(".")[-1]
        t_data = {
            "transformName": transformName,
            "functionName": row[d["Transform id"]].replace(".", "").replace("-", "").replace("_", ""),
            "displayName": row[d["Description"]].replace("OpenCTI: ", ""),
            "inputEntity": row[d["Input type"]],
            "description": row[d["Description"]],
            "transformSets": row[d["Sets"]],
            "outputEntities": output_entities,
        }

        transform_function = t_data["functionName"]

        transforms += 'import logging\n'
        transforms += 'from maltego_trx.maltego import MaltegoMsg, UIM_PARTIAL\n'
        transforms += 'from maltego_trx.transform import DiscoverableTransform\n'
        transforms += 'from trx.gunicorn.opencti.openctitransform import opencti_transform\n'
        transforms += 'from trx.gunicorn.extensions import global_registry\n\n'
        transforms += 'from requests.exceptions import RequestException\n\n'

        transforms += f'@global_registry.register_transform(\n'
        transforms += f'    display_name="{t_data["displayName"]}",\n'
        transforms += f'    input_entity="{t_data["inputEntity"]}",\n'
        transforms += f'    description="{t_data["description"]}",\n'
        transforms += f'    output_entities={t_data["outputEntities"]},\n'
        transforms += f'    transform_set="{t_data["transformSets"]}"\n'
        transforms += f')\n'
        transforms += f'class {transform_function}(DiscoverableTransform):\n'
        transforms += f'    @classmethod\n'
        transforms += f'    def create_entities(cls, request: MaltegoMsg, response):\n'
        transforms += '        try:\n'
        transforms += f'           opencti_transform("{t_data["transformName"]}", "{output}", request, response)\n'
        transforms += '        except RequestException as error:\n'
        transforms += '            message = "An error occurred during the request to the OpenCTI server."\n'
        transforms += '            if "Max retries exceeded with url" in str(error) and "Operation timed out" in str(error):\n'
        transforms += '                message = "Connection to the OpenCTI server timed out."\n'
        transforms += '            logging.error(f"{message}: {error}", exc_info=error)\n'
        transforms += '            response.addUIMessage(message, UIM_PARTIAL)\n'

        with open(f"./trx/gunicorn/transforms/{transform_function}.py", "w") as o:
            o.write(transforms)

        transforms = ""


if __name__ == '__main__':
    generate()
