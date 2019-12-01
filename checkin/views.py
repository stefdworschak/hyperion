from django.shortcuts import render,redirect
from random import randrange
from datetime import datetime as dt

# Create your views here.

def index(request):
    return render(request, 'checkin.html')

def checkin(request):
    randomID = randID(10,2)
    return render(request, 'checkin_success.html',{'randID':randomID})

def randID(length, type):
    randID = ""
    choices = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','x','y','z',
'1','2','3','4','5','6','7','8','9','0',
'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y','Z']
    num_choices = ['1','2','3','4','5','6','7','8','9','0']

    if type == 1:
        temp_choices = choices
    elif type == 2:
        temp_choices = num_choices
    else:
        #detault is all choices
        temp_choices = choices

    for i in range(length):
        rand = randrange(len(temp_choices) - 1)
        randID += temp_choices[rand]
    randID += str(dt.now().year + dt.now().month + dt.now().day + dt.now().hour + dt.now().minute + dt.now().second)

    return randID
