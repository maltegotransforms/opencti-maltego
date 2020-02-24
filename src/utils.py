def sanitize(element, encode = False):
    # TODO: replace by maltego_trx functions ?
    if isinstance(element, str):
        element = element.replace('&','&amp;')
        element = element.replace('<','&lt;')
        element = element.replace('>','&gt;')
        element = element.replace('\'','&apos;')
        element = element.replace('\"','&quot;')
        element = element.replace('^','&#710;')
        element = element.replace('[','&#91;')
        element = element.replace(']','&#93;')
        element = element.replace('#','')
        if encode:
            element = element.encode('unicode-escape').decode('ascii')
    elif isinstance(element, int):
        pass
    elif element==None:
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
    opencti_type = ""
    if stix2_type == "campaign":
        opencti_type = "Campaign"
    elif stix2_type == "intrusion-set":
        opencti_type = "Intrusion-Set"
    elif stix2_type == "report":
        opencti_type = "Report"
    elif stix2_type == "threat-actor":
        opencti_type = "Threat-Actor"
    return opencti_type