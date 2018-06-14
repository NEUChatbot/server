import hashlib
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .secret import secret
import xml.etree.ElementTree as ET
import time
import requests
import json
from server.settings import global_var


def checksignature(request):
    # if request.method != 'GET':
    #     return HttpResponse('only get method is available for check signature')
    # print(request.GET)
    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    echostr = request.GET.get('echostr')
    nonce = request.GET.get('nonce')
    if signature and timestamp and echostr:
        l = [secret['check_signature_token'], nonce, timestamp]
        l.sort()
        s = ''.join(l)
        s = hashlib.sha1(s.encode('utf-8')).hexdigest()
        if s == signature:
            return HttpResponse(echostr)
    return HttpResponse('Fail')


def reply(request):
    data = request.body
    print(data)
    tree = ET.fromstring(data)
    msg = {}
    for t in tree:
        msg[t.tag] = t.text
    # if msg['MsgType'] != 'text':
    #     msg['Content'] = '不支持的消息类型: %s' % msg['MsgType']
    response = '<xml> ' \
               '<ToUserName>%s</ToUserName> ' \
               '<FromUserName>%s</FromUserName> ' \
               '<CreateTime>%d</CreateTime> ' \
               '<MsgType>text</MsgType> <Content>' \
               '%s</Content>' \
               '</xml> ' % (msg['FromUserName'], msg['ToUserName'], time.time(), ChatBotSession.chat(msg['Content']))
    return HttpResponse(response)


def get_token(request):
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
        secret['app_id'], secret['app_secret'])

    if global_var['wx_token_expire_time'] - time.time() <= 0:
        r = requests.get(url).content.decode()
        o = json.loads(r)
        if 'access_token' in o:
            global_var['wx_token_expire_time'] = time.time() + o['expires_in']
            global_var['wx_token'] = o['access_token']
        else:
            return HttpResponse(r)  # 返回错误代码
    return HttpResponse(global_var['wx_token'])

@csrf_exempt
def wx(request):
    if request.method == 'GET':
        return checksignature(request)
    elif request.method == 'POST':
        return reply(request)
