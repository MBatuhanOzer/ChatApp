from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import IntegrityError

from .models import User


login_required(login_url="/login", redirect_field_name=None)
def index(request):
    return render(request, "chat/index.html")

        
def login_view(request):
    """
    Logs in a user with given username and password. If the user is logged in
    successfully, the user is redirected to the index page. If the user is not
    logged in successfully, the user is given an error message.

    :param request: The request object
    :return: A HTTP response
    """
    if request.method == "POST":
        # Get the username and password from the request
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        if username is None or password is None:
            return render(request, "chat/login.html", {"error": "Username and password are required."})

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        # If the user is authenticated, log them in
        if user is not None:
            login(request, user)
            return render(request, "chat/index.html")
        else:
            return render(request, "chat/login.html", {"error": "Invalid username or password"})
    else:
        # If the request is a GET request, render the login page
        return render(request, "chat/login.html")


def register(request):
    """
    Registers a user with given username and password. If the user is
    registered successfully, the user is redirected to the index page. If the
    user is not registered successfully, the user is given an error message.

    :param request: The request object
    :return: A HTTP response
    """
    if request.method == "POST":
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        if username is None or password is None:
            return render(request, "chat/register.html", {"error": "Username and password are required."})

        # Try to create user if failed return an error
        try:
            user = User.objects.create_user(username=username, password=password)
        except IntegrityError:
            return render(request, "chat/register.html", {"error": "Username already taken."})

        # If the user is created, log them in
        if user is not None:
            login(request, user)
            return render(request, "chat/index.html")
        else:
            return render(request, "chat/register.html", {"error": "An error occurred while registering the user."})
        
    else:
        return render(request, "chat/register.html")
    

login_required(login_url="/login", redirect_field_name=None)
def logout_view(request):
    """
    Logs out the user and redirects them to the login page.

    :param request: The request object
    :return: A HTTP response
    """
    logout(request)
    return render(request, "chat/login.html")