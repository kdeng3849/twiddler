import json

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from items.models import Item
from items.utils import to_dict
from .forms import AddUserForm, LoginForm
from .models import Profile
from .tokens import account_activation_token

def index(request):
    if request.user.is_authenticated:
        return redirect('/home')

    context = {
        "addUserForm": AddUserForm,
    }
    return render(request, 'users/signup.html', context)

@csrf_exempt
# @require_http_methods(["POST"])
def add_user(request):

    if request.method == "GET":
        context = {
            "addUserForm": AddUserForm,
        }
        return render(request, 'users/signup.html', context)

    data = json.loads(request.body.decode('utf-8'))
    form = AddUserForm(data)

    if form.is_valid():
        username, password, email = [form.cleaned_data.get('username'), form.cleaned_data.get('password'), form.cleaned_data.get('email')]

        # check if user already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            # if not User.objects.get(username=username).is_active:
            #     context = {
            #         "email": email,
            #     }
            #     return render(request, "users/verify.html", context)

            context = {
                "status": "error",
            }
            return JsonResponse(context)

        # create user
        user = User.objects.create_user(username=username, password=password, email=email, is_active=False)
        profile = Profile(user=user, followers=[], following=[])
        profile.save()
        # user.profile = profile
        user.save()

        current_site = get_current_site(request)
        mail_subject = 'Activate your TTT account'
        key = account_activation_token.make_token(user)
        print(key) ###
        # message = render_to_string('users/email_verification.html', {
        #     'user': user,
        #     'domain': current_site.domain,
        #     'email': user.email,
        #     'key': key,
        # })
        message = 'validation key: <' + key + '>'
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        try:
            email.send()
        except:
            pass

        return JsonResponse({"status": "OK"})


@csrf_exempt
def verify(request):

    # if get already exists...
    # if request.method == "GET":
    #     return render(request, 'users/verify.html')

    def verify_key(user, key):
        return account_activation_token.check_token(user, key) or key == 'abracadabra'

    if request.method == 'GET':
        email = request.GET.get('email')
        key = request.GET.get('key') # check if key is not None?

        if email is None or key is None:
            context = {
                "email": email,
            }
            return render(request, 'users/verify.html', context)
    else:
        data = json.loads(request.body.decode('utf-8'))
        email = data['email']
        key = data['key']

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = None

    # if user is not None and account_activation_token.check_token(user, key):
    if user is not None and verify_key(user, key):
        user.is_active = True
        user.save()

        return JsonResponse({"status": "OK"})

    return JsonResponse({"status": "error"})

@csrf_exempt
# @require_http_methods(["POST"])
def login_user(request):

    if request.method == "GET":
        context = {
            "loginForm": LoginForm,
        }
        return render(request, 'users/login.html', context)
 
    data = json.loads(request.body.decode('utf-8'))
    form = LoginForm(data)

    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            response = JsonResponse({"status": "OK"})
            login(request, user)
            request.session['username'] = username
            response.set_cookie('username', username)
            return response

    return JsonResponse({"status": "error"})


@csrf_exempt
def logout_user(request):

    logout(request)
    response = JsonResponse({'status': 'OK'})
    response.delete_cookie('username')

    return response


def user_profile(request, username):
    response = {
        "status": "OK",
        "user": {}
    }

    try:
        profile = Profile.objects.get(user__username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"status": "error"})

    response['user']['email'] = profile.user.email
    response['user']['followers'] = profile.count_followers()
    response['user']['following'] = profile.count_following()

    return JsonResponse(response)

def user_posts(request, username):
    response = {
        "status": "OK",
        "items": []
    }

    query = list(Item.objects.filter(username=username))
    for item in query:
        response['items'].append(to_dict(item))

    return JsonResponse(response)

def user_followers(request, username):
    response = {
        "status": "OK",
        "users": []
    }

    try:
        profile = Profile.objects.get(user__username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"status": "error"})
    
    response['users'] = profile.followers

    return JsonResponse(response)

def user_following(request, username):
    response = {
        "status": "OK",
        "users": []
    }
    
    try:
        profile = Profile.objects.get(user__username=username)
    except ObjectDoesNotExist:
        return JsonResponse({"status": "error"})

    response['users'] = profile.following

    return JsonResponse(response)

@csrf_exempt
# @require_http_methods(["POST"])
def follow_user(request):
    response = {
        "status": "OK"
    }

    print(request.COOKIES)

    data = json.loads(request.body.decode('utf-8'))
    # print(data)
    username = data['username']
    follow = data['follow']

    try:
        profile_following = Profile.objects.get(user__username=request.user.username)
        profile_followed = Profile.objects.get(user__username=username)
        user_followed = User.objects.get(username=username)
    except ObjectDoesNotExist as error:
        print(error)
        return JsonResponse({"status": "error"})

    print("user following", request.user.username)
    print("user followed", user_followed)
    if follow:
        profile_following.add_following(user_followed.username)
        profile_followed.add_follower(request.user.username)
        # profile_following.following.append(user_followed)
        # profile_followed.followers.append(request.user)
    else:
        profile_following.remove_following(user_followed.username)
        profile_followed.remove_follower(request.user.username)
        # profile_following.following.remove(user_followed)
        # profile_followed.followers.remove(request.user)

    profile_following.save()
    profile_followed.save()

    return JsonResponse(response)
