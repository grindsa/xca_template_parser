#!/usr/bin/python3
""" script to parse an xca certificate template """
import sys
from pprint import pprint

def _asn1_stream_parse(asn1_stream=None):
    """ parse asn_string """

    oid_dic = {
        "2.5.4.3": "commonName",
        "2.5.4.4": "surname",
        "2.5.4.5": "serialNumber",
        "2.5.4.6": "countryName",
        "2.5.4.7": "localityName",
        "2.5.4.8": "stateOrProvinceName",
        "2.5.4.9": "streetAddress",
        "2.5.4.10": "organizationName",
        "2.5.4.11": "organizationalUnitName",
        "2.5.4.12": "title",
        "2.5.4.13": "description",
        "2.5.4.42": "givenName",
    }

    # cut first 8 bytes which are bogus
    # asn1_stream = asn1_stream[8:]

    # print(asn1_stream)
    stream_list = asn1_stream.split(b'\x06\x03\x55')

    # we have to remove the first element from list as it contains junk
    stream_list.pop(0)

    dn_dic = {}
    for ele in stream_list:
        oid = '2.5.{0}.{1}'.format(ele[0], ele[1])
        if oid in oid_dic:
            value_len = ele[3]
            value = ele[4:4+value_len]
            dn_dic[oid_dic[oid]] = value.decode('utf-8')
    return dn_dic


def _utf_stream_parse(utf_stream=None):
    """ parse template information from utf_stream into dictitionary """

    template_dic = {}

    if utf_stream:
        stream_list = utf_stream.split(b'\x00\x00\x00')

        # iterate list and clean up parameter
        parameter_list = []
        for idx, ele in enumerate(stream_list):
            ele = ele.replace(b'\x00', b'')
            if idx > 0:
                # strip the first character
                ele = ele[1:]
            parameter_list.append(ele.decode('utf-8'))

        if parameter_list:
            # convert list into a directory
            template_dic = {item : parameter_list[index+1] for index, item in enumerate(parameter_list) if index % 2 == 0}

    return template_dic

def _stream_split(byte_stream):
    """ split template in asn1 structure and utf_stream """
    asn1_stream = None
    utf_stream = None

    if byte_stream:
        # search pattern
        pos = byte_stream.find(b'\x00\x00\x00\x0c') + 4

        # read file again and seek content till position
        asn1_stream = byte_stream[:pos]
        utf_stream = byte_stream[pos:]

    return(asn1_stream, utf_stream)

def template_process(byte_string=None):
    """ process template """
    (asn1_stream, utf_stream) = _stream_split(byte_string)

    if asn1_stream:
        dn_dic = _asn1_stream_parse(asn1_stream)

    template_dic = {}
    if utf_stream:
        template_dic = _utf_stream_parse(utf_stream)
        if template_dic:
            # replace '' with None
            template_dic = {k: None if not v else v for k, v in template_dic.items()}

    return (dn_dic, template_dic)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        IN_FILE = sys.argv[1]
        with open(IN_FILE, 'rb') as in_file:
            BYTE_STREAM = in_file.read()
            (DN_DIC, TEMPLATE_DIC) = template_process(BYTE_STREAM)
            print('\n# DN attributes')
            pprint(DN_DIC)
            print('\n# certificate extensions and attributes')
            pprint(TEMPLATE_DIC)
    else:
        print('you need to specify a template file as argument...')
