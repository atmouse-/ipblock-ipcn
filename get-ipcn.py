#!/usr/bin/python
import os
import sys
import errno
import socket
import ssl
import urllib.parse
import http.client
import time

IPCN_DOWNTXT_URL_PREFIX = "http://ipcn.chacuo.net/down/t_file=i_"
IPCN_OPR = {
    "CHINANET": "电信宽带",
    "UNICOM": "联通宽带",
    "CMNET": "移动宽带",
    "CERNET": "教育网",
    "CRTC": "铁通宽带",
    "CNCGROUP": "网通宽带",
    "GWBN": "长城宽带",
    "CSTN": "中科网宽带",
    "BCN": "广电宽带",
    "GeHua": "歌华宽带",
    "Topway": "天威宽带",
    "FOUNDERBN": "方正宽带",
    "ZHONG-BANG-YA-TONG": "中邦宽带",
    "WASU": "华数宽带(杭州)",
    "GZPRBNET": "珠江宽带",
    "HTXX": "油田宽带",
    "eTrunk": "视讯宽带",
    "WSN": "东南宽带",
    "CHINAGBN": "金桥网宽带",
    "EASTERNFIBERNET": "盈联宽带",
    "LiaoHe-HuaYu": "华宇宽带",
    "CTN": "有线宽带",
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

if __name__ == "__main__":
    to_dir = "ipcn"
    mkdir_p(to_dir)
    for opr, opr_name in IPCN_OPR.items():
        time.sleep(1)
        url = "http://ipcn.chacuo.net/down/t_file=i_{}".format(opr)
        referer_url = "http://ipcn.chacuo.net/view/i_{}".format(opr)
        to_file = os.path.join(to_dir, "{}.txt".format(opr))
        print(url)
        http_wget(url, to_file, referer_url=referer_url)
        if is_file_empty(to_file):
            sys.exit(1)