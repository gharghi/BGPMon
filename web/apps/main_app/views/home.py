from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from web.apps.main_app.models import Asn, Prefix, Notifications

# @is_user_in_group('Customers')  # for authorization with group name
def home(request):
    asns = Asn.objects.filter(user= request.user).count()
    prefixes = Prefix.objects.filter(user= request.user).count()
    notifications = Notifications.objects.filter(user__id=request.user.id).count()
    return render(request, 'index.html', {'asns':asns, 'prefixes':prefixes, 'notifications':notifications})
