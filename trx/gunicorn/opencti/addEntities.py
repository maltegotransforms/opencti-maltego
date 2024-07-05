#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pycti.utils.constants import IdentityTypes
from maltego_stix2.util import stix2_to_maltego
from opencti.utils import STIX2toOpenCTItype, addDisplayInfo
import re

# OpenCTI marking types to be shown on each entity in Maltego
format_config = {
	"marking_color": "TLP",
	"marking_text": None
}

def formatMarkings(markingDefinitions):
    color = ""
    min_order_color = 99999
    text = ""
    min_order_text = 99999
    for r in markingDefinitions:
        if (
            format_config["marking_color"]
            and r["definition_type"] == format_config["marking_color"]
            and r["x_opencti_order"] < min_order_color
        ):
            color = r["x_opencti_color"]
            min_order_color = r["x_opencti_order"]
        if (
            format_config["marking_text"]
            and r["definition_type"] == format_config["marking_text"]
            and r["x_opencti_order"] < min_order_text
        ):
            text = r["definition"]
            min_order_text = r["x_opencti_order"]
    return (color, text)


def addStixEntity(opencti_api_client, response, opencti_entity):
    # PreHandle identities
    if opencti_entity["standard_id"].startswith("identity--"):
        identity_class = opencti_entity["entity_type"].lower()

    # PreHandle Observables
    observable = False
    if "Stix-Cyber-Observable" in opencti_entity["parent_types"]:
        observable = True

    # Generate Stix2-almost-compliant dict
    clean_opencti_entity = opencti_api_client.stix2.generate_export(opencti_entity)

    # Handle relationships
    if clean_opencti_entity["id"].startswith("relationship--"):
        clean_opencti_entity["relationship_type"] = clean_opencti_entity["type"]
        clean_opencti_entity["type"] = "relationship"
    if "from" in clean_opencti_entity:
        clean_opencti_entity["source_ref"] = clean_opencti_entity["from"]["standard_id"]
        del clean_opencti_entity["from"]
    if "to" in clean_opencti_entity:
        clean_opencti_entity["target_ref"] = clean_opencti_entity["to"]["standard_id"]
        del clean_opencti_entity["to"]

    # Handle sightings
    if clean_opencti_entity["id"].startswith("sighting--"):
        clean_opencti_entity["type"] = "sighting"
        clean_opencti_entity["count"] = "attribute_count"
        del clean_opencti_entity["attribute_count"]
        clean_opencti_entity["sighting_of_ref"] = clean_opencti_entity["source_ref"]
        del clean_opencti_entity["source_ref"]
        clean_opencti_entity["observed_data_refs"] = [
            clean_opencti_entity["target_ref"]
        ]
        del clean_opencti_entity["target_ref"]

    # Handle identities
    if clean_opencti_entity["id"].startswith("identity--"):
        clean_opencti_entity["identity_class"] = identity_class

    # Handle notes
    if clean_opencti_entity["id"].startswith("note--"):
        clean_opencti_entity["abstract"] = clean_opencti_entity["attribute_abstract"]
        del clean_opencti_entity["attribute_abstract"]

    # Handle Observables
    if observable:
        if clean_opencti_entity["id"].startswith("file--"):
            clean_opencti_entity["type"] = "file"
        if "defanged" in clean_opencti_entity:
            clean_opencti_entity["is_defanged"] = clean_opencti_entity["defanged"]
            del clean_opencti_entity["defanged"]
        if (
            "value" not in clean_opencti_entity
            and "observable_value" in clean_opencti_entity
            and clean_opencti_entity["type"] in ["x-opencti-hostname"]
        ):
            clean_opencti_entity["value"] = clean_opencti_entity["observable_value"]
        if (
            "name" in opencti_entity
            and opencti_entity["name"] is None
            and "observable_value" in clean_opencti_entity
        ):
            clean_opencti_entity["name"] = clean_opencti_entity["observable_value"]
        to_be_removed = [
            "indicators",
            "indicatorsIds",
            "labels",
            "createdBy",
            "createdById",
            "observable_value",
        ]
        for k in list(clean_opencti_entity.keys()):
            if (
                k.startswith("x_opencti_") and k != "x_opencti_aliases"
            ) or k in to_be_removed:
                clean_opencti_entity.pop(k)

    # Handle general refs
    to_be_removed = [
        "createdById",
        "objectMarkingIds",
        "objectsIds",
        "importFiles",
        "importFilesIds",
    ]
    if "objectMarking" in opencti_entity:
        (color, text) = formatMarkings(opencti_entity["objectMarking"])
        clean_opencti_entity["x_maltego_marking_color"] = color
        clean_opencti_entity["x_maltego_marking_text"] = text
    if "createdBy" in clean_opencti_entity:
        clean_opencti_entity["created_by_ref"] = clean_opencti_entity["createdBy"][
            "standard_id"
        ]
        del clean_opencti_entity["createdBy"]
    if "objectMarking" in clean_opencti_entity:
        clean_opencti_entity["object_marking_refs"] = [
            r["standard_id"] for r in clean_opencti_entity["objectMarking"]
        ]
        del clean_opencti_entity["objectMarking"]
    if "objects" in clean_opencti_entity:
        clean_opencti_entity["object_refs"] = [
            r["standard_id"]
            for r in clean_opencti_entity["objects"]
            if "standard_id" in r
        ]
        del clean_opencti_entity["objects"]
    for k in list(clean_opencti_entity.keys()):
        if (
            k.startswith("x_opencti_") and k != "x_opencti_aliases"
        ) or k in to_be_removed:
            clean_opencti_entity.pop(k)

    maltego_entity = stix2_to_maltego(clean_opencti_entity)
    response.entities.append(maltego_entity)
    addDisplayInfo(maltego_entity, opencti_api_client.api_url)
    return maltego_entity


