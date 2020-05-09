import argparse
from bson import json_util
from datetime import datetime, date, timedelta
from dateutil.parser import parse
import json
import os
from random import randint
import requests

from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

# Most from firebase documentation
# https://firebase.google.com/docs/firestore/query-data/get-data
import env_vars
import modules.firebase as fb
from api.views import get_download_link, contract_interaction

# Firebase Firestor from here:
# https://github.com/firebase/firebase-admin-python
from firebase_admin.messaging import (Message, Notification, send)

from modules.decrypter import retrieve_encrypted_data, decrypt_to_dict

FCM_URL = os.environ.get('FCM_URL')
FCM_SCOPES = list(os.environ.get('FCM_SCOPES'))
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
FIRE = fb.Firebase('hp')


########################
# Views #
########################
def index(request):
    """ List all ongoing sessions """
    sessions = FIRE.openSessions()
    docs = sessions.stream()
    doc_list = []
    for doc in docs:
        d = doc.to_dict() 
        d['session_checkin'] = d['session_checkin'].strftime(DATE_FORMAT)
        doc_list.append(d)
    doc_list = sorted(doc_list, key=lambda x: x['session_checkin'], 
                      reverse = True) 
    return render(request, 'sessions.html', { 'docs' : doc_list })


def view_patient(request, session_id):
    """ View the patient """
    error = ""
    followup_session = []
    files_complete = 0
    req_session = {}
    user_session = fire.findSession(session_id)

    if user_session is None:
        return render(request, 'wrong_session.html', {'session_id' : session_id})

    # This is set by the api if a new document or session is created
    if request.session.get(session_id):
        req_session = request.session.get(session_id)
        req_session.setdefault('complete_files', 0)
        if req_session.get('documents'):
            request.session[session_id]['complete_files'] += 1
        if req_session.get("followup_session"):
            request.session[session_id]['complete_files'] += 1

    encrypted_data = retrieve_encrypted_data(user_session.get('data_key'))
    if encrypted_data == None:
       return render(request, 'wrong_session.html', {'session_id' : session_id})
    decrypted_data = decrypt_to_dict(encrypted_data, session_id)
    if decrypted_data == None:
       return render(request, 'wrong_session.html', {'session_id' : session_id})

    decrypted_data['patientSessions'] = replace_current_and_order_desc(
        decrypted_data.get('patientSessions'), user_session)
    add_download_links(decrypted_data['patientSessions'])
    print(decrypted_data)
    documents = []
    return render(request, 'patient.html', 
        {'session': user_session, 
         'patient': decrypted_data,
         'documents': documents,
         'current_session_documents': req_session.get('documents'),
         'tomorrow': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
         'followup_session': req_session.get('followup_session'),
        })

def end_session(request, session_id):

    del request.session[session_id]
    return redirect('/hp')


def create_session(request):
    previous_page = request.META['HTTP_REFERER']
    if request.POST == None:
        messages.error(request, "Missing date and time")
        return redirect(previous_page)
    else:
        session_id = request.POST.get('session_id')
        session_date = request.POST.get('new_session_date')
        session_time = request.POST.get('new_session_time')
        d = parse(f'{session_date} {session_time}')
        new_session_id = (
            str(randint(1000000000, 9999999999)) + 
            str(d.year + d.month + d.day + d.hour + d.minute + d.second))
        new_session = {
            "session_id": new_session_id,
            "session_shared": 0,
            "session_checkin": str(d),
            "session_details": {
                "pain_scale": None,
                "pre_conditions": None,
                "symptoms": None,
                "symptoms_duration": None
            },
            "session_documents": []
        }
        new_session_updates = FIRE.createSession(new_session).to_dict()
        session = {
            "session_id": session_id,
            "followup_session": {
                "session_id": new_session_id,
                "session_checkin": d,

            }
        }
        session_updates = FIRE.updateSession(session).to_dict()
        messages.success(request, "Session with ID " + new_session_id + " created")
        #send_to_topic(new_session_updates['session_id'], new_session_updates['session_shared'], 
        #            new_session_updates['session_documents'])
        if not request.session.get(session_id):
            request.session[session_id] = {}
        request.session[session_id].update({'followup_session': json.dumps(new_session)})
        return redirect(previous_page)




########################
# Supporting Functions #
########################
def add_download_links(sessions):
    for session in sessions:
        documents = session.get('session_documents')
        for document in documents:
            document.setdefault('content', None)
            doc_hash = document.get('document_hash')
            doc_type = document.get('document_type')
            download_link = get_download_link(doc_hash, doc_type)
            document['download_link'] = download_link
            if document.get('document_name') == 'Session Record':
                res = requests.get(download_link)
                if res.status_code == 200:
                    document['content'] = res.json()


def replace_current_and_order_desc(sessions, user_session):
    """ Helper function to order the sessions in DESC order """
    reordered_sessions = []
    for session in sessions:
        if session.get('session_id') == user_session.get('session_id'):
            reordered_sessions = [user_session] + reordered_sessions
        else:
            reordered_sessions = [session] + reordered_sessions
    return reordered_sessions


def sort_sessions(d):
    return -d['session_shared']


def hp_handle_404(request, exception):
    return render(request, '404.html', {'path' : request.build_absolute_uri()})


def update_data(request):
    sessions = FIRE.openSessions()
    docs = sessions.stream()
    doc_list = []
    for doc in docs:
        d = doc.to_dict() 
        d['session_checkin'] = d['session_checkin'].strftime(DATE_FORMAT)
        doc_list.append(d)
    doc_list = sorted(doc_list, key=lambda x: x['session_checkin'], 
                      reverse = True)
    return HttpResponse(json.dumps(doc_list, default=json_util.default), 
                        content_type='application/javascript')


def request_sharing(request):
    fire = fb.Firebase('sharing_request')
    session = request.POST
    updates = FIRE.updateSession(session).to_dict()
    updates['session_checkin'] = updates['session_checkin'].strftime(
        DATE_FORMAT)
    send_to_topic(updates['session_id'], updates['session_shared'], 
                  updates['session_documents'])
    return HttpResponse(json.dumps(updates, default=json_util.default), 
                                   content_type='application/javascript')

def send_to_topic(topic_name, session_shared, session_documents):
    # The topic name can be optionally prefixed with "/topics/".
    topic = topic_name
    # See documentation on defining a message payload.
    message = Message(
        data={
            'session_id': topic_name,
            'session_shared': session_shared,
            'session_documents': json.dumps(session_documents),
        },
        topic=topic,
    )
    # Send a message to the devices subscribed to the provided topic.
    response = send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    return
