import time, datetime
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import register

from web.apps.main_app.models import Notifications, Prefix, Asn

@login_required
# @is_user_in_group('Customers')  # for authorization with group name
def view_notifications(request):
    enddate = int(time.time())
    startdate = enddate - 86400
    notifications = Notifications.objects.filter(time__range=[startdate, enddate]).filter(user__id=request.user.id)
    return render(request, 'notifications/list_notifications.html', {'notifications': notifications})

@register.filter
def to_date(text):
    return time.strftime('%H:%M:%S %Y-%m-%d', time.localtime(text))

@register.filter
def status(text):
    code = {
        1:"Has been transited",
        2:"Has been hijacked",
        3: "Transiting",
        4:"Hijacking",
        0:"Path has been changed",
    }
    return code[text]
