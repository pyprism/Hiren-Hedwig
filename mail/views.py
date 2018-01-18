from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MailForm
from base.models import MailGun
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .models import Attachment, Mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def inbox(request):
    return render(request, 'mail/inbox.html')


@login_required
def compose(request):
    """
    Add new email to system
    :param request:
    :return:
    """
    if request.method == 'POST':
        files = request.FILES.getlist('attachment')
        compose = MailForm(request.POST)
        if compose.is_valid():
            domain_str = request.POST.get('mail_from')
            domain = domain_str.split('@')[1]  # extract domain name for mailgun api
            try:
                mailgun = MailGun.objects.get(name=domain, user=request.user)
            except ObjectDoesNotExist:
                messages.warning(request, "Your mail's domain " + domain + " is not found in settings!")
                return redirect('compose')
            compose_obj = compose.save(commit=False)
            compose_obj.domain = mailgun
            compose_obj.user = request.user
            if len(files) > 0:
                compose_obj.emotional_attachment = True
            if request.POST.get('send'):  # detect which submit was clicked
                compose_obj.state = 'Q'
                compose_obj.save()
                messages.success(request, 'Mail has been sent.')
            if request.POST.get('draft'):
                compose_obj.state = 'D'
                compose_obj.save()
                messages.success(request, 'Mail saved as draft.')
            if len(files) > 0:
                for file in files:
                    bunny = Attachment(
                        user=request.user,
                        mail=compose_obj,
                        file_name=file.name,
                        attachment=file
                    )
                    bunny.save()
        else:
            messages.warning(request, compose.errors)
        redirect('compose')
    return render(request, 'mail/compose.html')


@login_required
def sent(request):
    """
    List of sent mails
    :param request:
    :return:
    """
    mails = Mail.objects.filter(user=request.user, state='S').order_by('-updated_at')
    paginator = Paginator(mails, 20)
    page = request.GET.get('page')
    try:
        bunny = paginator.page(page)
    except PageNotAnInteger:
        # If bunny is not an integer, deliver first page.
        bunny = paginator.page(1)
    except EmptyPage:
        bunny = paginator.page(paginator.num_pages)
    return render(request, 'mail/mail_list.html', {'mails': bunny, 'title': 'Sent Mail'})


@login_required
def draft(request):
    """
    List of draft mails
    :param request:
    :return:
    """
    mails = Mail.objects.filter(user=request.user, state='D').order_by('-updated_at')
    paginator = Paginator(mails, 20)
    page = request.GET.get('page')
    try:
        bunny = paginator.page(page)
    except PageNotAnInteger:
        # If bunny is not an integer, deliver first page.
        bunny = paginator.page(1)
    except EmptyPage:
        bunny = paginator.page(paginator.num_pages)
    return render(request, 'mail/mail_list.html', {'mails': bunny, 'title': 'Draft Mail'})


@login_required
def queue(request):
    """
    List of queue mails
    :param request:
    :return:
    """
    mails = Mail.objects.filter(user=request.user, state='Q').order_by('-created_at')
    paginator = Paginator(mails, 20)
    page = request.GET.get('page')
    try:
        bunny = paginator.page(page)
    except PageNotAnInteger:
        # If bunny is not an integer, deliver first page.
        bunny = paginator.page(1)
    except EmptyPage:
        bunny = paginator.page(paginator.num_pages)
    return render(request, 'mail/mail_list.html', {'mails': bunny, 'title': 'Queue Mail'})


@login_required
def trash(request):
    """
    List of trash mails
    :param request:
    :return:
    """
    mails = Mail.objects.filter(user=request.user, state='T').order_by('-updated_at')
    paginator = Paginator(mails, 20)
    page = request.GET.get('page')
    try:
        bunny = paginator.page(page)
    except PageNotAnInteger:
        # If bunny is not an integer, deliver first page.
        bunny = paginator.page(1)
    except EmptyPage:
        bunny = paginator.page(paginator.num_pages)
    return render(request, 'mail/mail_list.html', {'mails': bunny, 'title': 'Trash Box'})



