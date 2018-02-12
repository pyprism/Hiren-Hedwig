from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MailForm
from base.models import MailGun
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .models import Attachment, Mail, Thread
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils.mailgun import get_mail


def terminator(request, obj, item=25):
    """
    Hasta la vista, baby ....  reusable paginator
    :param request:
    :param obj: db object
    :param item: optional number of item per page
    :return:
    """
    paginator = Paginator(obj, item)
    page = request.GET.get('page')
    try:
        bunny = paginator.page(page)
    except PageNotAnInteger:
        # If bunny is not an integer, deliver first page.
        bunny = paginator.page(1)
    except EmptyPage:
        bunny = paginator.page(paginator.num_pages)
    return bunny


@login_required
def inbox(request):
    """
    Get user inbox
    :param request:
    :return:
    """
    if request.GET.get('new'):  # check for new mail
        get_mail()
    mails = Thread.objects.filter(user=request.user).prefetch_related('mails').order_by('read', '-updated_at')
    bunny = terminator(request, mails, 15)
    return render(request, 'mail/inbox.html', {'mails': bunny, 'title': 'Inbox'})


@login_required
def inbox_details(request, pk):
    """
    wip
    :param request:
    :return:
    """
    thread = get_object_or_404(Thread.objects.prefetch_related('mails'), pk=pk, user=request.user)
    if not thread.read:
        thread.read = True
        thread.save()
    return render(request, 'mail/mail_thread.html', {'thread': thread})


@login_required
def thread_delete(request, thread_id, mail_id):
    """
    Handle mail/thread deletion
    :param request:
    :param thread_id:
    :param mail_id:
    :return:
    """
    mail = get_object_or_404(Mail, user=request.user, pk=mail_id)
    thread = get_object_or_404(Thread, user=request.user, pk=thread_id)
    thread.mails.remove(mail)
    if mail.emotional_attachment:
        Attachment.objects.filter(user=request.user, mail=mail).update(mail=None)
    mail.state = 'T'
    mail.save()
    if thread.mails.count() == 0:
        thread.delete()
        messages.success(request, 'Thread has been deleted.')
        return redirect('inbox')
    else:
        messages.success(request, 'Mail has been moved to trash.')
        return redirect('thread', pk=thread_id)


@login_required
def thread_reply(request, thread_id, mail_id):
    mail = get_object_or_404(Mail, user=request.user, pk=mail_id)
    return render(request, 'mail/thread_reply.html', {'mail': mail})


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
            if request.POST.get('draft'):
                compose_obj.state = 'D'
            compose_obj.save()
            if len(files) > 0:
                for file in files:
                    bunny = Attachment(
                        user=request.user,
                        mail=compose_obj,
                        file_name=file.name,
                        file_obj=file
                    )
                    bunny.save()
            if request.POST.get('send'):
                messages.success(request, 'Mail queued for sending.')
            if request.POST.get('draft'):
                messages.success(request, 'Mail saved as draft.')
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
    bunny = terminator(request, mails)
    return render(request, 'mail/mail_list.html', {'mails': bunny, 'title': 'Sent Mail'})


@login_required
def draft(request):
    """
    List of draft mails
    :param request:
    :return:
    """
    mails = Mail.objects.filter(user=request.user, state='D').order_by('-updated_at')
    bunny = terminator(request, mails)
    return render(request, 'mail/mail_list.html', {'mails': bunny, 'title': 'Draft Mail'})


@login_required
def queue(request):
    """
    List of queue mails
    :param request:
    :return:
    """
    mails = Mail.objects.filter(user=request.user, state='Q').order_by('-created_at')
    bunny = terminator(request, mails)
    return render(request, 'mail/mail_list.html', {'mails': bunny, 'title': 'Queue Mail'})


@login_required
def trash(request):
    """
    List of trash mails
    :param request:
    :return:
    """
    mails = Mail.objects.filter(user=request.user, state='T').order_by('-created_at')
    bunny = terminator(request, mails)
    return render(request, 'mail/mail_list.html', {'mails': bunny, 'title': 'Trash Box'})


@login_required
def mail_by_id(request, pk):
    """
    Get mail by id and return correct template based on mail type
    :param request:
    :param pk:
    :return:
    """
    mail = get_object_or_404(Mail, user=request.user, pk=pk)
    attachment = None
    if mail.emotional_attachment:
        attachment = get_list_or_404(Attachment, mail=mail, user=request.user)
    context = {'mail': mail, 'attachment': attachment}
    if mail.state == 'D':
        return render(request, 'mail/draft_edit.html', context)
    elif mail.state == 'Q':
        return render(request, 'mail/queue_readonly.html', context)
    elif mail.state == 'T':
        return render(request, 'mail/trash_delete.html', context)
    elif mail.state == 'S':
        return render(request, 'mail/sent_mail_readonly.html', context)
    elif mail.state == 'R':
        mail.is_read = True
        mail.save()
        return render(request, 'mail/inbox_details.html', context)


@login_required
def draft_edit(request, pk):
    """
    Handle draft edit form
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        files = request.FILES.getlist('new_attachment')
        instance = get_object_or_404(Mail, pk=pk, user=request.user)
        if request.POST.get('delete'):
            if instance.emotional_attachment:  # discard previous files
                Attachment.objects.filter(mail=instance, user=request.user).update(mail=None)
            instance.delete()
            messages.success(request, 'Draft has been discarded!')
        elif request.POST.get('draft') or request.POST.get('send'):
            mail_form = MailForm(request.POST, instance=instance)
            if mail_form.is_valid():
                mail = mail_form.save(commit=True)
                if len(files) > 0:  # if user send new attachment
                    if instance.emotional_attachment:
                        Attachment.objects.filter(mail=instance, user=request.user).update(mail=None)
                    for file in files:
                        bunny = Attachment(
                            user=request.user,
                            mail=instance,
                            file_name=file.name,
                            file_obj=file
                        )
                        bunny.save()
                    mail.emotional_attachment = True
                if request.POST.get('send'):
                    mail.state = 'Q'
                    messages.success(request, "Mail queued for sending.")
                else:
                    messages.success(request, "Draft updated.")
                mail.save()

    return redirect('draft')


@login_required
def trash_delete(request, pk):
    """
    Delete 'trash' mail by id
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        if request.POST.get('delete'):
            bunny = get_object_or_404(Mail, pk=pk, user=request.user)
            if bunny.emotional_attachment:
                Attachment.objects.filter(user=request.user, mail=bunny).update(mail=None)
            bunny.delete()
            messages.success(request, 'Mail has been deleted.')
        return redirect('trash')


@login_required
def sent_delete(request, pk):
    """
    move sent mail to trash
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        if request.POST.get('delete'):
            bunny = get_object_or_404(Mail, pk=pk, user=request.user)
            bunny.state = 'T'
            bunny.save()
            messages.success(request, 'Mail Moved To Trash.')
        return redirect('sent')



