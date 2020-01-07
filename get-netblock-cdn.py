#!/usr/bin/python
import os
import sys
import errno
import socket
import ssl
import urllib.parse
import http.client
import time
import json

import netaddr
import IP2Location
ip2 = IP2Location.IP2Location("IP2LOCATION-LITE-DB1.BIN")

NETBLOCK_COUNTRY_URL = "https://stat.ripe.net/data/country-resource-list/data.json?resource={}"
NETBLOCK_ANNOUCED_PREFIX_URL = "https://stat.ripe.net/data/announced-prefixes/data.json?resource={}"

TO_DIR = "ipcdn"
ASN = {
    "AKAMAI": {
        "AS12222": {"description": "AKAMAI - Akamai Technologies, Inc., US", "active": True},
        "AS16625": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS16702": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS18680": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS18717": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS20189": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS20940": {"description": "AKAMAI-ASN1, US", "active": True},
        "AS21342": {"description": "AKAMAI-ASN2, US", "active": True},
        "AS21357": {"description": "AKAMAI-MAPPING, US", "active": True},
        "AS21399": {"description": "AKAMAI3, US", "active": True},
        "AS22207": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS23454": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS23455": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS23903": {"description": "AKAMAI-AS-BANGLORE Akamai Banglore Office ASN, IN", "active": True},
        "AS24319": {"description": "AKAMAI-TYO-AP Akamai Technologies Tokyo ASN, SG", "active": True},
        "AS30675": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS31107": {"description": "AKAMAI-NY, US", "active": True},
        "AS31108": {"description": "AKAMAI-VA, US", "active": True},
        "AS31109": {"description": "AKAMAI-LA, US", "active": True},
        "AS31110": {"description": "AKAMAI-SJC, US", "active": True},
        "AS31377": {"description": "AKAMAI-BOS, US", "active": True},
        "AS33905": {"description": "AKAMAI-AMS, US", "active": True},
        "AS34164": {"description": "AKAMAI-LON, GB", "active": True},
        "AS34850": {"description": "AKAMAI-MUC, IR", "active": True},
        "AS35204": {"description": "AKAMAI-DUB, US", "active": True},
        "AS35993": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS35994": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS36183": {"description": "AKAMAI-AS - Akamai Technologies, Inc., US", "active": True},
        "AS39836": {"description": "AKAMAI-FRA, DE", "active": True},
        "AS43639": {"description": "AKAMAI-AMS2, NL", "active": True},
        "AS55770": {"description": "AKAMAI-AP Akamai Technologies, Inc., SG", "active": True},
        "AS393560": {"description": "AKAMAI-TEST - Akamai Technologies, Inc., US", "active": True},
    },
    "Fastly": {
        "AS54113": {"description": "Fastly", "active": True},
        "AS394192": {"description": "Fastly", "active": True},
    },
    "Msedge": {
        "AS8075": {"description": "Microsoft Corporation", "active": True},
    },
    "IDCFrontier": {
        "AS4694": {"description": "IDC Frontier Inc.", "active": True},
    },
    "EdgeCast": {
        "AS15133": {"description": "EdgeCast Networks, Inc. d/b/a Verizon Digital Media Services", "active": True},
    },
}

TXT = {
    "CLOUDFLARE": {
        "ALL_V4": {"url": "https://www.cloudflare.com/ips-v4", "active": True},
    },
}

CA_BUNDLE_FILE = ""


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise e

def get_http_proxy():
    try:
        proxy1 = os.environ['http_proxy']
        host, port = urllib.parse.urlparse(proxy1)[1].split(':')
        proxy1 = (host, int(port))
    except:
        proxy1 = ''
    try:
        proxy2 = os.environ['HTTP_PROXY']
        host, port = urllib.parse.urlparse(proxy2)[1].split(':')
        proxy2 = (host, int(port))
    except:
        proxy2 = ''
    return proxy1 or proxy2

def get_https_proxy():
    try:
        proxy1 = os.environ['https_proxy']
        host, port = urllib.parse.urlparse(proxy1)[1].split(':')
        proxy1 = (host, int(port))
    except:
        proxy1 = ''
    try:
        proxy2 = os.environ['HTTPS_PROXY']
        host, port = urllib.parse.urlparse(proxy2)[1].split(':')
        proxy2 = (host, int(port))
    except:
        proxy2 = ''
    return proxy1 or proxy2

