from django.shortcuts import render
from django.http import HttpResponse
from .models import ChatGPTConfiguration
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import openai
import traceback
from threading import Thread

# Create your views here.

def post_reply(url, reply, user_id):
    lines = reply.splitlines()
    messages = []
    tmp_messages = []
    for line in lines:
        if len("\n".join([*tmp_messages, line])) < 2000:
            tmp_messages.append(line)
        else:
            messages.append("\n".join(tmp_messages))
            tmp_messages = [line]
    if tmp_messages != []:
        messages.append("\n".join(tmp_messages))
    for message in messages:
        body = 'payload=' + json.dumps({"text": message, "user_ids": [user_id]})
        print(f"发送的消息为：{message}")
        requests.post(url, body)

def get_response(context, openAI_API_Key):
    openai.api_key = openAI_API_Key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=context,
    )
    return {"role": "assistant", "content": get_message(response) }, response["usage"]["total_tokens"]

def preprocess(x):
    x = x.decode()
    x = x.split("&")
    x = {a:b for a,b in [i.split("=") for i in x]}
    x["user_id"] = int(x["user_id"])
    return x

def get_message(message):
    return message["choices"][0]["message"]["content"]

def chatgpt_reply(user_id, text, precut = 0, retry = False):
    try:
        config = ChatGPTConfiguration.objects.get(user_id=user_id)
        openAI_API_Key = config.openAI_API_Key
        context = config.get_history()
        if context  == []:
            user_input = {"role": "user", "content": text }
        else:
            user_input = {"role": "system", "content": text }
        context.append(user_input)
        if precut > 0:
            if 2*precut >= len(context):
                context = []
                post_reply(config.bot_url(), "对话过长，强制重新开始。生成回答中……", user_id)
            else:
                context = [context[0], context[1], *context[2:][2*precut:]]
                print(f"对话过长，削减中……削减后context长度为 {len(context)}")
        if retry:
            print("重试前context长度为", len(context))
            if(len(context) < 2):
                post_reply(config.bot_url(), "没有可以重试的对话", user_id)
                return
            context = context[:-2]
            print(f"重试使用的context长度为 {len(context)}")
        response, tokencount = get_response(context, openAI_API_Key)
        context.append(response)
        print(f"新的context长度为 {len(context)}")
        config.save_history(context, tokencount)
        post_reply(config.bot_url(), response["content"], user_id)
        print("发送回复中……")
        print("发送成功")
    except openai.error.AuthenticationError:
        print("API-key错误")
        post_reply(config.bot_url(), "请求失败，请检查API-key是否正确。", user_id)
    except openai.error.Timeout:
        print("请求超时")
        post_reply(config.bot_url(), "请求超时，请检查网络连接。", user_id)
    except openai.error.APIConnectionError:
        print("连接失败")
        post_reply(config.bot_url(), "连接失败，请检查网络连接。", user_id)
    except openai.error.RateLimitError:
        print("请求过于频繁")
        post_reply(config.bot_url(), "请求过于频繁，请5s后再试。", user_id)
    except openai.error.InvalidRequestError:
        traceback.print_exc()
        chatgpt_reply(user_id, text, precut + 1)
    except:
        traceback.print_exc()
        post_reply(config.bot_url(), "发生了未知错误Orz", user_id)

@csrf_exempt
def predict(request):
    message = "ok"
    data = dict(request.POST)
    data["user_id"] = int(*data["user_id"])
    data["text"] = data["text"][0]
    print(f"收到了ID为{data['user_id']}的用户的消息：{data['text']}")
    # execute the chatgpt_reply function in background
    thread1 = Thread(target=chatgpt_reply, args=(data["user_id"], data["text"]), daemon=True)
    thread1.start()
    return HttpResponse(message)

@csrf_exempt
def read_webhook(request):
    message = "default"
    data = dict(request.POST)
    data["user_id"] = int(*data["user_id"])
    data["text"] = data["text"][0]
    print(f"收到了ID为{data['user_id']}的用户的指令：{data['text']}")
    if "clear" in data["text"]:
        try:
            config = ChatGPTConfiguration.objects.get(user_id=data['user_id'])
            config.clear_history()
            message = "历史记录已清空"
        except:
            message = "在清空历史记录时发生了错误"
    elif "totaltoken" in data["text"]:
        try:
            config = ChatGPTConfiguration.objects.get(user_id=data['user_id'])
            message = f"总token用量: {config.total_token}"
        except:
            message = "在获取总token用量时发生了错误"
    elif "retry" in data["text"]:
        try:
            config = ChatGPTConfiguration.objects.get(user_id=data['user_id'])
            message = "正在重试……"
            thread2 = Thread(target=chatgpt_reply, args=(data["user_id"], "Anything", 0, True), daemon=True)
            thread2.start()
        except:
            message = "在重试时发生了错误"
    elif "whoami" in data["text"]:
        try:
            config = ChatGPTConfiguration.objects.get(user_id=data['user_id'])
            message = f"当前用户ID为{data['user_id']}, API-key为{config.openAI_API_Key}, Bot Key为{config.bot_Key}"
        except:
            message = "不存在用户ID为" + str(data['user_id']) + "的用户"
    elif "newuser" in data["text"]:
        try:
            config = ChatGPTConfiguration.objects.get(user_id=data['user_id'])
            message = "当前用户已存在，用户ID为" + str(config.user_id) + "，API-key为" + config.openAI_API_Key + "，Bot Key为" + config.bot_Key
        except:
            config = ChatGPTConfiguration(user_id=data['user_id'])
            try:
                bot_key = data["text"].split(" ")[1]
                config.bot_Key = bot_key
                config.save()
                message = "新用户已创建，用户ID为" + str(config.user_id) + "BOT-Key 为：" + bot_key + "，请设置API-Key"
            except:
                message = f"没有指定bot-key，新用户(ID: {data['user_id']})创建失败"
    elif "setapikey" in data["text"]:
        try:
            config = ChatGPTConfiguration.objects.get(user_id=data['user_id'])
            config.openAI_API_Key = data["text"].split(" ")[1]
            config.save()
            message = "API-key已设置: " + data["text"].split(" ")[1]
        except:
            message = "在设置API-key时发生了错误"
    elif "setbotkey" in data["text"]:
        try:
            config = ChatGPTConfiguration.objects.get(user_id=data['user_id'])
            config.bot_Key = data["text"].split(" ")[1]
            config.save()
            message = "bot-key已设置: " + data["text"].split(" ")[1]
        except:
            message = "在设置bot-key时发生了错误"
    elif "save" in data["text"]:
        try:
            config = ChatGPTConfiguration.objects.get(user_id=data['user_id'])
            file_path = data["text"].split(" ")[1]
            context = config.save_history()
            chat_messages = []
            for i in range(len(context)):
                if i%2 == 0:
                    chat_messages.append("User: " +context[i]["content"])
                else:
                    chat_messages.append("ChatGPT: " + context[i]["content"])
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(chat_messages))
                message= "历史记录已保存"
            except Exception as e:
                message = "在保存历史记录时发生了错误: " + str(e)
        except:
            message = "在保存历史记录时发生了错误"
    else:
        message = "未知指令: " + data["text"]
    post_reply(config.bot_url(), message, data["user_id"])
    return HttpResponse(message)
