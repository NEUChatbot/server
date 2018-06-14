from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(requests):
    return HttpResponse('COMING SOON')


def whatismyip(requests):
    x_forwarded_for = requests.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = requests.META.get('REMOTE_ADDR')
    return HttpResponse(ip)