from datetime import datetime, timedelta
import io
import json 
import os
import requests
from uuid import uuid4

from django.shortcuts import render, redirect
from django.http import JsonResponse

from Cryptodome import Random
from Cryptodome.PublicKey.RSA import generate
from Cryptodome.Hash import SHA256

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.core.files.base import ContentFile

import firebase_admin
from firebase_admin import storage
from firebase_admin import credentials
from google.cloud.storage import Blob

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import modules.firebase as fb


cred = credentials.Certificate(settings.FCM_CREDENTIALS)
APP = firebase_admin.initialize_app(cred, { 
    'storageBucket': 'hyperion-260715.appspot.com',
    })
FIRE = fb.Firebase('hp')
CONTRACT_ENDPOINT = os.environ.get('CONTRACT_ENDPOINT')



@csrf_exempt
def validate_hashes(request):
    hashes = []
    try:
        data = json.loads(request.POST.get("data"))
        if isinstance(data['hashes'], str):
            data['hashes'] = json.loads(data['hashes'])
        contract_response = None
        contract_response = contract_interaction(
            data['data_key'], data['hashes'], data['action'])
        if contract_response is None:
            return JsonResponse({"status":505, "data":None})
        return JsonResponse({"status":200, "data":contract_response})
    except Exception as e:
        return JsonResponse({"status":505, "data":None})

def create_document(request):
    """ Creates a new Session Record document, hahes and stores the files
    on Firebase Storage 
    
    It also adds the new document records to the existing request.session to
    reused them accross views

    Redirects back to the patient page """
    file_hashes = []
    files = request.FILES
    data = request.POST

    # Create and hash Session Record
    d = json.dumps({
        'session_id': data.get('session_id'),
        'document_content': data.get('document_content'),
        'document_content': data.get('document_content'),
        'patient_diagnosis': data.get('patient_diagnosis'),
        'patient_recommendation': data.get('patient_recommendation'),
        'num_documents': len(files)
    })
    byte_object = bytes(d , 'utf-8')
    file_hash = hash_and_store_file(byte_object=byte_object, extension=".json", 
                                    attachment=False)
    f = {
        "document_name": "Session Record",
        "document_hash": file_hash,
        "document_type": ".json",
    }
    file_hashes.append(f)

    # Hash and store attachments
    if files is not None:
        for file in files:
            ext = "." + files[file].name.split(".")[-1]
            file_hash = hash_and_store_file(byte_object=files[file],
                                            extension=ext, attachment=True)
            f = {
                "document_name": "".join(files[file].name.split(".")[:-1]),
                "document_hash": file_hash,
                "document_type": ext,
            }
            file_hashes.append(f)

    # Save hashes on the distributed ledger
    contract_response = contract_interaction(
            data_key=data.get('data_key'),
            hashes=file_hashes,
            action="addMultiple"
            )

    if contract_response is None:
        messages.error(request, "Could add documents to distributed ledger. Please try again or contact your administrator")
    else:
        # Store documents in FirebaseFirestore
        session = {
            "session_id": data.get('session_id'),
            "session_documents": file_hashes,
            "session_content": d,
        }
        updates = FIRE.updateSession(session).to_dict()

    # Add document records to session to reuse on patient page
    if not request.session.get(data.get('session_id')):
        request.session[data.get('session_id')] = {}
    request.session[data.get('session_id')].update({"documents": file_hashes})
    return redirect(f"/sessions/patient/{data.get('session_id')}")


def hash_and_store_file(byte_object, extension, attachment=False):
    """ Creates a file_hash and stores the file in a bucket in FirebaseStorage 
    
    Returns the file_hash """
    if not attachment:
        file_hash = create_hash_string(byte_object)
        store_file_in_bucket(byte_object.decode('utf-8'), file_hash+".json")
        print(str(byte_object.decode('utf-8')))
    else:
        file_hash = create_hash_string(byte_object.file.getvalue())
        store_file_in_bucket(byte_object.file.getvalue(), file_hash+extension)
    return file_hash


def create_hash_string(byte_object):
    """Create hash from byte object

    Returns hash as hex string"""
    sha256 = SHA256.new()
    sha256.update(byte_object)
    return sha256.hexdigest()


# Firestore storage reference:
# https://stackoverflow.com/questions/49526753/upload-image-file-to-firebase-in-python
# https://stackoverflow.com/questions/42956250/get-download-url-from-file-uploaded-with-cloud-functions-for-firebase
# https://firebase.google.com/docs/storage/admin/start#google_cloud_storage_client_libraries
# https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
def store_file_in_bucket(filecontent, filename):
    """ Temporarily save the uploaded file and store it in the Firebase bucket

    Returns the path to the file"""
    path = default_storage.save(filename, ContentFile(filecontent))
    bucket = storage.bucket(app=APP)
    blob = bucket.blob(filename)
    new_token = uuid4()
    metadata  = {"firebaseStorageDownloadTokens": str(new_token)}
    blob.metadata = metadata
    blob.upload_from_filename(path)
    default_storage.delete(path)
    return path


def get_download_link(file_hash, file_type):
    bucket = storage.bucket(app=APP)
    blob = bucket.blob(file_hash+file_type)

    expiration = datetime.now() + timedelta(days=1)
    url = blob.generate_signed_url(expiration=expiration, 
                                   #bucket_bound_hostname='hyperion-health.net',
                                    version='v4')
    return url

def contract_interaction(data_key, hashes, action):
    data = json.dumps({
        "user": data_key,
        "hashes": [h.get('document_hash') for h in hashes],
        "action": action
    })
    resp = requests.post(CONTRACT_ENDPOINT, {"data": data})
    if resp.status_code == 200:
        return resp.json()
    else:
        return None       
