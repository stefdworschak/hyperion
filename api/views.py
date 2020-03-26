import io
import json 
import os

from django.shortcuts import render

from Cryptodome import Random
from Cryptodome.PublicKey.RSA import generate
from Cryptodome.Hash import SHA256

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import firebase_admin
from firebase_admin import storage
from firebase_admin import credentials

import tempfile

cred = credentials.Certificate(settings.FCM_CREDENTIALS)
APP = firebase_admin.initialize_app(cred, { 
    'storageBucket': 'hyperion-260715.appspot.com',
    })


# Create your views here.
# Encryption/Decryption logic from here
# https://stackoverflow.com/questions/30056762/rsa-encryption-and-decryption-in-python
def index(request):
    random_generator = Random.new().read
    keys = generate(1024, random_generator) 
    return render(request, 'index.html', {'keys': keys})


def hash_page(request):
    return render(request, 'hash.html')


# Firestore storage reference:
# https://stackoverflow.com/questions/49526753/upload-image-file-to-firebase-in-python
# https://stackoverflow.com/questions/42956250/get-download-url-from-file-uploaded-with-cloud-functions-for-firebase
# https://firebase.google.com/docs/storage/admin/start#google_cloud_storage_client_libraries
# https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
def store_file_in_bucket(file):
    """ Temporarily save the uploaded file and store it in the Firebase bucket

    Returns the path to the file"""
    path = default_storage.save(file.name, ContentFile(file.read()))
    bucket = storage.bucket(app=APP)
    blob = bucket.blob(file.name)
    blob.upload_from_filename(path)
    return path

def create_hash_string(byte_object):
    """Create hash from byte object

    Returns hash as hex string"""
    sha256 = SHA256.new()
    sha256.update(byte_object)
    return sha256.hexdigest()


def hash(request):
    """Create a new hash of a string or file and store it in a Firestore bucket

    Returns hash as hex string to webpage"""
    if request.FILES is None:
        string = request.POST.get('hash_string')
        hash_digest = create_hash_string(bytes(string, 'utf-8'))
    else:
        file = request.FILES.get('hash_file')
        path = store_file_in_bucket(file)
        #byte_file = io.BytesIO(file.file)
        #with open(path, 'rb') as read_file:
        #    byte_file = file.read()
        #print(byte_file)
        hash_digest = create_hash_string(file.file.getvalue())
        default_storage.delete(path)
    return render(request, 'hash_output.html', 
                  {'hash_object':hash_digest})
