from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from web.apps.main_app.models import Asn
from django.utils.translation import gettext as _


# @is_user_in_group('Customers')  # for authorization with group name
def setting(request):
    return render(request, 'setting/general.html')

class Setting(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'setting/general.html')


