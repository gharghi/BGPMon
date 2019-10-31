import time

from django.db.models import Func, F
from django.shortcuts import render
from django.template.defaultfilters import register
from django.db import connection

from web.apps.main_app.models import Notifications


def view_notifications(request):
    enddate = int(time.time())
    startdate = enddate - 86400
    # notifications = Notifications.objects.filter(time__range=[startdate, enddate]).filter(
    #     user__id=request.user.id).annotate(pathw = Func(F('path'),'group_concat')).order_by('time').reverse()
    cs = connection.cursor()
    query = "select id,prefix,asn,type,time,group_concat(path separator \"|\"),status from main_app_notifications where user_id = " + str(request.user.id) +" group by prefix,asn order by time desc"
    cs.execute(query)
    rows = cs.fetchall()
    return render(request, 'notifications/list_notifications.html', {'notifications': rows})


@register.filter
def to_date(text):
    return time.strftime('%H:%M:%S %Y-%m-%d', time.localtime(text))


@register.filter
def status(text):
    code = {
        1: "Has been transited",
        2: "Has been hijacked",
        3: "Transiting",
        4: "Hijacking",
        0: "Path has been changed",
    }
    return code[text]

@register.filter
def separate(text):
    path=[]
    for asn in text.split('|'):
        path.append(asn)
    return path

@register.filter
def path_summary(path):
    text = path.split(' ')
    return '... ' + str(text[-3]) + ' ' + str(text[-2]) + ' ' + str(text[-1])