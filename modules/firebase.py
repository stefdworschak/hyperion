import os
from datetime import datetime as dt

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class Firebase:

    def __init__(self, appname):
        
        cwd = os.getcwd()
        if (not len(firebase_admin._apps)):
            cred = credentials.Certificate(os.path.join(cwd,"modules", "hyperion-260715-firebase-adminsdk-5e36b-fa4a430b51.json"))
            firebase_admin.initialize_app(cred)
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

    def openSessions(self):
        users_ref = self.db.collection(u'checkins')
        return users_ref

    def updateSession(self, session):
        #try:
        doc_ref = self.db.collection(u'checkins').document(session['session_id'])
        doc_ref.update(session)
        updates = doc_ref.get()
        return updates
        #except Exception as e:
        #    return {}
    

    

