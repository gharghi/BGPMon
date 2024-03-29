import json
import urllib

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from web.apps.main_app.forms import AddAsnForm
from web.apps.main_app.models import Asn, Neighbors
from web.apps.main_app.views.limits import user_limit


def asn(request):
    return render(request, 'asn/asn.html')


class AddAsn(TemplateView):
    def get(self, request, *args, **kwargs):
        asns = Asn.objects.filter(user=request.user)
        return render(request, 'asn/asn.html', {'asns': asns})

    def post(self, request, *args, **kwargs):
        try:
            if not request.POST['asn']:
                messages.warning(request, _('Please enter a valid AS Number'))
                return HttpResponseRedirect("/asn/")

            if Asn.objects.filter(user=request.user).count() >= user_limit(request)['asn']:
                messages.error(request, 'You have reached your ' + str(user_limit(request)[
                                                                           'asn']) + ' AS Number limit.\n Please update your subscription to premium to add more AS Numbers.')
                return HttpResponseRedirect("/asn/")

            form = AddAsnForm(request.POST)
            if form.is_valid():
                form.instance.user = request.user
                form.instance.save()
                messages.success(request, _('AS Number added successfully'))
                return HttpResponseRedirect("/asn/")

            else:
                messages.error(request, form.errors)
                return HttpResponseRedirect("/asn/")

        except Exception as e:
            messages.error(request, e)
            return HttpResponseRedirect("/asn/")


def delete_asn(request, asn):
    asn_object = Asn.objects.filter(asn=asn, user_id=request.user.id)
    asn_object.delete()
    messages.success(request, _("AS Number deleted successfully"))
    return HttpResponseRedirect("/asn/")


def asn_make_policy(request, asn):
    saved_neighbors = {}
    saved_neighbors['left'] = Neighbors.objects.filter(asn__user__id=request.user.id, asn__asn=asn,
                                                       type=1).distinct().values_list('neighbor', flat=True)
    saved_neighbors['right'] = Neighbors.objects.filter(asn__user__id=request.user.id, asn__asn=asn,
                                                        type=2).distinct().values_list('neighbor', flat=True)
    asn_object = Asn.objects.filter(asn=asn, user_id=request.user.id).values('id', 'asn')
    neighbors = find_neighbors(asn, request)
    return render(request, 'asn/neighbors.html',
                  {'neighbors': neighbors, 'saved_neighbors': saved_neighbors, 'asn': asn_object.values()[0]})


# fetch list of right and left neighbors of ASN
def find_neighbors(asn, request):
    link = "http://stat.ripe.net/data/asn-neighbours/data.json?resource=AS" + str(asn)
    neighbors = {'left': [], 'right': []}
    try:
        with urllib.request.urlopen(link, timeout=10) as url:
            data = json.loads(url.read().decode())

    except urllib.request.HTTPError:
        messages.warning(request, _("There is no neighbors"))
        return False

    for object in data["data"]["neighbours"]:
        if object["type"] == 'left':
            neighbors['left'].append(object["asn"])

        elif object["type"] == 'right':
            neighbors['right'].append(object["asn"])

    return neighbors
