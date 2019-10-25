from django.db.models import Count
from django.shortcuts import render, redirect
from web.apps.main_app.models import Asn, Prefix, Notifications

# @is_user_in_group('Customers')  # for authorization with group name
def home(request):
    asns = Asn.objects.filter(user= request.user).count()
    prefixes = Prefix.objects.filter(user= request.user).count()
    notifications = Notifications.objects.filter(user=request.user).count()
    notif_history = Notifications.objects.filter(user=request.user).values('time').annotate(count=Count('id'))
    output = {
        'asns': asns,
        'prefixes': prefixes,
        'notifications': notifications,
        'notif_history': notif_history
    }
    return render(request, 'index.html', {'output': output})
