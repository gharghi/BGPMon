import json
import urllib

from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from web.apps.main_app.models import Neighbors, Asn, Prefix, Origins
from web.apps.jwt_store.models import User
from web.apps.main_app.forms import AddNeighborsForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _


def asn(request):
    return render(request, 'asn/neighbors.html')


class MakeAsnPolicy(TemplateView):

    def get(self, request, *args, **kwargs):
        neighbors = Neighbors.objects.filter(asn__user__id=request.user.id)
        return render(request, 'asn/list_neighbors.html', {'neighbors': neighbors, 'asn': asn})

    def post(self, request, asn, *args, **kwargs):
        try:
            form = AddNeighborsForm(request.POST)
            if form.is_valid():
                lefts = request.POST.getlist('left_asn')
                rights = request.POST.getlist('right_asn')
                for item in lefts:
                    form = AddNeighborsForm(request.POST)
                    if form.is_valid():
                        form.instance.neighbor = item
                        form.instance.type = 1
                        form.instance.save()

                for item in rights:
                    form = AddNeighborsForm(request.POST)
                    if form.is_valid():
                        form.instance.neighbor = item
                        form.instance.type = 2
                        form.instance.save()
                messages.success(request, _('Neighbors have registered successfully'))
                return HttpResponseRedirect("/asn/" + str(asn) +"/neighbors/")

            else:
                messages.error(request, form.errors)
                return HttpResponseRedirect("/asn/")

        except Exception as e:
            messages.error(request, e)
            return HttpResponseRedirect("/asn/" + asn[0] +"/neighbors/")



def list_neighbors(request, asn):
    neighbors = {}
    neighbors['asn'] = asn
    neighbors['left'] = Neighbors.objects.filter(asn__user__id=request.user.id, asn__asn= asn, type= 1).distinct().values('id', 'neighbor')
    neighbors['right'] = Neighbors.objects.filter(asn__user__id=request.user.id, asn__asn= asn, type = 2).distinct().values('id', 'neighbor')
    return render(request, 'asn/list_neighbors.html', {'neighbors': neighbors})


def delete_neighbors(request, id):
    neighbor_object = get_object_or_404(Neighbors, id=id)
    creator = User.objects.filter(asn__neighbors__id=id)
    asn = Asn.objects.filter(neighbors__id=id).values('asn')
    asn_num = asn[0]['asn']

    if request.user.is_authenticated and request.user == creator[0]:
        neighbor_object.delete()
        messages.success(request, _("Neighbor deleted successfully"))
        return HttpResponseRedirect("/asn/" + str(asn_num) +"/neighbors/")

    else:
        messages.success(request, _("There is an error"))
        return HttpResponseRedirect("/asn/")


def list_prefixes(request, asn):
    link = "http://stat.ripe.net/data/announced-prefixes/data.json?resource=" + str(asn)
    saved_prefixes = Prefix.objects.filter(origins__origin=asn).values_list('prefix', flat= True)
    prefixes = []
    try:
        with urllib.request.urlopen(link, timeout=10) as url:
            data = json.loads(url.read().decode())

    except urllib.request.HTTPError:
        messages.warning(request, _("This AS has no prefix"))
        return False

    for object in data["data"]["prefixes"]:
        prefixes.append(object['prefix'])

    return render(request, 'asn/list_prefixes.html', {'asn':asn, 'prefixes': prefixes, 'saved_prefixes': saved_prefixes})