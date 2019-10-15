from django.core.checks import translation
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from web.apps.main_app.models import Asn
from django.utils.translation import gettext as _
from django.views.generic.base import View
from django.utils import translation

# @is_user_in_group('Customers')  # for authorization with group name
def setting(request):
    return render(request, 'setting/general.html')

class Setting(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'setting/general.html')




class ChangeLanguage(View):
    language_code = ''
    redirect_to   = ''

    def get(self, request, *args, **kwargs):
        self.redirect_to   = request.META.get('HTTP_REFERER')
        self.language_code = kwargs.get('language_code')
        translation.activate(self.language_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = self.language_code
        return redirect('/' + self.language_code)