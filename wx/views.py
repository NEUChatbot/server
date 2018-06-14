import hashlib
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .secret import secret
import untangle
import time
import requests
import json
from server.settings import global_var

server_address = None
cache = dict()
response_queue = dict()


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


def registered(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    global server_address
    server_address = ip
    return HttpResponse(ip)


def send_to_server(id, question):
    requests.post(server_address, data={'id': id, 'question': question})


@csrf_exempt
def get_replay_from_server(request):
    id = request.POST.get('id')
    content = request.POST.get('content')
    response_queue[id] = content


def reply(request):
    data = request.body
    msg = untangle.parse(data).xml
    id = msg.MsgId.cdata
    response_msg = '聊天服务器暂时无法提供服务:('
    if server_address and requests.get(server_address).content == 'ok':
        send_to_server(id, msg.Content.cdata)
        cache[msg.MsgId.cdata] = msg
        start_time = time.time()
        while time.time() - start_time < 15 and response_queue.get(id, None) is None:
            pass
        response_msg = response_queue.get(id, '聊天服务器暂时无法提供服务:(')
    response = '<xml> ' \
               '<ToUserName>%s</ToUserName> ' \
               '<FromUserName>%s</FromUserName> ' \
               '<CreateTime>%d</CreateTime> ' \
               '<MsgType>text</MsgType> <Content>' \
               '%s</Content>' \
               '</xml> ' % (msg.FromUserName.cdata, msg.ToUserName.cdata, time.time(), response_msg)
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
