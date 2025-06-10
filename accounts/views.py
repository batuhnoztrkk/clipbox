from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # login sayfasına yönlendir
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Kullanıcıyı oturum açmış yap
            return redirect('home')  # Başarılı giriş sonrası yönlendirme (örnek: ana sayfa)
        else:
            messages.error(request, 'Kullanıcı adı veya şifre yanlış.')

    return render(request, 'accounts/login.html')