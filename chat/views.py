from django.shortcuts import render
from server.settings import ChatBotSession
# Create your views here.


def ask_chat_bot(question):
    return ChatBotSession.chat(question)