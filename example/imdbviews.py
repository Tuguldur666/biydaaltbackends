from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from api.settings import sendResponse, connectDB, disconnectDB

def dt_time(request): #{key : value, key1 : value1, key2 : value2, }
    jsons = json.loads(request.body)
    action = jsons['action']
    respData = [{"tsag":str(datetime.now())}] # response-n data-g beldej baina. data key ni list baih buguud list dotor dictionary baina.
    resp = sendResponse(action, 200, "Success", respData)
    return (resp) # response bustsaaj baina

def dt_hello(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    respData = [{"result":"Hello world"}]
    resp = sendResponse(action, 200, "Success",respData)
    return resp

def dt_class(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    respData = [{"result":"ISSW"}]
    resp = sendResponse(action, 200, "Success", respData)
    return resp

def dt_connect_status(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    
    try:
        conn = connectDB()
        disconnectDB(conn)
        respData = [{"status": "DB connected successfully"}]
        resp = sendResponse(action, 200, "Success", respData)
    except Exception as e:
        respData = [{"status": "DB connection failed", "error": str(e)}]
        resp = sendResponse(action, 500, "Error", respData)
    
    return resp


@csrf_exempt
def checkService(request):
    if request.method == "POST":
        try:
            jsons = json.loads( request.body)
        except: 
            action = "invalid request json"
            respData = []
            resp = sendResponse(action, 404, "Error", respData)
            return (JsonResponse(resp))
        try: 
            action = jsons['action']
        except:
            action = "no action"
            respData = []
            resp = sendResponse(action, 400,"Error", respData)
            return (JsonResponse(resp))
    
        if(action == 'time'):
            result = dt_time(request)
            return (JsonResponse(result))
        elif(action == 'hello'): #hello world
            result = dt_hello(request)
            return (JsonResponse(result))
        elif(action == 'class'): #
            result = dt_class(request)
            return (JsonResponse(result))
        elif(action == 'dbcheck'):
            result = dt_connect_status(request)
            return (JsonResponse(result))
        else:
            action = action
            respData = []
            resp = sendResponse(action, 406,"Error", respData)
            return (JsonResponse(resp))
    elif request.method == "GET":
        return (JsonResponse({ "method":"GET" }))
    else :
        return (JsonResponse({ "method":"busad" }))