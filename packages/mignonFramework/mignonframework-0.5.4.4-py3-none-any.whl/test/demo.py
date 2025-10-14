import requests
import json
import urllib.parse
from mignonFramework import JSONFormatter

# 由 Mignon Rex 的 MignonFramework.CurlToRequestsConverter 生成
# Have a good Request

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6,zh-TW;q=0.5",
    "Cache-Control": "no-cache",
    "Origin": "http://www.shandong.gov.cn",
    "Pragma": "no-cache",
    "Proxy-Connection": "keep-alive",
    "Referer": "http://www.shandong.gov.cn/jpaas-jpolicy-web-server/front/info/list?titles=%E6%B5%B7%E6%B4%8B",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

cookies = {
    "_ud_": "801fffb9ddb44708a97d418c32c05d3f",
    "flag0": "Fri%20Sep%2012%202025%2010:54:51%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)",
    "arialoadData": "true",
    "zh_choose_undefined": "s",
    "Hm_lvt_3147c565b4637bb1f8c07a562a3c6cb7": "1757472689,1757645692,1757655261",
    "HMACCOUNT": "7506E1E9AB54B3B8",
    "ariauseGraymode": "false",
    "Hm_lpvt_3147c565b4637bb1f8c07a562a3c6cb7": "1757655274",
    "wondersLog_sdywtb_sdk": "%7B%22persistedTime%22%3A1757472688804%2C%22updatedTime%22%3A1757655274409%2C%22sessionStartTime%22%3A1757645679925%2C%22sessionReferrer%22%3A%22http%3A%2F%2Fwww.shandong.gov.cn%2Fjpaas-jpolicy-web-server%2Ffront%2Finfo%2Findex%22%2C%22deviceId%22%3A%2294516ae9ae4fa3cd691cd2ddae482ce3-9400%22%2C%22LASTEVENT%22%3A%7B%22eventId%22%3A%22wondersLog_pv%22%2C%22time%22%3A1757655274409%7D%2C%22sessionUuid%22%3A8582028317666946%2C%22costTime%22%3A%7B%22wondersLog_unload%22%3A1757655274409%7D%7D"
}

params = {
    "title": "海洋",
    "issue": "",
    "publishTime": "",
    "infoLevel": "",
    "category": "",
    "agencyword": "",
    "publishUnit": "",
    "themeCategory": "",
    "city": "",
    "sortKey": "publishdate",
    "level": "",
    "levelWord": "",
    "content": "",
    "analysis": "1",
    "pageSize": "10",
    "pageNo": "2"
}

url = "http://www.shandong.gov.cn/jpaas-jpolicy-web-server/front/info/do-search"

response = requests.post(
    url,
    headers=headers,
    cookies=cookies,
    params=params,
    verify=False
)

# The following print statements are for debugging and are not part of the core request logic.
print(f"状态码: {response.status_code}")
try:
    print("响应 JSON:", response.json())
    JSONFormatter(response.text)
except json.JSONDecodeError:
    print("响应文本:", response.text)