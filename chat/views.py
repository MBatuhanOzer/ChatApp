from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render

def index(request):
    pass

        

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
