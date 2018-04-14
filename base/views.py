from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import auth
from django.contrib import messages
from .models import Account, MailGun, Setting, Pgpkey
from .forms import MailGunForm, PgpKeyForm
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, get_list_or_404
from utils.mailgun import send_mail, get_mail
from mail.models import Mail
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.core import serializers


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
            if not user.initialized:
                return redirect('generate_key')
            else:
                return redirect('unlock')
        else:
            messages.warning(request, 'Username/Password is not valid!')
            return redirect('login')
    else:
        return render(request, 'base/login.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('inbox')
    if request.method == "POST":
        sign_up, created = Setting.objects.get_or_create(task='S')
        if sign_up.active:
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
                messages.warning(request, "Username is not available!")
                return redirect('signup')
            messages.success(request, 'Account created successfully!')
            return redirect('login')
        else:
            messages.warning(request, 'Signup is disabled!')
        return redirect('signup')
    else:
        return render(request, 'base/signup.html')


@login_required
def generate_key(request):
    """
    Handle and save pgp public key
    :param request:
    :return:
    """
    if request.user.initialized:
        return redirect('inbox')
    if request.method == 'POST':
        pgp_form = PgpKeyForm(request.POST)
        if pgp_form.is_valid():
            pgp = pgp_form.save(commit=False)
            pgp.user = request.user
            pgp.save()
            user = Account.objects.get(username=request.user.username)
            user.initialized = True
            user.save()
            return HttpResponse("success")
        else:
            return HttpResponse(pgp_form.errors, content_type='application/json')

    return render(request, 'base/generate_key.html')


@login_required
def unlock(request):
    """
    Unlock mailbox
    :param request:
    :return:
    """
    if request.content_type == 'application/json':
        pgp = get_list_or_404(Pgpkey, user=request.user)
        data = serializers.serialize('json', pgp)
        return HttpResponse(data, content_type='application/json')
    return render(request, 'base/unlock.html')


@login_required
def settings(request):
    mailgun = MailGun.objects.filter(user=request.user)
    sign_up, created = Setting.objects.get_or_create(task='S')
    users = Account.objects.all()
    return render(request, 'base/settings.html', {'mailgun': mailgun, 'users': users, 'signup': sign_up})


@login_required
def signup_settings(request):
    if request.user.is_admin:
        if request.method == 'POST':
            sign_up = Setting.objects.get(task='S')
            if request.POST.get('enable'):
                sign_up.active = False
            elif request.POST.get('disable'):
                sign_up.active = True
            sign_up.save()
        return redirect('settings')

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


def cron_send_mail(request):
    """
    Cron endpoint for sending queued mail
    :param request:
    :return:
    """
    send_mail()
    return HttpResponse("Bugs Bunny!")


def cron_check_mail(request):
    """
    Cron endpoint for checking new stored email
    :param request:
    :return:
    """
    get_mail()
    return HttpResponse("Bunny")


def cron_delete_trash(request):
    """
    Cron endpoint for deleting 30 days old trash mails
    :param request:
    :return:
    """
    month = datetime.today() - timedelta(days=30)
    mails = Mail.objects.filter(state='T', updated_at__lte=month)
    mails.delete()
    return HttpResponse("Nuked")



