from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def inbox(request):
    return render(request, 'mail/inbox.html')


@login_required
def compose(request):
    return render(request, 'mail/compose.html')



