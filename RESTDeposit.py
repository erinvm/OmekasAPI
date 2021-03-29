import xml.etree.ElementTree as ET
import json
import requests
import secrets

# Replace IP with new Omeka-s IP when needed.
IP = '34.205.75.131'
IDENTITY = secrets.key_identity
CREDENTIAL = secrets.key_credential

ns = {'dc': 'http://purl.org/dc/elements/1.1/', 
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/', 
        'xml': 'http://www.openarchives.org/OAI/2.0/'}




def build_url(ip, category=None):
    """ Build url based on IP and API needs.
        Return: url
    """
    if category == 'item_set':
        url = f'http://{ip}/omeka-s/api/item_sets?'
    elif category == 'item':
        url = f'http://{ip}/omeka-s/api/items?'
    else:
        url = f'http://{ip}/omeka-s/'
    return url


def get_oapi_root(url):
    """ Harvest all oai_dc metadata records from other ip item set given a url. 
        Return: xml tree
    """
    xml_data = requests.get(url + "oai?verb=ListRecords&metadataPrefix=oai_dc&set=176")
    root = ET.fromstring(xml_data.text)

    return root


def create_post(url, data, files=''):
    """Given a url and string, creates post request.
        Return: request response
    """
    payload = {'key_identity' : IDENTITY, 'key_credential' : CREDENTIAL }
    headers = {'Content-type': 'application/json'}

    return requests.post(url, params=payload, headers=headers, data=data, files=files)


def get_elements(dc, is_id):
    """ Retrieve elements from xml tree, form into data string, and post to Omeka given an item_set id.
        TO DO: try to find out how to upload multiple values with the same label. 
        Return: nothing
    """
    create_set_url = build_url(IP, 'item')

    for record in dc.iterfind(".//oai_dc:dc", ns):
        title = record.find('dc:title', ns).text
        title_str = '{ "dcterms:title" : [ {"property_id": 1, "property_label" : "Title", "@value" : "'+title+'", "type" : "literal" } ],'
        
        creator  = record.find('dc:creator', ns).text
        creator_str = ' "dcterms:creator" : [ {"property_id": 2, "property_label" : "Creator", "@value" : "'+creator+'", "type" : "literal" } ],'
        
        itemset_str = ' "o:item_set" : [ {"o:id": '+str(is_id)+'}]}'

        date = record.findall('dc:date', ns)[0].text
        date_str = ' "dcterms:date" : [ {"property_id": 7, "property_label" : "Date", "@value" : "'+date+'", "type" : "literal" } ],'

        iden = ''
        for identifer in record.findall('dc:identifier', ns):
            iden = iden+' '+identifer.text
        id_str = ' "dcterms:identifier" : [ {"property_id": 10, "property_label" : "Identifier", "@value" : "'+iden+'", "type" : "literal" } ],'

        data = f'{title_str} "@type" : "o:Item", {creator_str}{date_str}{id_str}{itemset_str}'

        create_post(create_set_url, data)

    return None



#create item set
create_set_url = build_url(IP, 'item_set')
restinput_is_data = '{"dcterms:title" : [ { "type" : "literal", "property_label" : "Title", "@value" : "RestInput", "property_id" : 1 } ] }'
response = create_post(create_set_url, restinput_is_data).json()
itemset_id = response['o:id']

#harvest oai_dc from other_ip get item_set 'Zotero Input' (set 176)
other_ip = '34.235.195.237'
get_url = build_url(other_ip)
xml = get_oapi_root(get_url)
get_elements(xml, itemset_id)
