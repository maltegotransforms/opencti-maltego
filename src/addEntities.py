from pycti.utils.constants import IdentityTypes
from utils import sanitize, STIX2toOpenCTItype
from maltego_trx.entities import *
from entities import *
from config import format_config


def formatMarkings(entity, markingDefinitions):
    for r in markingDefinitions:
        if (
            format_config["marking_color"]
            and r["definition_type"] == format_config["marking_color"]
        ):
            entity.addProperty(fieldName="marking_color", value=r["color"])
        if (
            format_config["marking_text"]
            and r["definition_type"] == format_config["marking_text"]
        ):
            entity.addProperty(fieldName="marking_text", value=r["definition"])


def addIdentity(transform, opencti_entity):
    entity = transform.addEntity(Identity, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(fieldName="type", value="identity")
    # No aliases in official schema
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    if opencti_entity["entity_type"] == "user":
        identity_class = "individual"
    elif opencti_entity["entity_type"] == "sector":
        identity_class = "class"
    else:
        identity_class = "organization"
    entity.addProperty(fieldName="identity_class", value=identity_class)
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addThreatActor(transform, opencti_entity):
    entity = transform.addEntity(ThreatActor, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    entity.addProperty(fieldName="goals", value=[opencti_entity["goal"]])
    entity.addProperty(
        fieldName="sophistication", value=opencti_entity["sophistication"]
    )
    entity.addProperty(
        fieldName="resource_level", value=opencti_entity["resource_level"]
    )
    entity.addProperty(
        fieldName="primary_motivation", value=opencti_entity["primary_motivation"]
    )
    entity.addProperty(
        fieldName="secondary_motivations",
        value=[opencti_entity["secondary_motivation"]],
    )
    entity.addProperty(
        fieldName="personal_motivations", value=[opencti_entity["personal_motivation"]]
    )
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addIntrusionSet(transform, opencti_entity):
    entity = transform.addEntity(IntrusionSet, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="first_seen", value=opencti_entity["first_seen"])
    entity.addProperty(fieldName="last_seen", value=opencti_entity["last_seen"])
    entity.addProperty(fieldName="goals", value=[opencti_entity["goal"]])
    entity.addProperty(
        fieldName="resource_level", value=opencti_entity["resource_level"]
    )
    entity.addProperty(
        fieldName="primary_motivation", value=opencti_entity["primary_motivation"]
    )
    entity.addProperty(
        fieldName="secondary_motivations",
        value=[opencti_entity["secondary_motivation"]],
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addCampaign(transform, opencti_entity):
    entity = transform.addEntity(Campaign, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="first_seen", value=opencti_entity["first_seen"])
    entity.addProperty(fieldName="last_seen", value=opencti_entity["last_seen"])
    entity.addProperty(fieldName="objective", value=opencti_entity["objective"])
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addIncident(transform, opencti_entity):
    entity = transform.addEntity(Incident, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="first_seen", value=opencti_entity["first_seen"])
    entity.addProperty(fieldName="last_seen", value=opencti_entity["last_seen"])
    entity.addProperty(fieldName="objective", value=opencti_entity["objective"])
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addMalware(transform, opencti_entity):
    entity = transform.addEntity(Malware, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addTool(transform, opencti_entity):
    entity = transform.addEntity(Tool, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addVulnerability(transform, opencti_entity):
    entity = transform.addEntity(Vulnerability, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addAttackPattern(transform, opencti_entity):
    entity = transform.addEntity(AttackPattern, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addCourseOfAction(transform, opencti_entity):
    entity = transform.addEntity(CourseOfAction, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addReport(transform, opencti_entity):
    entity = transform.addEntity(Report, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="published", value=opencti_entity["published"])
    entity.addProperty(fieldName="report_types", value=[opencti_entity["report_class"]])
    entity.addProperty(
        fieldName="confidence", value=opencti_entity["source_confidence_level"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    entity.addProperty(fieldName="object_refs", value=opencti_entity["objectRefsIds"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addIndicator(transform, opencti_entity):
    entity = transform.addEntity(Indicator, sanitize(opencti_entity["name"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="aliases", value=sanitize(opencti_entity["alias"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addIpv4Addr(transform, opencti_entity):
    entity = transform.addEntity(Ipv4Addr, sanitize(opencti_entity["value"], True))
    entity.addProperty(fieldName="id", value=opencti_entity["stix_id_key"])
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def addRelationship(transform, opencti_entity):
    entity = transform.addEntity(
        Relationship, sanitize(opencti_entity["relationship_type"], True)
    )
    entity.addProperty(
        fieldName="id", value=opencti_entity["stix_id_key"], matchingRule="strict"
    )
    entity.addProperty(
        fieldName="created_by_ref",
        value=opencti_entity["createdByRef"]["stix_id_key"]
        if opencti_entity["createdByRef"]
        else None,
    )
    entity.addProperty(
        fieldName="description", value=sanitize(opencti_entity["description"], True)
    )
    entity.addProperty(
        fieldName="object_marking_refs",
        value=[r["stix_id_key"] for r in opencti_entity["markingDefinitions"]],
    )
    entity.addProperty(
        fieldName="external_references", value=opencti_entity["externalReferencesIds"]
    )
    entity.addProperty(fieldName="confidence", value=opencti_entity["weight"])
    entity.addProperty(fieldName="created", value=opencti_entity["created_at"])
    entity.addProperty(fieldName="modified", value=opencti_entity["updated_at"])
    entity.addProperty(fieldName="source_ref", value=opencti_entity["from"]["id"])
    entity.addProperty(fieldName="target_ref", value=opencti_entity["to"]["id"])
    entity.addProperty(fieldName="start_time", value=opencti_entity["first_seen"])
    entity.addProperty(fieldName="stop_time", value=opencti_entity["last_seen"])
    formatMarkings(entity, opencti_entity["markingDefinitions"])
    return entity


def searchAndAddEntity(
    opencti_api_client, transform, stix_id, stix_type, stix_name, output=None
):
    types = [STIX2toOpenCTItype(stix_type)]
    opencti_entity = None
    maltego_entity = None

    if (
        not output
        or output == stix_type
        or (output == "identity" and IdentityTypes.has_value(stix_type))
    ):
        # Search for entity in OpenCTI based on STIX id or (type, name)
        opencti_entity = opencti_api_client.stix_domain_entity.get_by_stix_id_or_name(
            types=types, stix_id_key=stix_id, name=stix_name
        )
        if opencti_entity:
            # Don't trust input type as id is prioritary over (name, type)
            if "Identity" in opencti_entity["parent_types"]:
                maltego_entity = addIdentity(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "threat-actor":
                maltego_entity = addThreatActor(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "intrusion-set":
                maltego_entity = addIntrusionSet(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "campaign":
                maltego_entity = addCampaign(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "incident":
                maltego_entity = addIncident(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "malware":
                maltego_entity = addMalware(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "tool":
                maltego_entity = addTool(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "vulnerability":
                maltego_entity = addVulnerability(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "attack-pattern":
                maltego_entity = addAttackPattern(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "course-of-action":
                maltego_entity = addCourseOfAction(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "report":
                maltego_entity = addReport(transform, opencti_entity)
            elif opencti_entity["entity_type"] == "indicator":
                maltego_entity = addIndicator(transform, opencti_entity)

    return {"opencti_entity": opencti_entity, "maltego_entity": maltego_entity}


def searchAndAddRelashionship(
    opencti_api_client, transform, stix_id, stix_type="relationship", output=None
):
    opencti_entity = None
    maltego_entity = None

    if not output or output == stix_type:
        # Search for entity in OpenCTI based on STIX id or (type, name)
        opencti_entity = opencti_api_client.stix_relation.read(id=stix_id)

        if opencti_entity:
            maltego_entity = addRelationship(transform, opencti_entity)

    return {"opencti_entity": opencti_entity, "maltego_entity": maltego_entity}
