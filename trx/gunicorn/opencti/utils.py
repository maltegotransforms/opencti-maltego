def STIX2toOpenCTItype(stix2_type):
    if stix2_type.startswith("x-opencti-"):
        return "XOpenCTI" + stix2_type[10:].replace("-", " ").title().replace(" ", "")
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
