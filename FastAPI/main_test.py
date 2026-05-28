import akshare as ak
import efinance as ef
import urllib3
import requests
# import adata

# 申万研究所(swsresearch.com)证书链不完整，对该域名跳过 SSL 验证
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_original_request = requests.Session.request
def _selective_verify_request(self, method, url, **kwargs):
    if 'swsresearch.com' in url:
        kwargs['verify'] = False
    return _original_request(self, method, url, **kwargs)
requests.Session.request = _selective_verify_request


if __name__ == '__main__':
    pass
