import json

import requests


def api_url(path):
    return 'https://qyapi.weixin.qq.com/cgi-bin/' + path


class WeiXinException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "WEIXIN ERROR({0}: {1})".format(self.code, self.message)


def request(method, url, **kwargs):
    result_json = requests.request(method, url, **kwargs).json()
    if 'errcode' in result_json and result_json['errcode'] != 0:
        raise WeiXinException(result_json['errcode'], result_json['errmsg'])
    return result_json


class WeiXinClientFactory:
    def __init__(self, agent_id):
        self.agent_id = agent_id

    def create_by_corp(self, corp_id, secret):
        token = request('get', api_url("gettoken"), params={
            "corpid": corp_id,
            "corpsecret": secret
        })['access_token']
        return WeiXinClient(token, self.agent_id)


class WeiXinClient:
    def __init__(self, token, agent_id):
        self.token = token
        self.agent_id = agent_id

    def publish_message(self, message,
                        users='@all',
                        parties=None,
                        tags=None,
                        message_type='text',
                        safe=False):
        payload = json.dumps({
            "touser": users,
            "toparty": parties,
            "totag": tags,
            "msgtype": message_type,
            "agentid": self.agent_id,
            message_type: {
                "content": message,
            },
            "safe": 1 if safe else 0
        })
        print payload
        request('post', api_url('message/send'), params={
            "access_token": self.token
        }, data=payload)
