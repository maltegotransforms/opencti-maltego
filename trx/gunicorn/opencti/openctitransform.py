#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pycti import OpenCTIApiClient
from maltego_trx.maltego import *
from maltego_stix2.util import maltego_to_stix2
from opencti.config import local_execution_path, python_path, opencti_config
from opencti.utils import STIX2toOpenCTItype, setLinkLabel
from opencti.addEntities import (
    searchAndAddEntity,
    searchAndAddObservable,
    searchAndAddRelashionship,
    searchAndAddSighting,
    addStixEntity,
)


def opencti_transform(transformName, output, client_msg: MaltegoMsg, response):

    client_msg.Genealogy = [{"Name": "maltego.STIX2." + client_msg.getProperty("type")}]

    stix2_entity = maltego_to_stix2(
        client_msg,
        transform=response,
        allow_custom_types=True,
        allow_custom_fields=True,
        allow_skipping_stix2_coercion=True,
    )

    # Setup OpenCTI client
    opencti_api_client = OpenCTIApiClient(
        opencti_config["url"],
        opencti_config["token"],
        log_level=opencti_config["log_level"],
        ssl_verify=opencti_config["ssl_verify"],
        proxies=opencti_config["proxies"]
    )

    # Search and complete details for the input entity (StixRelation or StixEntity)
    if transformName.startswith("StixRelation"):
        entity = searchAndAddRelashionship(opencti_api_client, response, stix2_entity)
    elif transformName.startswith("StixSighting"):
        entity = searchAndAddSighting(opencti_api_client, response, stix2_entity)
    elif transformName.startswith("StixObservable"):
        entity = searchAndAddObservable(opencti_api_client, response, stix2_entity)
    else:
        entity = searchAndAddEntity(opencti_api_client, response, stix2_entity)

    # If input entity found in OpenCTI, proceed with the transform
    if entity["opencti_entity"]:
        # *ToDetails: Nothing else to do
        if transformName.endswith("ToDetails"):
            pass

        # *ToReports: Find related reports
        elif transformName.endswith("ToReports"):
            reports = opencti_api_client.report.list(
                filters=[
                    {
                        "key": "objectContains",
                        "values": [entity["opencti_entity"]["x_opencti_id"]],
                    }
                ],
                first=opencti_config["limit"],
            )
            for report in reports:
                child_entity = addStixEntity(opencti_api_client, response, report)
                child_entity.reverseLink()

        # *ToAuthoredReports: Find reports with a specific author
        elif transformName.endswith("ToAuthoredReports"):
            reports = opencti_api_client.report.list(
                filters=[
                    {
                        "key": "createdBy",
                        "values": [entity["opencti_entity"]["x_opencti_id"]],
                    }
                ],
                first=opencti_config["limit"],
            )
            for report in reports:
                child_entity = addStixEntity(opencti_api_client, response, report)
                child_entity.reverseLink()

        # *ToNotes: Find related notes
        elif transformName.endswith("ToNotes"):
            notes = opencti_api_client.note.list(
                filters=[
                    {
                        "key": "objectContains",
                        "values": [entity["opencti_entity"]["x_opencti_id"]],
                    }
                ],
                first=opencti_config["limit"],
            )
            for note in notes:
                child_entity = addStixEntity(opencti_api_client, response, note)
                child_entity.reverseLink()

        # *ToOpinions: Find related opinions
        elif transformName.endswith("ToOpinions"):
            opinions = opencti_api_client.opinion.list(
                filters=[
                    {
                        "key": "objectContains",
                        "values": [entity["opencti_entity"]["x_opencti_id"]],
                    }
                ],
                first=opencti_config["limit"],
            )
            for opinion in opinions:
                child_entity = addStixEntity(opencti_api_client, response, opinion)
                child_entity.reverseLink()

        # ContainerToStixDomainEntities: Find and add all entities
        elif transformName in [
            "ReportToStixDomainEntities",
            "NoteToStixDomainEntities",
            "OpinionToStixDomainEntities",
        ]:
            for object_ref in entity["opencti_entity"]["objects"]:
                if "Stix-Domain-Object" in object_ref["parent_types"]:
                    if (
                        not output
                        or STIX2toOpenCTItype(output) == object_ref["entity_type"]
                        or STIX2toOpenCTItype(output) in object_ref["parent_types"]
                        or output.lower() == object_ref["entity_type"].lower()
                    ):
                        child_entity = searchAndAddEntity(
                            opencti_api_client,
                            response,
                            {"id": object_ref["standard_id"]},
                        )
        # ContainerToRelations: Find and add all relations
        elif transformName in [
            "ReportToRelations",
            "NoteToRelations",
            "OpinionToRelations",
        ]:
            output = "stix-core-relationship"
            for object_ref in entity["opencti_entity"]["objects"]:
                if "stix-core-relationship" in object_ref["parent_types"]:
                    child_entity = searchAndAddRelashionship(
                        opencti_api_client,
                        response,
                        {"id": object_ref["standard_id"]},
                    )
        # ContainerToObservable: Find and add all observables
        elif transformName in [
            "ReportToStixObservable",
            "NoteToStixObservable",
            "OpinionToStixObservable",
        ]:
            output = "stix-cyber-observable"
            for object_ref in entity["opencti_entity"]["objects"]:
                if "Stix-Cyber-Observable" in object_ref["parent_types"]:
                    child_entity = searchAndAddObservable(
                        opencti_api_client,
                        response,
                        {"id": object_ref["standard_id"]},
                    )

        # StixDomainEntityTo(Relations|StixDomainEntity)(Inferred)?: Return relations|entities when a relation is found
        elif transformName in [
            "StixDomainEntityToStixDomainEntity",
            # "StixDomainEntityToStixDomainEntityInferred",
            "StixDomainEntityToRelations",
            "StixDomainEntityToSightings",
            # "StixDomainEntityToRelationsInferred",
            "StixRelationToRelations",
            "StixDomainEntityToStixObservable",
            "StixObservableToRelations",
        ]:
            # inferred = "Inferred" in transformName
            stix_relations = []
            if output:
                maltego_type = output
                opencti_type = STIX2toOpenCTItype(output)
                if "ToSightings" in transformName:
                    stix_relations = opencti_api_client.stix_sighting_relationship.list(
                        fromId=entity["opencti_entity"]["x_opencti_id"],
                        toTypes=[opencti_type],
                        # inferred=inferred,
                        first=opencti_config["limit"],
                    )
                    stix_relations += opencti_api_client.stix_sighting_relationship.list(
                        toId=entity["opencti_entity"]["x_opencti_id"],
                        fromTypes=[opencti_type],
                        # inferred=inferred,
                        first=opencti_config["limit"],
                    )
                else:
                    stix_relations = opencti_api_client.stix_core_relationship.list(
                        fromId=entity["opencti_entity"]["x_opencti_id"],
                        toTypes=[opencti_type],
                        # inferred=inferred,
                        first=opencti_config["limit"],
                    )
                    stix_relations += opencti_api_client.stix_core_relationship.list(
                        toId=entity["opencti_entity"]["x_opencti_id"],
                        fromTypes=[opencti_type],
                        # inferred=inferred,
                        first=opencti_config["limit"],
                    )
            else:
                maltego_type = None
                if "ToSightings" in transformName:
                    stix_relations = opencti_api_client.stix_sighting_relationship.list(
                        fromId=entity["opencti_entity"]["x_opencti_id"],
                        # inferred=inferred,
                        first=opencti_config["limit"],
                    )
                    stix_relations += opencti_api_client.stix_sighting_relationship.list(
                        toId=entity["opencti_entity"]["x_opencti_id"],
                        # inferred=inferred,
                        first=opencti_config["limit"],
                    )
                else:
                    stix_relations = opencti_api_client.stix_core_relationship.list(
                        fromId=entity["opencti_entity"]["x_opencti_id"],
                        # inferred=inferred,
                        first=opencti_config["limit"],
                    )
                    stix_relations += opencti_api_client.stix_core_relationship.list(
                        toId=entity["opencti_entity"]["x_opencti_id"],
                        # inferred=inferred,
                        first=opencti_config["limit"],
                    )
            if len(stix_relations) > 0:
                if "ToRelations" in transformName or "ToSightings" in transformName:
                    for relation in stix_relations:
                        reverse_link = False
                        if (
                            relation["to"]["id"]
                            == entity["opencti_entity"]["x_opencti_id"]
                        ):
                            reverse_link = True
                        child_entity = addStixEntity(
                            opencti_api_client, response, relation
                        )
                        # if "inferred" in relation and relation["inferred"]:
                        #    child_entity.setLinkLabel("Inferred")
                        if reverse_link:
                            child_entity.reverseLink()
                else:
                    for relation in stix_relations:
                        if (
                            relation["to"]["standard_id"]
                            == entity["opencti_entity"]["id"]
                        ):
                            reverse_link = True
                            neighbour_data = relation["from"]
                        else:
                            reverse_link = False
                            neighbour_data = relation["to"]
                        if "ToStixObservable" in transformName:
                            neighbour_entity = searchAndAddObservable(
                                opencti_api_client,
                                response,
                                {
                                    "id": neighbour_data["standard_id"],
                                    "type": neighbour_data["entity_type"],
                                },
                            )
                        else:
                            neighbour_entity = searchAndAddEntity(
                                opencti_api_client,
                                response,
                                {
                                    "id": neighbour_data["standard_id"],
                                    "type": neighbour_data["entity_type"],
                                },
                                maltego_type,
                            )
                        if neighbour_entity["maltego_entity"] is not None:
                            setLinkLabel(
                                neighbour_entity["maltego_entity"], relation, True
                            )
                            if reverse_link:
                                neighbour_entity["maltego_entity"].reverseLink()

        # StixRelationToStixDomainEntity: Find and add from and to entities
        elif transformName in [
            "StixRelationToStixDomainEntity",
            "StixSightingToStixDomainEntity",
        ]:
            if (
                "Stix-Cyber-Observable" in entity["opencti_entity"]["from"]["parent_types"]
                or "stix-cyber-observable" in entity["opencti_entity"]["from"]["parent_types"]
            ):
                from_entity = searchAndAddObservable(
                    opencti_api_client,
                    response,
                    {
                        "id": entity["opencti_entity"]["from"]["standard_id"],
                        "type": entity["opencti_entity"]["from"]["entity_type"],
                    },
                )
            else:
                from_entity = searchAndAddEntity(
                    opencti_api_client,
                    response,
                    {
                        "id": entity["opencti_entity"]["from"]["standard_id"],
                        "type": entity["opencti_entity"]["from"]["entity_type"],
                    },
                    output,
                )

            if from_entity["maltego_entity"]:
                from_entity["maltego_entity"].reverseLink()
                setLinkLabel(
                    from_entity["maltego_entity"],
                    entity["opencti_entity"],
                    False,
                )

            if (
                "Stix-Cyber-Observable" in entity["opencti_entity"]["to"]["parent_types"]
                or "stix-cyber-observable" in entity["opencti_entity"]["to"]["parent_types"]
            ):
                to_entity = searchAndAddObservable(
                    opencti_api_client,
                    response,
                    {
                        "id": entity["opencti_entity"]["to"]["standard_id"],
                        "type": entity["opencti_entity"]["to"]["entity_type"],
                    },
                )
            else:
                to_entity = searchAndAddEntity(
                    opencti_api_client,
                    response,
                    {
                        "id": entity["opencti_entity"]["to"]["standard_id"],
                        "type": entity["opencti_entity"]["to"]["entity_type"],
                    },
                    output,
                )
            if to_entity["maltego_entity"]:
                setLinkLabel(
                    to_entity["maltego_entity"],
                    entity["opencti_entity"],
                    False,
                )

        # StixObservableToIndicators: Return indicators
        elif transformName == "StixObservableToIndicators":
            if "indicators" in entity["opencti_entity"]:
                for indicator in entity["opencti_entity"]["indicators"]:
                    neighbour_entity = searchAndAddEntity(
                        opencti_api_client,
                        response,
                        {
                            "id": indicator["id"],
                        },
                        None,
                    )
                    neighbour_entity["maltego_entity"].reverseLink()