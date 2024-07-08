#!/usr/bin/env python3

import argparse
import csv
import logging
import os
import shutil
import subprocess
import sys
import time
import zipfile

from rich.logging import RichHandler

VERSION = "2.0"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)

def install_dependencies():

    result = subprocess.run(
        ['pip', 'install', '-r', 'trx/gunicorn/requirements.txt'],
        stdout=subprocess.DEVNULL,  # Suppress standard output
        stderr=subprocess.PIPE  # Capture standard error
    )
    if result.returncode == 0:
        logging.info("Dependencies installed.")
    else:
        logging.error("An error occurred while installing dependencies.")
        logging.error(result.stderr.decode('utf-8'))


def generate_transforms():
    logging.info("Generating transforms from CSV...")
    input_name = "transforms.csv"
    keys = ["Transform id", "Description", "Input type", "Sets", "Output"]

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
                logging.error("A key is missing, exiting...")
                sys.exit(0)

        output_entities = []
        output = row[d["Output"]] or None
        if o_entity := row[d["Output"]]:
            output_entities = [f"maltego.STIX2.{o_entity}"] if o_entity != "maltego.Unknown" else [o_entity]
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
        transforms += 'from maltego_trx.decorator_registry import TransformSet\n'
        transforms += 'from opencti.openctitransform import opencti_transform\n'
        transforms += 'from opencti.config import global_registry\n\n'
        transforms += 'from requests.exceptions import RequestException\n\n'

        transforms += f'@global_registry.register_transform(\n'
        transforms += f'    display_name="{t_data["displayName"]}",\n'
        transforms += f'    input_entity="{t_data["inputEntity"]}",\n'
        transforms += f'    description="{t_data["description"]}",\n'
        transforms += f'    output_entities={t_data["outputEntities"]},\n'
        transforms += f'    transform_set=TransformSet(name="{t_data["transformSets"]}", description="{t_data["transformSets"]}")\n'
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

    logging.info("Transforms generated successfully.")


def setup_directories():
    logging.info("Setting up directories...")
    os.makedirs("mtz/Servers/", exist_ok=True)
    os.makedirs("mtz/TransformSets/", exist_ok=True)
    os.makedirs("mtz/TransformRepositories/Local/", exist_ok=True)
    os.makedirs("output/", exist_ok=True)
    logging.info("Directories setup completed.")


def clean_old_results():
    logging.info("Cleaning old results...")
    for root, dirs, files in os.walk("./trx/gunicorn/transforms"):
        for file in files:
            if file.startswith("opencti"):
                os.remove(os.path.join(root, file))
    if os.path.exists("trx/gunicorn/opencti/config.py"):
        os.remove("trx/gunicorn/opencti/config.py")
    for path in ["mtz", "output"]:
        if os.path.exists(path):
            shutil.rmtree(path)
    setup_directories()
    logging.info("Old results cleaned.")


def copy_config():
    logging.info("Copying config file...")
    # os.makedirs("./trx/gunicorn/opencti/", exist_ok=True)
    config_path = "config.py"

    if not os.path.exists(config_path):
        logging.info("Config file not found.")
        logging.info(
            "Copying sample config file to ./trx/gunicorn/opencti/config.py please update it with your configuration.")
        shutil.copy("config.py.sample", "./trx/gunicorn/opencti/config.py")
    else:
        shutil.copy(config_path, "./trx/gunicorn/opencti/config.py")
    logging.info("Config file copied.")


def create_mtz_package():
    logging.info("Creating MTZ package...")
    result = subprocess.run(["python3", "trx/gunicorn/project.py", "--generate-config"], capture_output=True)

    if result.returncode != 0:
        logging.error("Failed to generate config: %s", result.stderr.decode())
        return

    max_wait_time = 300
    start_time = time.time()

    while not os.path.exists("output/local.mtz"):
        if time.time() - start_time > max_wait_time:
            logging.error("Timed out waiting for output/local.mtz to be created")
            return
        time.sleep(1)

    with zipfile.ZipFile("output/local.mtz", 'r') as zip_ref:
        zip_ref.extractall("mtz")
    shutil.rmtree("mtz/TransformRepositories")
    shutil.rmtree("mtz/Servers")
    shutil.copy("stix2_entities.mtz.sample", "mtz/stix2_entities.mtz")
    with zipfile.ZipFile("mtz/stix2_entities.mtz", 'r') as zip_ref:
        zip_ref.extractall("mtz")
    os.remove("mtz/stix2_entities.mtz")
    with zipfile.ZipFile("output/config.mtz", 'w') as zipf:
        for root, dirs, files in os.walk("mtz"):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, "mtz"))
    logging.info("MTZ package created and extracted successfully.")


def main():
    clean_old_results()
    copy_config()
    install_dependencies()
    generate_transforms()
    create_mtz_package()
    logging.info(
        "All done. MTZ packages can be imported in Maltego and don't forget to copy ./trx/gunicorn/ at the execution "
        "path provided in the configuration.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CLI tool for managing transforms and MTZ packages.")
    parser.add_argument('--clean', action='store_true', help="Clean old results and setup directories.")
    parser.add_argument('--copy-config', action='store_true', help="Copy the config.py file.")
    parser.add_argument('--all', action='store_true', help="Run all steps in sequence.")

    args = parser.parse_args()

    if args.clean or args.copy_config:
        if args.clean:
            clean_old_results()
        if args.copy_config:
            copy_config()
    else:
        main()
