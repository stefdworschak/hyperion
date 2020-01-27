import argparse
from datetime import datetime as dt
import json
from bson import json_util
import os
import requests

from django.http import HttpResponse
from django.shortcuts import render


# Most from firebase documentation
# https://firebase.google.com/docs/firestore/query-data/get-data
import env_vars
import modules.firebase as fb

# Firebase Firestor from here:
# https://github.com/firebase/firebase-admin-python
from firebase_admin.messaging import (Message, Notification, send)

FCM_URL = os.environ.get('FCM_URL')
FCM_SCOPES = list(os.environ.get('FCM_SCOPES'))

# Create your views here.
def index(request):
    fire = fb.Firebase('hp')
    sessions = fire.openSessions()
    docs = sessions.stream()
    doc_list = []
    for doc in docs:
        d = doc.to_dict() 
        d['session_checkin'] = d['session_checkin'].strftime('%Y-%m-%d %H:%M:%S')
        doc_list.append(d)
    doc_list = sorted(doc_list, key=lambda x: x['session_checkin'], reverse = True) 
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
    doc_list = sorted(doc_list, key=lambda x: x['session_checkin'], reverse = True)
    return HttpResponse(json.dumps(doc_list, default=json_util.default), content_type="application/javascript")

def requestSharing(request):
    fire = fb.Firebase('sharing_request')
    session = request.POST
    updates = fire.updateSession(session).to_dict()
    updates['session_checkin'] = updates['session_checkin'].strftime('%Y-%m-%d %H:%M:%S')
    send_to_topic(updates['session_id'])
    return HttpResponse(json.dumps(updates, default=json_util.default), content_type="application/javascript")

def send_to_topic(topic_name):
    # [START send_to_topic]
    # The topic name can be optionally prefixed with "/topics/".
    topic = topic_name

    # See documentation on defining a message payload.
    message = Message(
        notification=Notification(
            title="HYPERION PERMISSION SHARE", 
            body="Do you want to give permission to share your information?",
            image=""
            ),
        data={
            'score': '850',
            'time': '2:45',
            'session_id': topic_name,
        },
        topic=topic,
    )

    # Send a message to the devices subscribed to the provided topic.
    response = send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_topic]
    return
