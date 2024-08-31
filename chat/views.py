from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotFound
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError

from .models import User, Chat, Message
from .consumers import ChatConsumer


@login_required(login_url="/login", redirect_field_name=None)
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
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

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
            return HttpResponseRedirect(reverse("index"))
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

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

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
            return HttpResponseRedirect(reverse("index"))
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
    return HttpResponseRedirect(reverse("login"))

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Chat

def chat(request, chat_id):
    """
    Renders the chat page.

    :param request: The request object
    :param chat_id: The ID of the chat
    :return: A HTTP response
    """
    chat = Chat.objects.filter(id=chat_id).first()

    # Check if chat exists; if not, check for the participants
    if not chat:
        user2_id = request.GET.get('user2_id')  # Assuming you get user2_id from a GET parameter

        if user2_id:
            try:
                user2 = User.objects.get(id=user2_id)
                # Create the chat if the participants are valid
                if request.user != user2:  # Ensure user is not creating a chat with themselves
                    chat = Chat.objects.create()
                    chat.participants.add(request.user, user2)
                    chat.save()
                else:
                    return HttpResponseForbidden("Cannot create a chat with yourself.")
            except User.DoesNotExist:
                return HttpResponseForbidden("Invalid user.")
        else:
            return HttpResponseForbidden("No chat found and no user specified to create a chat.")

    # Check if the user is a participant in the chat
    if request.user not in chat.participants.all():
        return HttpResponseForbidden("You are not part of this chat.")

    return render(request, "chat/chat.html", {"chat": chat})


@login_required(login_url="/login", redirect_field_name=None)
def search_users(request):
    '''
    Searches for users with the given query.

    :param request: The request object
    :return: A JSON response
    '''
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    user_list = [{'id': user.id, 'username': user.username} for user in users]
    return JsonResponse(user_list, safe=False)

@login_required(login_url="/login", redirect_field_name=None)
def start_chat(request, user2_id):
    '''
    Starts a new chat with the given user.

    :param request: The request object
    :param user2_id: The ID of the user to start the chat with
    :return: A HTTP response
    '''
    user2 = User.objects.get(id=user2_id)
    if user2 is None:
        return HttpResponseNotFound("User not found")
    chat_id = ChatConsumer.get_chat_id(user1_id=request.user.id, user2_id=user2.id)
    return HttpResponseRedirect(reverse('chat', args=[chat_id]))