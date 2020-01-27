from django.shortcuts import render

from Crypto import Random
from Crypto.PublicKey.RSA import generate

# Create your views here.
# Encryption/Decryption logic from here
# https://stackoverflow.com/questions/30056762/rsa-encryption-and-decryption-in-python
def index(request):
    random_generator = Random.new().read
    keys = generate(1024, random_generator) 
    return render(request, 'index.html', {'keys': keys})