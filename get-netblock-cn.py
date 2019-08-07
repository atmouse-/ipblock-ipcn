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

NETBLOCK_CN_COUNTRY_URL = "https://stat.ripe.net/data/country-resource-list/data.json?resource={}"
NETBLOCK_CN_ANNOUCED_PREFIX_URL = "https://stat.ripe.net/data/announced-prefixes/data.json?resource={}"

TO_DIR = "ipcn"
ASN = {
    "CHINANET": {
        "AS64079": {"description": "China Telecom Global LimitedHong Kong", "active": False},
        "AS63838": {"description": "China Telecom HengyangChina", "active": True},
        "AS63835": {"description": "China Telecom HuNan Changsha IDCChina", "active": True},
        "AS63527": {"description": "China Telecom Global LimitedHong Kong", "active": False},
        "AS59265": {"description": "China telecom â China Next Generation InternetChina", "active": True},
        "AS58543": {"description": "China Telecom Guangdong IDCChina", "active": True},
        "AS58542": {"description": "China Telecom YueyangChina", "active": True},
        "AS58541": {"description": "China Telecom XiangtanChina", "active": True},
        "AS58540": {"description": "China Telecom ZhuzhouChina", "active": True},
        "AS58539": {"description": "China Telecom ChangshaChina", "active": True},
        "AS58518": {"description": "China TelecomChina", "active": True},
        "AS58517": {"description": "China TelecomChina", "active": True},
        "AS58461": {"description": "China Telecom HangZhou IDCChina", "active": True},
        "AS49209": {"description": "China Telecom Europe Ltd.United Kingdom", "active": False},
        "AS4835":  {"description": "China Telecom (Group)China", "active": True},
        "AS4816":  {"description": "China Telecom (Group)China", "active": True},
        "AS4815":  {"description": "China Telecom (Group)China", "active": True},
        "AS4813":  {"description": "China Telecom(Group)China", "active": True},
        "AS4812":  {"description": "China Telecom (Group)China", "active": True},
        "AS4811":  {"description": "China Telecom (Group)China", "active": True},
        "AS4809":  {"description": "China Telecom Next Generation Carrier NetworkChina", "active": True},
        "AS44218": {"description": "China Telecom Europe Ltd.Belarus", "active": False},
        "AS4134":  {"description": "China Telecom BackboneChina", "active": True},
        "AS36678": {"description": "CHINA TELECOM (AMERICAS) CORPORATIONUnited States", "active": True},
        "AS25726": {"description": "China Telecom South Africa (Pty) Ltd.South Africa", "active": False},
        "AS23724": {"description": "IDC, China Telecommunications CorporationChina", "active": True},
        "AS17998": {"description": "CHINA TELECOM GROUPAustralia", "active": False},
        "AS17777": {"description": "China Telecommunications Broadcast Satellite Corp.China", "active": False},
        "AS136195":        {"description": "China Telecom DehongChina", "active": True},
        "AS136190":        {"description": "China Telecom DaLiChina", "active": True},
        "AS136188":        {"description": "China Telecom Yunnan Diqing MANChina", "active": True},
        "AS134419":        {"description": "China Telecom BeihaiChina", "active": True},
        "AS134418":        {"description": "China Telecom ShaanxiChina", "active": True},
        "AS134172":        {"description": "Colocation at China Telecom Hong Kong datacenter at ShatinChina", "active": False},
        "AS133776":        {"description": "China Telecom QuanzhouChina", "active": True},
        "AS133775":        {"description": "China Telecom XiamenChina", "active": True},
        "AS133774":        {"description": "China Telecom Fujian Fuzhou IDCChina", "active": True},
        "AS131325":        {"description": "China Telecom KunMingChina", "active": True},
    },
    "UNICOM": {
        "AS9800":  {"description": "CHINA UNICOMChina", "active": True},
        "AS63837": {"description": "China Unicom IP networkChina", "active": True},
        "AS63836": {"description": "China Unicom IP networkChina", "active": True},
        "AS63659": {"description": "CHINA UNICOM CLOUD DATA COMPANY LIMITED Shanghai BranchChina", "active": True},
        "AS4837":  {"description": "China Unicom BackboneChina", "active": True},
        "AS4808":  {"description": "China Unicom Beijing Province NetworkChina", "active": True},
        "AS197407":        {"description": "CHINA UNICOM (EUROPE) OPERATIONS LIMITEDUnited Kingdom", "active": False},
        "AS19174": {"description": "China Unicom (Americas) Operations LtdUnited States", "active": False},
        "AS17816": {"description": "China Unicom IP network China169 Guangdong provinceChina", "active": True},
        "AS17623": {"description": "China Unicom Shenzen networkChina", "active": True},
        "AS17622": {"description": "China Unicom Guangzhou networkChina", "active": True},
        "AS17621": {"description": "China Unicom Shanghai networkChina", "active": True},
        "AS138421":        {"description": "China UnicomChina", "active": True},
        "AS137539":        {"description": "China UnicomChina", "active": True},
        "AS136959":        {"description": "China Unicom Guangdong IP networkChina", "active": True},
        "AS136958":        {"description": "China Unicom Guangdong IP networkChina", "active": True},
        "AS136167":        {"description": "CHINA UNICOM(MACAU) COMPANY LIMITEDMacao", "active": False},
        "AS135061":        {"description": "China Unicom Guangdong IP networkChina", "active": True},
        "AS134821":        {"description": "China Unicom (Australia) Operations Pty LtdAustralia", "active": False},
        "AS134543":        {"description": "China Unicom Guangdong IP networkChina", "active": True},
        "AS134542":        {"description": "China Unicom IP networkChina", "active": True},
        "AS133119":        {"description": "China Unicom IP networkChina", "active": True},
        "AS133118":        {"description": "China Unicom IP networkChina", "active": True},
        "AS132281":        {"description": "China Unicom (Singapore) Operations Pte LtdSingapore", "active": False},
        "AS132101":        {"description": "China Unicom GlobalHong Kong", "active": False},
        "AS10206": {"description": "China Unicom Zhongwei CloudChina", "active": True},
        "AS10099": {"description": "China Unicom Global", "active": False},
    },
    "CMNET": {
        "AS9231":  {"description": "China Mobile Hong Kong Company LimitedHong Kong", "active": False},
        "AS58807": {"description": "China Mobile International LimitedHong Kong", "active": False},
        "AS58453": {"description": "China Mobile International LimitedHong Kong", "active": False},
        "AS56048": {"description": "China Mobile Communicaitons CorporationChina", "active": True},
        "AS56047": {"description": "China Mobile communications corporationChina", "active": True},
        "AS56046": {"description": "China Mobile communications corporationChina", "active": True},
        "AS56045": {"description": "China Mobile communications corporationChina", "active": True},
        "AS56044": {"description": "China Mobile communications corporationChina", "active": True},
        "AS56042": {"description": "China Mobile communications corporationChina", "active": True},
        "AS56041": {"description": "China Mobile communications corporationChina", "active": True},
        "AS56040": {"description": "China Mobile communications corporationChina", "active": True},
        "AS45120": {"description": "China Mobile communications corporationChina", "active": True},
        "AS24311": {"description": "China Mobile Communications Corporation IPv6 networkChina", "active": False},
        "AS24059": {"description": "China Mobile communications corporationChina", "active": True},
        "AS137872":        {"description": "China Mobile Hong Kong Company LimitedHong Kong", "active": False},
        "AS134810":        {"description": "China Mobile Group JiLin communications corporationChina", "active": True},
        "AS132510":        {"description": "IDC ShanXi China Mobile communications corporationChina", "active": True},
        "AS132501":        {"description": "China Mobile Group FuJian communications corporationChina", "active": True},
    },
    "CERNET": {},
    "CRTC": {},
    "CNCGROUP": {},
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
    url = NETBLOCK_CN_ANNOUCED_PREFIX_URL.format(asn)
    json_file = os.path.join(to_dir, "{}.json".format(asn))
    referer_url = "https://stat.ripe.net/{}#tabId=routing".format(asn)
    http_wget(url, json_file, referer_url=referer_url)
    if is_file_empty(json_file):
        return False
    to_file = os.path.join(to_dir, "{}.txt".format(asn))
    return __parse_asn_announced_prefix(json_file, to_file)

def __parse_asn_announced_prefix(source_file, to_file):
    try:
        fp = open(to_file, "w")
        data = json.loads(open(source_file).read())
        for d in data["data"]["prefixes"]:
            # skip ipv6
            if ":" in d["prefix"]:
                continue
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
                    # sleeping may bypass antibot
                    time.sleep(1)
