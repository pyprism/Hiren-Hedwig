from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MailForm
from base.models import MailGun
from django.shortcuts import get_object_or_404
from django.contrib import messages


@login_required
def inbox(request):
    return render(request, 'mail/inbox.html')


@login_required
def compose(request):
    if request.method == 'POST':
        files = request.FILES.getlist('attachment')
        if len(files) == 0:
            compose = MailForm(request.POST)
            if compose.is_valid():
                domain_str = request.POST.get('mail_from')
                domain = domain_str.split('@')[1]
                mailgun = get_object_or_404(MailGun, name=domain, user=request.user)
                compose_obj = compose.save(commit=False)
                compose_obj.domain = mailgun
                compose_obj.user = request.user
                compose_obj.state = 'Q'
                compose_obj.save()
                messages.success(request, 'Mail has been sent.')
            else:
                messages.warning(request, compose.errors)
        else:
            messages.warning(request, 'attachment!!')
        redirect('compose')
    return render(request, 'mail/compose.html')



