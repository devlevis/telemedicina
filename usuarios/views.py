from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required

# Create your views here.
def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        coonfirmar_senha = request.POST.get('confirmar_senha')
        
        if senha != coonfirmar_senha:
            messages.add_message(request, constants.ERROR, "O campo 'Senha' e 'Confirmar senha' devem ser iguais")
            return redirect('/usuarios/cadastro')
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, "A senha deve ter no mínimo 6 dígitos")
            return redirect('/usuarios/cadastro')
        
        users = User.objects.filter(username=username)
        print(users.exists())
        
        if users.exists():
         messages.add_message(request, constants.ERROR, "Já existe um usuário com esse username")
         return redirect('/usuarios/cadastro')
                
        user = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )
        
        return redirect('/usuarios/login')
    

def login_view(request):
    if request.method == "GET":
        print(request.user)
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        user = auth.authenticate(request, username=username, password=senha)
        
        if user:
            auth.login(request, user)
            return redirect('/pacientes/home')
        
        messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos')
        return redirect('/usuarios/login')
    
def sair(request):
    auth.logout(request)
    return redirect('/usuarios/login')