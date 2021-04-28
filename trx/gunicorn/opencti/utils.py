from maltego_trx.maltego import MaltegoEntity
from markdown import markdown
from maltego_stix2.config import _heritage_config


def STIX2toOpenCTItype(stix2_type):
    if stix2_type.startswith("x-opencti-"):
        return "X-OpenCTI-" + stix2_type[10:].title().replace(" ", "")
    else:
        return stix2_type.title().replace(" ", "")


def setLinkLabel(maltego_entity, relation, with_type=True):
    link_label = ""
    if with_type:
        link_label += relation["relationship_type"] + "\n"
    if (
        "start_time" in relation
        and relation["start_time"]
        and len(relation["start_time"]) > 9
        and relation["start_time"][0:10] != "1970-01-01"
        and "stop_time" in relation
        and relation["stop_time"]
        and len(relation["stop_time"]) > 9
        and relation["stop_time"][0:10] != "5138-11-16"
    ):
        link_label += relation["start_time"][0:10] + "\n" + relation["stop_time"][0:10]
    elif (
        "start_time" in relation
        and relation["start_time"]
        and len(relation["start_time"]) > 9
        and relation["start_time"][0:10] != "1970-01-01"
    ):
        link_label += relation["start_time"][0:10] + "\n" + "-"
    elif (
        "stop_time" in relation
        and relation["stop_time"]
        and len(relation["stop_time"]) > 9
        and relation["stop_time"][0:10] != "5138-11-16"
    ):
        link_label += "-" + "\n" + relation["stop_time"][0:10]

    if link_label != "":
        maltego_entity.setLinkLabel(link_label)


def get_display_name(fields):
    stix2_type = fields.get("type")
    heritage_conf = _heritage_config.get(stix2_type)

    display_name_field = None
    translation = {}
    if heritage_conf:
        display_name_field = heritage_conf.display_value_override
        translation = heritage_conf.property_map

    name_field_in_maltego = translation.get("name", "name")
    value_field_in_maltego = translation.get("value", "value")
    if display_name_field is None and name_field_in_maltego in fields:
        display_name_field = name_field_in_maltego
    elif display_name_field is None and value_field_in_maltego in fields:
        display_name_field = value_field_in_maltego
    else:
        display_name_field = "id"

    display = fields.get(display_name_field) or fields["id"]
    return display


def addDisplayInfo(maltego_entity: MaltegoEntity, opencti_url=None):
    if not opencti_url:
        return
    if opencti_url.endswith("/graphql"):
        opencti_url = opencti_url[: -len("/graphql")]
    fields = {}
    for fieldName, displayName, matchingRule, value in maltego_entity.additionalFields:
        fields[fieldName] = value

    stix2_id = fields.get("id")
    description = fields.get("description") or ""

    if not stix2_id:
        return

    display = get_display_name(fields)

    if description:
        description = f"<br/><br/>{markdown(description)}"

    url = f"{opencti_url}/dashboard/id/{stix2_id}"
    maltego_entity.setIconURL()
    maltego_entity.addDisplayInformation(
        f"<h2>{display}</h2>"
        f'<h4><a href="{url}">View in OpenCTI</a></h4>'
        f"{description}",
        title="STIX 2 Description",
    )
