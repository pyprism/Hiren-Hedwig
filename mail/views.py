from django.shortcuts import render


def inbox(request):
    return render(request, 'mail/inbox.html')
