from django.shortcuts import render, redirect, reverse
from accounts.forms import UserLoginForm, UserRegistrationForm


from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse('sessions_index'))

    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)

        if login_form.is_valid():
            user = auth.authenticate(username=request.POST.get('username'),
                                     password=request.POST.get('password'))
            if user:
                auth.login(user=user, request=request)
                return redirect(reverse('sessions_index'))
                messages.success(request, "You have successfully logged in!")
            else:
                messages.error(request, 'Username and password combination is wrong.')
    else:
        login_form = UserLoginForm()
    return render(request, 'index.html', {'login_form': login_form})


@login_required
def logout(request):
    """ Log user out """
    auth.logout(request)
    messages.success(request, "You have been logged out!")
    return redirect(reverse('accounts_index'))
