import os
from datetime import datetime as dt

from django.conf import settings

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class Firebase:

    def __init__(self, app):
        if (not len(firebase_admin._apps)):
            cred = credentials.Certificate(settings.FCM_CREDENTIALS)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.get_app()
        self.db = firestore.client()


    def insertSession(self, session):
        doc_ref = self.db.collection(u'checkins').document(session['session_id'])
        doc_ref.set({
            u'session_id' : session['session_id'],
            u'session_checkin' : dt.now(),
            u'session_shared' : 0,
            u'session_details' : session['session_details']
        })
        return True


    def openSessions(self, order='desc'):
        if order == 'desc':
            sort_by_direction = firestore.Query.DESCENDING
        else:
            sort_by_direction = firestore.Query.ASCENDING
        users_ref = self.db.collection(u'checkins').order_by(
            u'session_checkin', direction=sort_by_direction)
        return users_ref


    def updateSession(self, session):
        """ Updates an existing FirebaseFirestore document 
        
        Returns updated document """
        doc_ref = self.db.collection(u'checkins').document(session['session_id'])
        doc_ref.update(session)
        updates = doc_ref.get()
        return updates



    def createSession(self, session):
        #try:
        doc_ref = self.db.collection(u'checkins').document(session['session_id'])
        doc_ref.set(session)
        updates = doc_ref.get()
        return updates
        #except Exception as e:
        #    return {}
    

    def findSession(self, session_id):
        collection = self.db.collection(u'checkins')
        session = collection.document(str(session_id)).get().to_dict()
        if session is None:
            return None
        
        session['session_checkin'] = session['session_checkin'].strftime(
            DATE_FORMAT)

        if session['session_shared'] != '2':
            return None
        return session

    

