import io
import json 
import os
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

import tempfile
from healthcare.views import contract_interaction

from django.views.decorators.csrf import csrf_exempt, csrf_protect

cred = credentials.Certificate(settings.FCM_CREDENTIALS)
APP = firebase_admin.initialize_app(cred, { 
    'storageBucket': 'hyperion-260715.appspot.com',
    })

@csrf_exempt
def validate_hashes(request):
    hashes = []
    print(request.POST)
    print(request.POST.get("data"))
    try:
        data = json.loads(request.POST.get("data"))
        print("POST DATA")
        print(data)
        contract_response = None
        contract_response = contract_interaction(data['data_key'], data['hashes'], data['action'])
        if contract_response is None:
            print("CONTRACT RESPONSE NONE")
            return JsonResponse({"status":505, "data":None})
        return JsonResponse({"status":200, "data":contract_response})
    except:
        print("WRONG DATA PROVIDED")
        return JsonResponse({"status":505, "data":None})

def create_document(request):
    file_hashes = []
    files = request.FILES
    data = request.POST
    # TODO: Add file encryption
    # 1) Hash file contents
    # 2) Store file with hash as name of firestore
    # 3) Update session information
    # 3) Udate session information in firestore
    # 4) Render new document
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
    request.session[data.get('session_id')] = file_hashes
    return redirect(f"/hp/patient/{data.get('session_id')}")

def hash_and_store_file(byte_object, extension, attachment=False):
    if not attachment:
        file_hash = create_hash_string(byte_object)
        store_file_in_bucket(byte_object.decode('utf-8'), file_hash+".json")
        print(str(byte_object.decode('utf-8')))
    else:
        file_hash = create_hash_string(byte_object.file.getvalue())
        store_file_in_bucket(byte_object.read(), file_hash+extension)
    return file_hash


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


def create_hash_string(byte_object):
    """Create hash from byte object

    Returns hash as hex string"""
    sha256 = SHA256.new()
    sha256.update(byte_object)
    return sha256.hexdigest()
