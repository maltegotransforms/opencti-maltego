#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
from functools import lru_cache

from pycti import OpenCTIApiClient
from maltego_trx.maltego import *
from maltego_stix2.util import maltego_to_stix2
from opencti.config import (
    local_execution_path,
    python_path,
    opencti_config,
    max_client_sessions,
)
from opencti.utils import STIX2toOpenCTItype, setLinkLabel, addDisplayInfo
from opencti.addEntities import (
    searchAndAddEntity,
    searchAndAddObservable,
    searchAndAddRelationship,
    searchAndAddSighting,
    addStixEntity,
    plainSearchAndAddEntities,
)
import re

from opencti.config import opencti_token_setting, opencti_url_setting, ssl_verify_setting, http_proxies_setting

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

@lru_cache(maxsize=max_client_sessions)
def get_client(opencti_url, opencti_token, ssl_verify, http_proxies):
    client = OpenCTIApiClient(
        opencti_url,
        opencti_token,
        log_level=opencti_config["log_level"],
        ssl_verify=ssl_verify,
        proxies=http_proxies,
    )
    return client


class hashabledict(dict):  # Thanks https://stackoverflow.com/a/1151705
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def opencti_transform(transformName, output, client_msg: MaltegoMsg, response):
    limit = client_msg.Slider if client_msg.Slider != 100 else opencti_config["limit"]
    limit = (
        5000 if limit > 5000 else limit
    )  # Max number of results in API without pagination

    opencti_url = client_msg.TransformSettings.get(opencti_url_setting.name) or opencti_config["url"]
    opencti_token = client_msg.TransformSettings.get(opencti_token_setting.name) or opencti_config["token"]
    ssl_verify = False

    http_proxies = client_msg.TransformSettings.get(http_proxies_setting.name)

    if not http_proxies and "proxies" in opencti_config and opencti_config["proxies"]:
        http_proxies = opencti_config["proxies"]

    if "SSLVerify" in client_msg.TransformSettings:
        ssl_verify = client_msg.TransformSettings["SSLVerify"] == "true"

    if opencti_url:
        opencti_url = opencti_url.rstrip('/')
    else:
        response.addUIMessage("Please enter a valid API URL", UIM_PARTIAL)
        return
    if not opencti_token:
        response.addUIMessage("Please enter a valid token", UIM_PARTIAL)
        return

    http_proxies = http_proxies or {}

    # Setup OpenCTI client
    opencti_api_client: OpenCTIApiClient
    try:
        opencti_api_client = get_client(opencti_url, opencti_token, ssl_verify, hashabledict(http_proxies))
    except ValueError as error:
        message = f"OpenCTI API Client Error: {error}"
        if str(error) == "OpenCTI API is not reachable. Waiting for OpenCTI API to start or check your configuration...":
            message = f"[{opencti_url}] - {error}"
        log.error(message,exc_info=message)
        response.addUIMessage(message, UIM_PARTIAL)
        return



    entity = None
    if transformName == "PlainSearch":
        plainSearchAndAddEntities(
            opencti_api_client, response, search_value=client_msg.Value, limit=limit
        )
    else:
        if getattr(client_msg, "Genealogy", None) is None:
            client_msg.Genealogy = [
                {"Name": "maltego.STIX2." + client_msg.getProperty("type")}
            ]
        stix2_entity = maltego_to_stix2(
            client_msg,
            transform=response,
            allow_custom_types=True,
            allow_custom_fields=True,
            allow_skipping_stix2_coercion=True,
        )
        # Search and complete details for the input entity (StixRelation or StixEntity)
        if transformName.startswith("StixRelation"):
            entity = searchAndAddRelationship(
                opencti_api_client, response, stix2_entity
            )
        elif transformName.startswith("StixSighting"):
            entity = searchAndAddSighting(opencti_api_client, response, stix2_entity)
        elif transformName.startswith("StixObservable"):
            entity = searchAndAddObservable(opencti_api_client, response, stix2_entity)
        else:
            entity = searchAndAddEntity(opencti_api_client, response, stix2_entity)

    # If input entity found in OpenCTI, proceed with the transform
    if entity is not None and entity["opencti_entity"]:

        # *ToDetails or PlainObservableSearch: Nothing else to do
        if transformName.endswith("ToDetails"):
            pass

        # *ToContainer
        elif (
            transformName.endswith("ToReports")
            or transformName.endswith("ToNotes")
            or transformName.endswith("ToOpinions")
            or transformName.endswith("ToAuthoredReports")
        ):
            opencti_class = None
            if transformName.endswith("Reports"):
                opencti_class = opencti_api_client.report
            elif transformName.endswith("Notes"):
                opencti_class = opencti_api_client.note
            elif transformName.endswith("Opinions"):
                opencti_class = opencti_api_client.opinion
            containers = opencti_class.list(
                filters=[
                    {
                        "key": "createdBy"
                        if "Authored" in transformName
                        else "objectContains",
                        "values": [entity["opencti_entity"]["x_opencti_id"]],
                    }
                ],
                first=limit
            )
            for container in containers:
                child_entity = addStixEntity(opencti_api_client, response, container)
                child_entity.reverseLink()

        # ContainerTo*
        elif (
            transformName.startswith("ReportTo")
            or transformName.startswith("NoteTo")
            or transformName.startswith("OpinionTo")
        ):
            opencti_class = None
            if transformName.startswith("ReportTo"):
                opencti_class = opencti_api_client.report
            elif transformName.startswith("NoteTo"):
                opencti_class = opencti_api_client.note
            elif transformName.startswith("OpinionTo"):
                opencti_class = opencti_api_client.opinion

            custom_attributes = None
            if "ToRelations" in transformName:
                custom_attributes = (
                    'objects(types: ["stix-core-relationship"]) { edges { node { ... on StixCoreRelationship {'
                    + opencti_api_client.stix_core_relationship.properties
                    + " } } } }"
                )
            elif "ToStixObservable" in transformName:
                custom_attributes = (
                    'objects(types: ["stix-cyber-observable"]) { edges { node { ... on StixCyberObservable {'
                    + opencti_api_client.stix_cyber_observable.properties
                    + " } } } }"
                )
            else:
                # ToStixDomainEntities
                if output:
                    custom_attributes = (
                        'objects(types: ["'
                        + STIX2toOpenCTItype(output)
                        + '"]) { edges { node { ... on StixDomainObject {'
                        + opencti_api_client.stix_domain_object.properties
                        + " } } } }"
                    )
                else:
                    custom_attributes = (
                        'objects(types: ["Stix-Domain-Object"]) { edges { node { ... on StixDomainObject {'
                        + opencti_api_client.stix_domain_object.properties
                        + " } } } }"
                    )

            container = opencti_class.read(
                id=entity["opencti_entity"]["id"], customAttributes=custom_attributes
            )

            for obj in container["objects"]:
                addStixEntity(opencti_api_client, response, obj)

        # StixDomainEntityTo(Relations|StixDomainEntity)(Inferred)?: Return relations|entities when a relation is found
        elif transformName in [
            "StixDomainEntityToRelations",
            "StixDomainEntityToSightings",
            "StixRelationToRelations",
            "StixObservableToRelations",
            # "StixDomainEntityToRelationsInferred",
            "StixDomainEntityToStixDomainEntity",
            "StixDomainEntityToStixObservable",
            "StixObservableToStixDomainEntity"
            # "StixDomainEntityToStixDomainEntityInferred",
        ]:
            # inferred = "Inferred" in transformName
            stix_relations = []
            custom_attributes_from = None
            custom_attributes_to = None

            if not output and "ToStixDomainEntity" in transformName:
                output = "stix-domain-object"

            if "ToStixDomainEntity" in transformName:
                custom_attributes_from = re.sub(
                    r"from {.*}\s+to {",
                    r"from {  ... on StixDomainObject {"
                    + opencti_api_client.stix_domain_object.properties
                    + "} } to {",
                    opencti_api_client.stix_core_relationship.properties,
                    flags=re.DOTALL,
                )
                custom_attributes_to = re.sub(
                    r"}\s+to {.*}",
                    r"} to { ... on StixDomainObject {"
                    + opencti_api_client.stix_domain_object.properties
                    + "} }",
                    opencti_api_client.stix_core_relationship.properties,
                    flags=re.DOTALL,
                )
            elif "ToStixObservable" in transformName:
                custom_attributes_from = re.sub(
                    r"from {.*}\s+to {",
                    r"from {  ... on StixCyberObservable {"
                    + opencti_api_client.stix_cyber_observable.properties
                    + "} } to {",
                    opencti_api_client.stix_core_relationship.properties,
                    flags=re.DOTALL,
                )
                custom_attributes_to = re.sub(
                    r"}\s+to {.*}",
                    r"} to { ... on StixCyberObservable {"
                    + opencti_api_client.stix_cyber_observable.properties
                    + "} }",
                    opencti_api_client.stix_core_relationship.properties,
                    flags=re.DOTALL,
                )

            if output:
                maltego_type = output
                opencti_type = STIX2toOpenCTItype(output)
                if "ToSightings" in transformName:
                    stix_relations = opencti_api_client.stix_sighting_relationship.list(
                        fromId=entity["opencti_entity"]["x_opencti_id"],
                        toTypes=[opencti_type],
                        # inferred=inferred,
                        first=limit,
                        customAttributes=custom_attributes_to,
                    )
                    stix_relations += opencti_api_client.stix_sighting_relationship.list(
                        toId=entity["opencti_entity"]["x_opencti_id"],
                        fromTypes=[opencti_type],
                        # inferred=inferred,
                        first=limit,
                        customAttributes=custom_attributes_from,
                    )
                else:
                    stix_relations = opencti_api_client.stix_core_relationship.list(
                        fromId=entity["opencti_entity"]["x_opencti_id"],
                        toTypes=[opencti_type],
                        # inferred=inferred,
                        first=limit,
                        customAttributes=custom_attributes_to,
                    )
                    stix_relations += opencti_api_client.stix_core_relationship.list(
                        toId=entity["opencti_entity"]["x_opencti_id"],
                        fromTypes=[opencti_type],
                        # inferred=inferred,
                        first=limit,
                        customAttributes=custom_attributes_from,
                    )
            else:
                maltego_type = None
                if "ToSightings" in transformName:
                    stix_relations = opencti_api_client.stix_sighting_relationship.list(
                        fromId=entity["opencti_entity"]["x_opencti_id"],
                        # inferred=inferred,
                        first=limit,
                        customAttributes=custom_attributes_to,
                    )
                    stix_relations += opencti_api_client.stix_sighting_relationship.list(
                        toId=entity["opencti_entity"]["x_opencti_id"],
                        # inferred=inferred,
                        first=limit,
                        customAttributes=custom_attributes_from,
                    )
                else:
                    stix_relations = opencti_api_client.stix_core_relationship.list(
                        fromId=entity["opencti_entity"]["x_opencti_id"],
                        # inferred=inferred,
                        first=limit,
                        customAttributes=custom_attributes_to,
                    )
                    stix_relations += opencti_api_client.stix_core_relationship.list(
                        toId=entity["opencti_entity"]["x_opencti_id"],
                        # inferred=inferred,
                        first=limit,
                        customAttributes=custom_attributes_from,
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
                        # To prevent errors linked to OpenCTI filtering bug on Stix-Domain-Object,
                        # test if to and from are not empty before adding the relation
                        if (
                            relation["to"]
                            and relation["to"]["standard_id"]
                            == entity["opencti_entity"]["id"]
                            and relation["from"]
                        ):
                            neighbour_entity = addStixEntity(
                                opencti_api_client,
                                response,
                                opencti_api_client.process_multiple_fields(
                                    relation["from"]
                                ),
                            )
                            neighbour_entity.reverseLink()
                        elif relation["to"]:
                            neighbour_entity = addStixEntity(
                                opencti_api_client,
                                response,
                                opencti_api_client.process_multiple_fields(
                                    relation["to"]
                                ),
                            )
                        setLinkLabel(neighbour_entity, relation, True)

        # Stix(Relation|Sighting)ToStixDomainEntity(From|To): Find and add entities
        elif transformName in [
            "StixRelationToStixDomainEntityFrom",
            "StixSightingToStixDomainEntityFrom",
            "StixRelationToStixDomainEntityTo",
            "StixSightingToStixDomainEntityTo",
            "StixRelationToStixDomainEntity",
            "StixSightingToStixDomainEntity",
        ]:
            if transformName in [
                "StixRelationToStixDomainEntityFrom",
                "StixSightingToStixDomainEntityFrom",
                "StixRelationToStixDomainEntity",
                "StixSightingToStixDomainEntity",
            ]:
                if (
                    "Stix-Cyber-Observable"
                    in entity["opencti_entity"]["from"]["parent_types"]
                    or "stix-cyber-observable"
                    in entity["opencti_entity"]["from"]["parent_types"]
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
            if transformName in [
                "StixRelationToStixDomainEntityTo",
                "StixSightingToStixDomainEntityTo",
                "StixRelationToStixDomainEntity",
                "StixSightingToStixDomainEntity",
            ]:
                if (
                    "Stix-Cyber-Observable"
                    in entity["opencti_entity"]["to"]["parent_types"]
                    or "stix-cyber-observable"
                    in entity["opencti_entity"]["to"]["parent_types"]
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