def plainSearchAndAddEntities(opencti_api_client, response, search_value, limit=500):
    opencti_observable_entities = opencti_api_client.stix_cyber_observable.list(
        search=search_value, first=limit
    )
    opencti_domain_entities = opencti_api_client.stix_domain_object.list(
        search=search_value, first=limit
    )
    res = []
    for opencti_entity in opencti_observable_entities + opencti_domain_entities:
        maltego_entity = addStixEntity(opencti_api_client, response, opencti_entity)
        res.append({"opencti_entity": opencti_entity, "maltego_entity": maltego_entity})

    return res


def searchAndAddEntity(opencti_api_client, response, stix_entity, output=None):
    types = [STIX2toOpenCTItype(stix_entity["type"]) if "type" in stix_entity else None]
    stix_id = stix_entity["id"] if "id" in stix_entity else None
    stix_name = stix_entity["name"] if "name" in stix_entity else None
    stix_type = stix_entity["type"] if "type" in stix_entity else None
    opencti_entity = None
    maltego_entity = None

    # Enrich API answer with more attributes
    custom_attributes = re.sub(
        r"\.\.\. on Basic(Object|Relationship) {\n(\s+)id\n(\s+)}",
        r"... on Basic\g<1> {\n\g<2>id\n\g<2>standard_id\n\g<2>entity_type\n\g<2>parent_types\n\g<3>}",
        opencti_api_client.stix_domain_object.properties,
    )

    if (
        not output
        or STIX2toOpenCTItype(output) == stix_type
        or (output == "identity" and IdentityTypes.has_value(stix_type))
    ):
        # Search for entity in OpenCTI based on STIX id or (type, name)
        opencti_entity = opencti_api_client.stix_domain_object.get_by_stix_id_or_name(
            types=types,
            stix_id=stix_id,
            name=stix_name,
            customAttributes=custom_attributes,
        )
        if opencti_entity:
            maltego_entity = addStixEntity(opencti_api_client, response, opencti_entity)
    else:
        # Search for entity in OpenCTI based on STIX id
        opencti_entity = opencti_api_client.stix_domain_object.get_by_stix_id_or_name(
            stix_id=stix_id,
            customAttributes=custom_attributes,
        )
        # Then filter on type
        if opencti_entity and opencti_entity["entity_type"] == STIX2toOpenCTItype(
            output
        ):
            maltego_entity = addStixEntity(opencti_api_client, response, opencti_entity)

    return {"opencti_entity": opencti_entity, "maltego_entity": maltego_entity}


def searchAndAddObservable(opencti_api_client, response, stix_entity):
    opencti_entity = None
    maltego_entity = None

    stix_id = stix_entity["id"] if "id" in stix_entity else None
    stix_value = (
        stix_entity["value"]
        if "value" in stix_entity
        else (stix_entity["name"] if "name" in stix_entity else None)
    )

    if stix_id is not None:
        opencti_entity = opencti_api_client.stix_cyber_observable.read(id=stix_id)

    elif stix_value is not None:
        opencti_entities = opencti_api_client.stix_cyber_observable.list(
            search=stix_value
        )
        # Filter results to only keep exact matches
        opencti_entities = [
            opencti_entity
            for opencti_entity in opencti_entities
            if opencti_entity["observable_value"] == stix_value
        ]
        if len(opencti_entities) > 0:
            # Only add the first match
            opencti_entity = opencti_entities[0]

    if opencti_entity:
        maltego_entity = addStixEntity(opencti_api_client, response, opencti_entity)

    return {"opencti_entity": opencti_entity, "maltego_entity": maltego_entity}


def searchAndAddRelationship(
    opencti_api_client, response, stix_entity, stix_type="Relationship", output=None
):
    stix_id = stix_entity["id"] if "id" in stix_entity else None
    opencti_entity = None
    maltego_entity = None

    if not output or output == stix_type:
        opencti_entity = opencti_api_client.stix_core_relationship.read(id=stix_id)

        if opencti_entity:
            maltego_entity = addStixEntity(opencti_api_client, response, opencti_entity)

    return {"opencti_entity": opencti_entity, "maltego_entity": maltego_entity}


def searchAndAddSighting(
    opencti_api_client, response, stix_entity, stix_type="Sighting", output=None
):
    stix_id = stix_entity["id"] if "id" in stix_entity else None
    opencti_entity = None
    maltego_entity = None

    if not output or output == stix_type:
        # Search for entity in OpenCTI based on STIX id or (type, name)
        opencti_entity = opencti_api_client.stix_sighting_relationship.read(id=stix_id)

        if opencti_entity:
            maltego_entity = addStixEntity(opencti_api_client, response, opencti_entity)

    return {"opencti_entity": opencti_entity, "maltego_entity": maltego_entity}
