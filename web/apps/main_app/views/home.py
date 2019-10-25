from django.db.models import Count
from django.shortcuts import render, redirect
from web.apps.main_app.models import Asn, Prefix, Notifications

# @is_user_in_group('Customers')  # for authorization with group name
def home(request):
    asns = Asn.objects.filter(user= request.user).count()
    prefixes = Prefix.objects.filter(user= request.user).count()
    notifications = Notifications.objects.filter(user__id=request.user.id).count()
    notifications_count = Notifications.objects.filter(user__id=request.user.id).values('time').annotate(count=Count('id'))
    return render(request, 'index.html', {'asns':asns, 'prefixes':prefixes, 'notifications':notifications, 'notifications_count':notifications_count})
