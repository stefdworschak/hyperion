import json
from bson import json_util
from datetime import datetime as dt

from django.http import HttpResponse
from django.shortcuts import render

import modules.firebase as fb

# Create your views here.
# Most from firebase documentation
# https://firebase.google.com/docs/firestore/query-data/get-data
def index(request):
    fire = fb.Firebase('hp')
    sessions = fire.openSessions()
    docs = sessions.stream()
    doc_list = []
    for doc in docs:
        d = doc.to_dict() 
        d['session_checkin'] = d['session_checkin'].strftime('%Y-%m-%d %H:%M:%S')
        doc_list.append(d)
    return render(request, "sessions.html", { 'docs' : doc_list })

def updateData(request):
    fire = fb.Firebase('hp')
    sessions = fire.openSessions()
    docs = sessions.stream()
    doc_list = []
    for doc in docs:
        d = doc.to_dict() 
        d['session_checkin'] = d['session_checkin'].strftime('%Y-%m-%d %H:%M:%S')
        doc_list.append(d)
    
    return HttpResponse(json.dumps(doc_list, default=json_util.default), content_type="application/javascript")

def requestSharing(request):
    fire = fb.Firebase('sharing_request')
    session = request.POST
    updates = fire.updateSession(session).to_dict()
    updates['session_checkin'] = updates['session_checkin'].strftime('%Y-%m-%d %H:%M:%S')
    return HttpResponse(json.dumps(updates, default=json_util.default), content_type="application/javascript")
