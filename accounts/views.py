from django.shortcuts import render, redirect, reverse
from accounts.forms import UserLoginForm

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):
    """ Shows the login form and handle the user login flow """
    # Check if the user is authenticated and redirect to index if True
    if request.user.is_authenticated:
        return redirect(reverse('sessions_index'))

    # If POST data is present
    if request.method == 'POST':
        # send it to the form
        login_form = UserLoginForm(request.POST)

        # Check if the form is valid
        if login_form.is_valid():
            # Authenticate the user
            user = auth.authenticate(username=request.POST.get('username'),
                                     password=request.POST.get('password'))
            # If the user authentication is complete
            if user:
                # Log the user in, redirect to the patient sessions and
                # show success message
                auth.login(user=user, request=request)
                return redirect(reverse('sessions_index'))
                messages.success(request, "You have successfully logged in!")
            else:
                # Show error message if form is invalid
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
