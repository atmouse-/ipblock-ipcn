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


TO_DIR = "ipcloud"

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

def fetch_aws_announced_prefix(service="AMAZON"):
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
        if n['region'].startswith("cn-"): continue
        if n['service'] == service:
            fileout.write(n['ip_prefix'])
            fileout.write("\n")
    os.remove(json_file)
    return True

if __name__ == "__main__":
    fetch_aws_announced_prefix()