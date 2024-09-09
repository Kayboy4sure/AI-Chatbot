from django.shortcuts import render, redirect
from django.http import JsonResponse
from openai import OpenAI


from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Chat

from django.utils import timezone


openai_api_key = 'enter your api key'
client = OpenAI(api_key=openai_api_key)

def ask_openai(message):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "text"
        }
    )
    response = chat_completion.choices[0].message.content
    return response

# Create your views here.
@login_required(login_url='login')
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST['message']
        response = ask_openai(message)
        # response = message

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'response': response})
    
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')