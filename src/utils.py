def sanitize(element, encode=False):
    # TODO: replace by maltego_trx functions ?
    if isinstance(element, str):
        element = element.replace("&", "&amp;")
        element = element.replace("<", "&lt;")
        element = element.replace(">", "&gt;")
        element = element.replace("'", "&apos;")
        element = element.replace('"', "&quot;")
        element = element.replace("^", "&#710;")
        element = element.replace("[", "&#91;")
        element = element.replace("]", "&#93;")
        element = element.replace("#", "")
        if encode:
            element = element.encode("unicode-escape").decode("ascii")
    elif isinstance(element, int):
        pass
    elif element == None:
        pass
    elif isinstance(element, dict):
        for key in element.keys():
            element[key] = sanitize(element[key])
    elif isinstance(element, list):
        i = 0
        for val in element:
            element[i] = sanitize(val)
            i += 1
    return element


def STIX2toOpenCTItype(stix2_type):
    if stix2_type == "identity":
        return "Identity"
    if stix2_type == "threat-actor":
        return "Threat-Actor"
    if stix2_type == "intrusion-set":
        return "Intrusion-Set"
    if stix2_type == "campaign":
        return "Campaign"
    if stix2_type == "incident":
        return "Incident"
    if stix2_type == "malware":
        return "Malware"
    if stix2_type == "tool":
        return "Tool"
    if stix2_type == "vulnerability":
        return "Vulnerability"
    if stix2_type == "attack-pattern":
        return "Attack-Pattern"
    if stix2_type == "course-of-action":
        return "Course-Of-Action"
    if stix2_type == "report":
        return "Report"
    if stix2_type == "autonomous-system":
        return "Autonomous-System"
    if stix2_type == "domain-name":
        return "Domain-Name"
    if stix2_type == "file":
        return "File*"
    if stix2_type == "mac-addr":
        return "Mac-Addr"
    if stix2_type == "ipv4-addr":
        return "IPv4-Addr"
    if stix2_type == "ipv6-addr":
        return "IPv6-Addr"
    if stix2_type == "url":
        return "URL"
    if stix2_type == "email-addr":
        return "Email-Addr"
    if stix2_type == "indicator":
        return "Indicator"
    return ""
