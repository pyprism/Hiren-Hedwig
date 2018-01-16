from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import auth
from django.contrib import messages
from .models import Account, MailGun
from .forms import MailGunForm
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from hiren.settings import SIGNUP


def login(request):
    """
    Handles authentication
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        return redirect('inbox')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect('inbox')
        else:
            messages.error(request, 'Username/Password is not valid!')
            return redirect('login')
    else:
        return render(request, 'base/login.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('inbox')
    if request.method == "POST":
        if SIGNUP == 'True':
            username = request.POST.get('username')
            password = request.POST.get('password')
            count = Account.objects.count()
            acc = Account(username=username, password=make_password(password))
            if count == 0:
                acc.is_admin = True
            else:
                pass
            try:
                acc.save()
            except IntegrityError:
                messages.error(request, "username is not available!")
                return redirect('signup')
            messages.success(request, 'Account created successfully!')
        else:
            messages.error(request, 'Signup is disabled!')
        return redirect('signup')
    else:
        return render(request, 'base/signup.html')


@login_required
def settings(request):
    mailgun = MailGun.objects.filter(user=request.user)
    users = Account.objects.all()
    return render(request, 'base/settings.html', {'mailgun': mailgun, 'users': users})


@login_required
def create_domain(request):
    """
    Add Mailgun domain name, private api key
    :param request:
    :return:
    """
    if request.method == 'POST':
        mailgun_form = MailGunForm(request.POST)
        if mailgun_form.is_valid():
            mailgun = mailgun_form.save(commit=False)
            mailgun.user = request.user
            mailgun.save()
            messages.success(request, "New Domain Added!", extra_tags='mailgun')
        else:
            messages.error(request, mailgun_form.errors, extra_tags='mailgun')
        return redirect('settings')
    return render(request, 'base/create_domain.html')


@login_required
def update_domain(request, pk):
    """
    Update domain info
    :param request:
    :param pk: database pk
    :return:
    """
    mailgun_obj = get_object_or_404(MailGun, user=request.user, pk=pk)
    if request.method == 'POST':
        mailgun_form = MailGunForm(request.POST, instance=mailgun_obj)
        if mailgun_form.is_valid():
            mailgun = mailgun_form.save(commit=False)
            mailgun.user = request.user
            mailgun.save()
            messages.success(request, "Information Updated", extra_tags='mailgun')
        else:
            messages.error(request, mailgun_form.errors, extra_tags='mailgun')
        return redirect('update_domain', pk=pk)
    return render(request, 'base/update_domain.html', {'mailgun': mailgun_obj})


@login_required
def delete_domain(request, pk):
    """
    Nuke domain  :D
    :param request:
    :param pk: db primary key
    :return:
    """
    mailgun_obj = get_object_or_404(MailGun, user=request.user, pk=pk)
    mailgun_obj.delete()
    messages.success(request, 'Domain Deleted!')
    return redirect('settings')


@login_required
def create_user(request):
    """
    Create non-admin user
    :param request:
    :return:
    """
    if request.user.is_admin:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            acc = Account(username=username, password=make_password(password))
            try:
                acc.save()
            except IntegrityError:
                messages.error(request, "username is not available!")
                return redirect('create_user')
            messages.success(request, 'Account created successfully!')
            return redirect('create_user')
        return render(request, 'base/create_user.html')


@login_required
def update_user(request, username):
    """
    update password
    :param request:
    :param username:
    :return:
    """
    if request.user.is_admin:
        if request.method == 'POST':
            user = get_object_or_404(Account, username=username)
            user.set_password(request.POST.get('password'))
            user.save()
            messages.success(request, 'Password updated.')
            return redirect('update_user', username=username)
        return render(request, 'base/update_user.html')

