""" Creates an SNMP conf.yaml file for DataDog """
import requests
import xmltodict
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

dce_username = ''
dce_password = ''
dce_server = ''

def getAllDevices(dce_server):
    """Gets All Devices For The Provided DCE Server."""
    auth = HTTPBasicAuth(dce_username, dce_password)
    url = "https://" + str(dce_server) + "/integration/services/ISXCentralDeviceService_v2_0"
    body = """<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:isx=\"http://www.apc.com/stdws/xsd/ISXCentralDevices-v2\">
    <soapenv:Header/>
    <soapenv:Body>
    <isx:getAllDevicesRequest>
    </isx:getAllDevicesRequest>
    </soapenv:Body>
    </soapenv:Envelope>"""
    headers = {'Content-Type': 'text/plain'}
    requests.packages.urllib3.disable_warnings()
    response = requests.request("GET", url, headers=headers, data=body, verify=False, auth=auth)
    return response.content


def instance_builder():
    """Builds all strings for the Instance"""
    #instance_string = "  -\n    ip_address: {}\n    port: 161\n    community_string: public\n    snmp_version: 1\n    profile: apc_ups\n"
    instance_block = ""
    dce_export = xmltodict.parse(getAllDevices(dce_server))['soap:Envelope']['soap:Body']['ns1:getAllDevicesResponse']['ns1:ArrayOfISXCDevice']['ns2:ISXCDevice']
    for configuration_item in dce_export:
        if str(configuration_item['ns2:ipAddress']) != "None":
            if str(configuration_item['ns2:ISXCDeviceType']) == "UPS":
                instance_string = "  -\n    ip_address: {}\n    port: 161\n    community_string: public\n    snmp_version: 1\n    profile: apc_ups\n".format(str(configuration_item['ns2:ipAddress']))
                instance_block += instance_string
    return instance_block

def build_yaml():
    """Builds the conf.yaml dynamically."""
    doc_head = """init_config:\ninstances:\n"""
    doc_body = instance_builder()
    doc_foot = """\nmetrics:\n  - MIB: UDP-MIB\n    symbol: udpInDatagrams\n  - MIB: TCP-MIB\n    symbol: tcpActiveOpens\n  - OID: 1.3.6.1.2.1.6.5.0\n    name: tcpPassiveOpens\n  - OID: 1.3.6.1.2.1.6.5.0\n    name: tcpPassiveOpens\n    metric_tags:\n      - TCP"""
    return str(doc_head + doc_body + doc_foot)

if __name__ == "__main__":
    f = open("conf.yaml", "w")
    f.write(build_yaml())
    f.close()