def urlopen(url, ca_file=CA_BUNDLE_FILE, http_proxy=get_http_proxy(), https_proxy=get_https_proxy(), referer=""):
    '''
    return filehandle
    '''
    port = 0
    headers = {
        'Cache-Control':'no-cache',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    }
    if referer:
        headers['Referer'] = referer
    # default http protocol
    if (not url.startswith("http://")) and (not url.startswith("https://")):
        url = "http://" + url
    scheme, uri = url.split(':', 1)
    netloc, path = urllib.parse.splithost(uri)
    if ':' in netloc:
        host, port = netloc.split(':')
        port = int(port)
    else:
        host = netloc
    if scheme == "http":
        if not port: port = 80
        if http_proxy:
            path = url
            conn = http.client.HTTPConnection(*http_proxy)
            conn.request("GET", path, headers=headers)
        else:
            conn = http.client.HTTPConnection(host, port=port)
            conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        return response
    elif scheme == "https":
        if not port: port = 443
        orighost, origport = host, port
        origpath = path
        if https_proxy:
            host, port = https_proxy
            path = url
        else:
            if ca_file:
                ca_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                ca_context.load_verify_locations(cafile=ca_file)
                conn = http.client.HTTPSConnection(host, port=port, context=ca_context)
            else:
                conn = http.client.HTTPSConnection(host, port=port)
            if https_proxy:
                conn.set_tunnel(orighost, origport)
                conn.request("GET", origpath, headers=headers)
            else:
                conn.request("GET", origpath, headers=headers)
            response = conn.getresponse()
    else:
        raise Exception("protocol unsupport.")
    return response

def http_wget(url, save_to, proxy='', referer_url=""):
    CHUNK = 64 * 1024
    try:
        if proxy:
            proxy_host, proxy_port = proxy.split(':')
            proxy_port = int(proxy_port)
            response = urlopen(url, http_proxy=(proxy_host, proxy_port), https_proxy=(proxy_host, proxy_port), referer=referer_url)
        else:
            response = urlopen(url, referer=referer_url)
        fp = open(save_to, 'wb')
        while True:
            chunk = response.read(CHUNK)
            if not chunk: break
            fp.write(chunk)
        fp.flush()
        del fp
        return True
    except:
        return False

def is_file_empty(filename):
    if os.stat(filename).st_size == 0:
        return True
    else:
        return False

def fetch_asn_announced_prefix(org, asn):
    to_dir = os.path.join(TO_DIR, org)
    mkdir_p(to_dir)
    url = NETBLOCK_ANNOUCED_PREFIX_URL.format(asn)
    json_file = os.path.join(to_dir, "{}.json".format(asn))
    referer_url = "https://stat.ripe.net/{}#tabId=routing".format(asn)
    http_wget(url, json_file, referer_url=referer_url)
    if is_file_empty(json_file):
        return False
    to_file = os.path.join(to_dir, "{}.txt".format(asn))
    return __parse_asn_announced_prefix(json_file, to_file)

def fetch_txt_announced_prefix(org, ipversion, url):
    to_dir = os.path.join(TO_DIR, org)
    mkdir_p(to_dir)
    txt_file = os.path.join(to_dir, "{}.txt".format(ipversion))
    referer_url = "https://www.cloudflare.com/ips/"
    http_wget(url, txt_file, referer_url=referer_url)
    if is_file_empty(txt_file):
        return False
    return True

def fetch_aws_announced_prefix(service="CLOUDFRONT"):
    to_dir = os.path.join(TO_DIR, service)
    mkdir_p(to_dir)
    json_file = os.path.join(to_dir, "{}.json".format("ALL_V4"))
    txt_file = os.path.join(to_dir, "{}.txt".format("ALL_V4"))
    http_wget("https://ip-ranges.amazonaws.com/ip-ranges.json", json_file)
    if is_file_empty(json_file):
        return False
    filein = open(json_file)
    fileout = open(txt_file, 'w')
    ctx = json.loads(filein.read())
    for n in ctx['prefixes']:
        if n['service'] == service:
            fileout.write(n['ip_prefix'])
            fileout.write("\n")
    os.remove(json_file)
    return True

def __parse_asn_announced_prefix(source_file, to_file):
    try:
        fp = open(to_file, "w")
        data = json.loads(open(source_file).read())
        for d in data["data"]["prefixes"]:
            # skip ipv6
            if ":" in d["prefix"]:
                continue
            # # filter hk
            # firstip = netaddr.IPNetwork(d["prefix"]).ip.__str__()
            # if ip2.get_country_short(firstip) != b"HK":
            #     continue
            fp.write(d["prefix"])
            fp.write("\n")
            fp.flush()
        fp.close()
        return True
    except:
        return False

if __name__ == "__main__":
    for org, asns in ASN.items():
        if asns:
            for asn, des in asns.items():
                if des["active"]:
                    # print("{}:{}".format(asn, des["description"]))
                    if not fetch_asn_announced_prefix(org, asn):
                        sys.exit(1)
                    # sleep 10sec may bypass antibot
                    time.sleep(1)
    for org, ips in TXT.items():
        if ips:
            for ipversion, ip in ips.items():
                if ip["active"]:
                    # print("{}:{}".format(asn, des["description"]))
                    if not fetch_txt_announced_prefix(org, ipversion, ip["url"]):
                        sys.exit(1)
                    # sleep 10sec may bypass antibot
                    time.sleep(1)
    fetch_aws_announced_prefix()