from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers


def terminator(request, obj, item=15, ajax=False):
    """
    Hasta la vista, baby ....  reusable paginator
    :param request:
    :param obj: db object
    :param item: optional number of item per page
    :param ajax:
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
    bugs = []
    if ajax:
        return bunny
    for i in bunny.object_list:
        hiren = {}
        hiren['id'] = i.id
        hiren['mail_from'] = i.mail_from
        hiren['mail_to'] = i.mail_to
        hiren['cc'] = i.cc
        hiren['bcc'] = i.bcc
        hiren['subject'] = i.subject
        hiren['body'] = i.body
        hiren['state'] = i.state
        hiren['emotional_attachment'] = i.emotional_attachment
        hiren['received_datetime'] = i.received_datetime
        hiren['created_at'] = i.created_at.strftime("%d/%m/%Y, %I:%M:%S %p")
        bugs.append(hiren)
    hiren = {"obj": bugs, "totalSize": paginator.count, "sizePerPage": item,
             "pageStartIndex": bunny.start_index(), "page": bunny.number}
    return hiren




