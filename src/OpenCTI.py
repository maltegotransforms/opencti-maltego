#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## TODO
# Support adding for all STIX2 entities
# Orient relationship transforms with new 3.0.2 parameter
# Handle errors and messages

import argparse
from pycti import OpenCTIApiClient
from maltego_trx.maltego import *
from maltego_trx.entities import *
from entities import *
from config import local_execution_path, python_path, opencti_config
from utils import sanitize, STIX2toOpenCTItype
from addEntities import (
    searchAndAddEntity,
    searchAndAddRelashionship,
    addRelationship,
    addReport,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OpenCTI-Maltego transforms")
    parser.add_argument(
        "--transform", dest="transformName", type=str, help="The transform to run"
    )
    parser.add_argument(
        "--output",
        dest="output",
        type=str,
        default=None,
        help="To restrict output entity types",
    )

    args, unknown = parser.parse_known_args()

    # print(unknown)

    if len(unknown) > 0:
        # Create Maltego transgorm object
        transform = MaltegoTransform()

        # Parse Maltego input parameters
        client_msg = MaltegoMsg(LocalArgs=unknown)

        # Extract input entity parameters
        input_value = client_msg.Value
        input_id = (
            client_msg.getProperty("id") if client_msg.getProperty("id") else None
        )
        input_type = (
            client_msg.getProperty("type") if client_msg.getProperty("type") else None
        )
        input_name = (
            client_msg.getProperty("name") if client_msg.getProperty("name") else None
        )

        # Setup OpenCTI client
        opencti_api_client = OpenCTIApiClient(
            opencti_config["url"],
            opencti_config["token"],
            opencti_config["log_level"],
            opencti_config["ssl_verify"],
        )

        # Search and complete details for the input entity (StixRelation or StixEntity)
        if args.transformName.startswith("StixRelation"):
            entity = searchAndAddRelashionship(opencti_api_client, transform, input_id)
        else:
            entity = searchAndAddEntity(
                opencti_api_client, transform, input_id, input_type, input_name
            )

        # If input entity found in OpenCTI, proceed with the transform
        if entity["opencti_entity"]:
            # *ToDetails: Nothing else to do
            if args.transformName.endswith("ToDetails"):
                pass

            # *ToReports: Find related reports
            elif args.transformName.endswith("ToReports"):
                reports = opencti_api_client.report.list(
                    filters=[
                        {
                            "key": "knowledgeContains",
                            "values": [entity["opencti_entity"]["id"]],
                        }
                    ]
                )
                for report in reports:
                    child_entity = addReport(transform, report)
                    child_entity.reverseLink()

            # ReportToStixDomainEntities: Find and add all entities
            elif args.transformName == "ReportToStixDomainEntities":
                for object_ref in entity["opencti_entity"]["objectRefs"]:
                    child_entity = searchAndAddEntity(
                        opencti_api_client,
                        transform,
                        object_ref["id"],
                        object_ref["entity_type"],
                        None,
                        args.output,
                    )

            # StixDomainEntityTo(Relations|StixDomainEntity)(Inferred)?: Return relations|entities when a relation is found
            elif args.transformName in [
                "StixDomainEntityToStixDomainEntity",
                "StixDomainEntityToStixDomainEntityInferred",
                "StixDomainEntityToRelations",
                "StixDomainEntityToRelationsInferred",
                "StixRelationToRelations",
            ]:
                inferred = "Inferred" in args.transformName
                stix_relations = []
                if args.output:
                    stix_relations = opencti_api_client.stix_relation.list(
                        fromId=entity["opencti_entity"]["id"],
                        toTypes=[STIX2toOpenCTItype(args.output)],
                        inferred=inferred,
                        forceNatural=True
                    )
                else:
                    stix_relations = opencti_api_client.stix_relation.list(
                        fromId=entity["opencti_entity"]["id"], inferred=inferred, forceNatural=True
                    )
                if len(stix_relations) > 0:
                    if "Relations" in args.transformName:
                        for relation in stix_relations:
                            reverse_link = False
                            if relation["to"]["id"] == entity["opencti_entity"]["id"]:
                                reverse_link = True
                            child_entity = addRelationship(transform, relation)
                            if "inferred" in relation and relation["inferred"]:
                                child_entity.setLinkLabel("Inferred")
                            if reverse_link:
                                child_entity.reverseLink()
                    else:
                        for relation in stix_relations:
                            if relation["to"]["id"] == entity["opencti_entity"]["id"]:
                                reverse_link = True
                                neighbour_data = relation["from"]
                            else:
                                reverse_link = False
                                neighbour_data = relation["to"]
                            neighbour_entity = searchAndAddEntity(
                                opencti_api_client,
                                transform,
                                neighbour_data["stix_id_key"],
                                neighbour_data["entity_type"],
                                None,
                                args.output,
                            )

                            neighbour_entity["maltego_entity"].setLinkLabel(
                                "Inferred\n"
                                if "inferred" in relation and relation["inferred"]
                                else ""
                                + relation["relationship_type"]
                                + "\n"
                                + (
                                    relation["first_seen"][0:10]
                                    if len(relation["first_seen"]) > 9
                                    else ""
                                )
                                + "\n"
                                + (
                                    relation["last_seen"][0:10]
                                    if len(relation["last_seen"]) > 9
                                    else ""
                                )
                            )

                            if reverse_link:
                                neighbour_entity["maltego_entity"].reverseLink()

            # StixRelationToStixDomainEntity: Find and add from and to entities
            elif args.transformName == "StixRelationToStixDomainEntity":
                # TODO: implement reverse link with parameter introduced in pycti 3.0.2
                from_entity = searchAndAddEntity(
                    opencti_api_client,
                    transform,
                    entity["opencti_entity"]["from"]["stix_id_key"],
                    entity["opencti_entity"]["from"]["entity_type"],
                    None,
                    args.output,
                )
                from_entity["maltego_entity"].reverseLink()

                to_entity = searchAndAddEntity(
                    opencti_api_client,
                    transform,
                    entity["opencti_entity"]["to"]["stix_id_key"],
                    entity["opencti_entity"]["to"]["entity_type"],
                    None,
                    args.output,
                )

                if (
                    "inferred" in entity["opencti_entity"]
                    and entity["opencti_entity"]["inferred"]
                ):
                    from_entity.setLinkLabel("Inferred")
                    to_entity.setLinkLabel("Inferred")

        # Output Maltego XML result
        print(transform.returnOutput())
