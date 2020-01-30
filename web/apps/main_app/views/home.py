import time

from django.db.models import Count
from django.shortcuts import render

from web.apps.main_app.models import Asn, Prefix, Notifications, Stats


def home(request):
    asns = Asn.objects.filter(user=request.user).count()
    prefixes = Prefix.objects.filter(user=request.user).count()
    notifications = Notifications.objects.filter(user=request.user).count()
    notif_history = Notifications.objects.filter(user=request.user).values('time').annotate(count=Count('id'))
    stats = Stats.objects.values_list('update_time', flat=True).last()
    output = {
        'asns': asns,
        'prefixes': prefixes,
        'notifications': notifications,
        'notif_history': notif_history,
        'last_update': int(time.time() - stats)
    }
    return render(request, 'index.html', {'output': output})
