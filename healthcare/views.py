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
from django.contrib.auth.decorators import login_required

# Most from firebase documentation
# https://firebase.google.com/docs/firestore/query-data/get-data
import env_vars
import modules.firebase as fb
from api.views import get_download_link, contract_interaction

# Firebase Firestor from here:
# https://github.com/firebase/firebase-admin-python
from firebase_admin.messaging import (Message, Notification, send)

from modules.decrypter import (retrieve_encrypted_data, decrypt_to_dict,
                               delete_encrpted_data)

FCM_URL = os.environ.get('FCM_URL')
FCM_SCOPES = list(os.environ.get('FCM_SCOPES'))
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
FIRE = fb.Firebase('hp')


########################
# Views #
########################
@login_required(redirect_field_name=None, login_url='/')
def index(request):
    """ List all ongoing sessions """
    session_list = list_sessions()
    return render(request, 'sessions.html', { 'sessions' : session_list })

@login_required(redirect_field_name=None, login_url='/')
def scheduled(request):
    """ List all ongoing sessions """
    session_list = list_sessions(order='asc')
    return render(request, 'scheduled.html', { 'sessions' : session_list })

@login_required(redirect_field_name=None, login_url='/')
def view_patient(request, session_id):
    """ View the patient """
    error = ""
    followup_sessions = []
    files_complete = 0
    req_session = {}
    user_session = FIRE.findSession(session_id)

    if user_session is None:
        return render(request, 'wrong_session.html', {'session_id' : session_id})

    # This is set by the api if a new document or session is created
    if request.session.get(session_id):
        req_session = request.session.get(session_id)
        req_session.setdefault('complete_files', 0)
        if req_session.get('documents'):
            request.session[session_id]['complete_files'] += 1
        if req_session.get("followup_sessions"):
            req_followups = []
            for followup in req_session.get("followup_sessions"): 
                followup = json.loads(followup)
                followup["followup_session"] = str(
                    followup.get('session_checkin'))
                followup_sessions.append(followup)
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
 
    documents = []
    return render(request, 'patient.html', 
        {'session': user_session, 
         'patient': decrypted_data,
         'documents': documents,
         'current_session_documents': req_session.get('documents'),
         'tomorrow': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
         'followup_sessions': followup_sessions,
        })

@login_required(redirect_field_name=None, login_url='/')
def end_session(request, session_id):
    data_key = request.POST.get("data_key")
    session = {
            "session_id": session_id,
            "session_shared": "3",
            "data_key": ""
    }
    session_updates = FIRE.updateSession(session).to_dict()
    delete_encrpted_data(data_key)
    if request.session.get(session_id):
        del request.session[session_id]
    return redirect('/sessions')

@login_required(redirect_field_name=None, login_url='/')
def create_session(request):
    """ Creates new session for a follow-up

    Redirects back to the patient page """
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
            "session_shared": "0",
            "session_checkin": d,
            "session_details": {
                "pain_scale": "",
                "pre_conditions": "",
                "symptoms": "",
                "symptoms_duration": ""
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
        new_session_json = json.dumps(new_session, sort_keys=True, indent=1,
                                        cls=DjangoJSONEncoder)
        send_to_topic(session_id, new_session_json, 
                    "New Session", session_updates.get('data_key'))
        if not request.session.get(session_id):
            request.session[session_id] = {}
        if not request.session[session_id].get('followup_sessions'):
            request.session[session_id].setdefault('followup_sessions',[])
        request.session[session_id]['followup_sessions'].append(new_session_json)
        return redirect(previous_page)


def hp_handle_404(request, exception):
    return render(request, '404.html', {'path' : request.build_absolute_uri()})

@login_required(redirect_field_name=None, login_url='/')
def update_data(request):
    order = request.POST.get('order')
    session_list = list_sessions(order)
    return HttpResponse(json.dumps(session_list, default=json_util.default), 
                        content_type='application/javascript')

@login_required(redirect_field_name=None, login_url='/')
def request_sharing(request):
    session = request.POST
    updates = FIRE.updateSession(session).to_dict()
    updates['session_checkin'] = updates['session_checkin'].strftime(
        DATE_FORMAT)
    send_to_topic(updates['session_id'], updates['session_shared'], 
                  updates['session_documents'])
    return HttpResponse(json.dumps(updates, default=json_util.default), 
                                   content_type='application/javascript')


########################
# Supporting Functions #
########################
def list_sessions(order='desc'):
    sessions = FIRE.openSessions(order=order)
    docs = sessions.stream()
    doc_list = []
    for doc in docs:
        d = doc.to_dict() 
        if isinstance(d['session_checkin'], datetime):
            d['session_checkin'] = d['session_checkin'].strftime(DATE_FORMAT)
        doc_list.append(d)
    return doc_list


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


def send_to_topic(topic_name, session_shared, session_documents, user_id=""):
    """ Sends a new message to an existing FirebaseMessaging topic """
    topic = topic_name
    message = Message(
        data={
            'session_id': topic_name,
            'session_shared': session_shared,
            'session_documents': json.dumps(session_documents),
            'user_id': user_id,
        },
        topic=topic,
    )
    response = send(message)
    return
