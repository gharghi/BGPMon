from django.core.checks import translation
from django.shortcuts import render, redirect
from django.utils import translation
from django.views.generic import TemplateView
from django.views.generic.base import View


def setting(request):
    return render(request, 'setting/general.html')


class Setting(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'setting/general.html')


class ChangeLanguage(View):
    language_code = ''
    redirect_to = ''

    def get(self, request, *args, **kwargs):
        self.redirect_to = request.META.get('HTTP_REFERER')
        self.language_code = kwargs.get('language_code')
        translation.activate(self.language_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = self.language_code
        return redirect('/' + self.language_code)
