from typing import Type
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from projects.models import *
from .models import *
from .forms import CreateUserForm, EditUserForm, CreateTechnologyForm, SendMessageForm
from .utils import search_profiles, pagination_profiles
from django.contrib.auth.models import AnonymousUser

# Create your views here.


def login_profile(request):
    page = 'login'
    context = {
        'page': page,
    }

    # When we are logged and use 'login' URL switch to main site with users1
    if request.user.is_authenticated:
        return redirect('profiles')

    # request.POST method send a JSON file with csrf_token and data to validation by a server.
    if request.method == 'POST':
        print(f'Login Token equals: {request.POST}')
        username = request.POST['username']
        password = request.POST['password']

        # Check if the user exists
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, f"Nie znaleziono użytkownika: {username}.")

        try:
            user = authenticate(request, username=user, password=password)
        except UnboundLocalError:
            messages.error(request, "Logowanie niepomyślne")
            return redirect('login')

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'profiles')
        else:
            messages.error(
                request, "Logowanie niepomyślne.")

    return render(request, 'users/login-and-register.html', context)


def logout_profile(request):
    # Logout the user
    messages.info(request, f"Użytkownik {request.user} wylogowany pomyślnie.")
    logout(request)
    return redirect('profiles')


def register_profile(request):
    # Register new profile
    page = 'register'
    form = CreateUserForm()

    # If we use submit in register form
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            # Commit=False save user in function so we can late use login(request, user)
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(
                request, f"Użytkownik {user.username} utworzony pomyślnie.")

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('edit-account')
        else:
            messages.error(
                request, "Wystąpił błąd podczas rejestracji.")

    context = {'form': form, 'page': page}
    return render(request, 'users/login-and-register.html', context)


def profiles(request):
    # Show all profiles
    profiles, find_profile = search_profiles(request)
    pages_range, profiles = pagination_profiles(request, profiles, 3)

    context = {
        'profiles': profiles,
        'find_profile': find_profile,
        'pages_range': pages_range,
    }
    return render(request, 'users/profiles.html', context)


def userProfile(request, pk):
    # Show specific profile by id which we give in the endpoint
    profile = Profile.objects.get(id=pk)
    projects = Project.objects.filter(owner=profile)
    count = projects.count()
    main_technologies = profile.technology_set.exclude(description__exact='')
    tags_technologies = profile.technology_set.filter(description__exact='')

    context = {
        'profile': profile,
        'main_technologies': main_technologies,
        'tags_technologies': tags_technologies,
        'projects': projects,
    }

    return render(request, 'users/profile.html', context)


@login_required(login_url='login')
def user_account(request):
    profile = request.user.profile
    technologies = profile.technology_set.all()
    projects = profile.project_set.all()

    context = {
        'profile': profile,
        'technologies': technologies,
        'projects': projects,
    }

    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def edit_account(request):
    profile = request.user.profile
    form = EditUserForm(instance=profile)

    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            messages.success(request, "Edycja profilu przebiegła pomyślnie.")
            return redirect('account')

    context = {'form': form}

    return render(request, 'users/profile-form.html', context)

# Technology


@login_required(login_url='login')
def create_technology(request):
    profile = request.user.profile
    method = 'create'
    form = CreateTechnologyForm()

    if request.method == 'POST':
        form = CreateTechnologyForm(request.POST)
        if form.is_valid():
            technology = form.save(commit=False)
            technology.owner = profile
            technology.save()
            messages.success(
                request, f"Technologia {technology.name} dodana pomyślnie.")
            return redirect('account')

    context = {
        'method': method,
        'form': form,
    }

    return render(request, 'users/form-technology.html', context)


@login_required(login_url='login')
def update_technology(request, pk):
    profile = request.user.profile
    technology = profile.technology_set.get(id=pk)
    method = 'update'
    form = CreateTechnologyForm(instance=technology)

    if request.method == 'POST':
        form = CreateTechnologyForm(request.POST, instance=technology)
        if form.is_valid():
            technology.save()
            messages.success(
                request, "Edycja technologii przebiegła pomyślnie.")
            return redirect('account')

    context = {
        'method': method,
        'form': form,
    }

    return render(request, 'users/form-technology.html', context)


@login_required(login_url='login')
def delete_technology(request, pk):
    delete_type = 'Technologia'
    profile = request.user.profile
    technology = profile.technology_set.get(id=pk)
    if request.method == 'POST':
        technology.delete()
        messages.success(
            request, "Usuwanie technologii przebiegło pomyślnie.")
        return redirect('account')
    context = {'object': technology, 'delete_type': delete_type}
    return render(request, 'delete-template.html', context)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    msg_request = profile.recipient_msg.all()
    print(msg_request)
    unread_msg_count = msg_request.filter(is_read=False).count()
    context = {
        'msg_request': msg_request,
        'unread_msg_count': unread_msg_count,
    }
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def message(request, pk):
    profile = request.user.profile
    message = profile.recipient_msg.get(id=pk)
    if not message.is_read:
        message.is_read = True
        message.save()
    context = {'message': message}
    return render(request, 'users/message.html', context)


def create_message(request, pk):
    recipient = Profile.objects.get(id=pk)
    form = SendMessageForm

    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.full_name
                message.email = sender.email
            message.save()

            messages.success(
                request, f'Twoja wiadomość "{message.title}" została wysłana pomyślnie.')
            return redirect('user-profile', pk=recipient.id)

    context = {
        'recipient': recipient,
        'form': form
    }
    return render(request, 'users/send-message.html', context)
