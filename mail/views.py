from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MailForm
from base.models import MailGun
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Attachment


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
            mailgun = get_object_or_404(MailGun, name=domain, user=request.user)
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



