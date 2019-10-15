from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from web.apps.main_app.models import Origins, Prefix
from web.apps.jwt_store.models import User
from web.apps.main_app.forms import AddOriginsForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _


def asn(request):
    return render(request, 'add_prefix/add_prefix.html')


class MakePrefixPolicy(TemplateView):

    # def get(self, request, *args, **kwargs):
    #     origins = Origins.objects.filter(prefix__user__id=request.user.id)
    #     prefix = Prefix.objects.filter(user__id=request.user.id)
    #     return render(request, 'add_prefix/list_origins.html', {'origins': origins, 'prefix': prefix})

    def post(self, request, *args, **kwargs):
        try:
            if request.POST.get('origin'):
                form = AddOriginsForm(request.POST)
                if form.is_valid():
                    form.instance.origin = request.POST['origin']
                    form.instance.save()
                else:
                    messages.error(request, form.errors)
                    return HttpResponseRedirect("/prefix/")
            else:
                in_bgp = request.POST.getlist('in_bgp')
                in_db = request.POST.getlist('in_db')
                for item in in_bgp:
                    form = AddOriginsForm(request.POST)
                    if form.is_valid():
                        form.instance.origin = item
                        form.instance.save()
                    else:
                        messages.error(request, form.errors)
                        return HttpResponseRedirect("/prefix/")

                for item in in_db:
                    form = AddOriginsForm(request.POST)
                    if form.is_valid():
                        form.instance.origin = item
                        form.instance.save()
                    else:
                        messages.error(request, form.errors)
                        return HttpResponseRedirect("/prefix/")
            messages.success(request, _('Origins have registered successfully'))
            return HttpResponseRedirect("/prefix/" + str(request.POST.getlist('prefix')[0]) + "/origins/")

        except Exception as e:
            messages.error(request, e)
            return HttpResponseRedirect("/prefix/")


def list_origins(request, id):
    origins = list(Origins.objects.filter(prefix__id=id))
    prefix = Prefix.objects.filter(id=id).values_list('prefix', flat=True)[0]
    creator = User.objects.filter(prefix__id=id).values_list('username', flat=True)[0]
    if request.user.is_authenticated and request.user.username == creator:
        return render(request, 'add_prefix/list_origins.html', {'origins': origins, 'prefix': prefix})

    else:
        messages.error(request, _('There is no result'))
        return HttpResponseRedirect("/prefix/")


def delete_origin(request, id):
    origins_object = get_object_or_404(Origins, id=id)
    prefix = Prefix.objects.filter(origins__id=id).values_list('id', flat=True)[0]
    creator = User.objects.filter(prefix__id=prefix).values_list('username', flat=True)[0]
    prefix = prefix
    if request.user.is_authenticated and request.user.username == creator:
        origins_object.delete()
        messages.success(request, _("Originate ASN deleted successfully"))
        return HttpResponseRedirect("/prefix/" + str(prefix) + "/origins/")
