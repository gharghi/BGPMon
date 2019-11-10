import urllib.request
import json
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from netaddr import IPNetwork
from web.apps.main_app.forms import AddPrefixForm, AddOriginsForm
from web.apps.main_app.forms.make_policy_form import MakePolicyForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from web.apps.main_app.models import Prefix, Origins
from django.utils.translation import gettext as _
import socket
from web.apps.main_app.views.limits import user_limit


# @is_user_in_group('Customers')  # for authorization with group name


def add_prefix(request):
    # prefixes = prefix.Prefix.objects.all()
    return render(request, 'add_prefix/add_prefix.html')


class MakePolicy(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'add_prefix/make_policy.html')

    def post(self, request, *args, **kwargs):
        try:
            form = MakePolicyForm(request.POST)
            if form.is_valid():
                #
                username = request.user
                prefix = request.POST.getlist('prefix')
                for item in prefix:
                    form = MakePolicyForm(request.POST)
                    if form.is_valid():
                        form.instance.user = username
                        if IPNetwork(item).version is 6:
                            af = socket.AF_INET6
                        else:
                            af = socket.AF_INET
                        form.instance.network = socket.inet_pton(af,str(IPNetwork(item).network))
                        form.instance.broadcast = socket.inet_pton(af, str(IPNetwork(item).broadcast))
                        form.instance.prefix = item
                        form.instance.save()



                messages.success(request, _('Prefix(s) added successfully'))
                return HttpResponseRedirect("/prefix/")

            else:
                messages.error(request, form.errors)
                return render(request, 'add_prefix/add_prefix.html', {'add_prefix_form': add_prefix})

        except Exception as e:
            messages.error(request, e)
            return render(request, 'add_prefix/add_prefix.html', {'add_prefix_form': add_prefix})


class CreatePrefix(TemplateView):
    def get(self, request, *args, **kwargs):
        objects = Prefix.objects.filter(user=request.user).values('prefix','id')
        prefixes = []
        for object in objects:
            prefix = {'prefix': object['prefix'], 'id':object['id']}
            origins = Origins.objects.filter(prefix=object['id']).values('origin', 'id')
            asns = []
            if origins:
                for origin in origins:
                    asns.append({'id': origin['id'], 'origin': origin['origin']})
            prefixes.append({'prefix':prefix, 'origins': asns})

        return render(request, 'add_prefix/add_prefix.html', {'prefixes': prefixes})


    def post(self, request, *args, **kwargs):
        try:
            if not request.POST['prefix']:
                messages.error(request, _('Please enter a valid prefix'))
                return HttpResponseRedirect("/prefix/")

            if Prefix.objects.filter(user=request.user).count() >= user_limit(request)['prefix']:
                messages.error(request, 'You have reached your '+ str(user_limit(request)['prefix']) +' prefix limit.\n Please update your subscription to premium to add more prefixes.')
                return HttpResponseRedirect("/prefix/")

            form = AddPrefixForm(request.POST)
            if form.is_valid():
                user_prefix = form.cleaned_data["prefix"]
                route_objects = find_route_objects(user_prefix, request)
                # asns = find_advertised_asn(user_prefix)
                saved_prefixes = Prefix.objects.filter(user=request.user).values_list('prefix', flat=True)
                return render(request, 'add_prefix/make_policy.html', {'route_objects': route_objects, 'saved_prefixes':saved_prefixes})

        except Exception as e:
            messages.error(request, 'There is an unusual error!')
            return render(request, 'add_prefix/add_prefix.html', {'add_prefix_form': add_prefix})


def find_route_objects(prefix, request):
    link = "http://rest.db.ripe.net/search.json?query-string=" + prefix + "&type-filter=route&flags=no-filtering&flags=all-more&source=RIPE"
    objects = {prefix: prefix}
    try:
        with urllib.request.urlopen(link, timeout=10) as url:
            data = json.loads(url.read().decode())

    except urllib.request.HTTPError:
        messages.warning(request, _("There is no route object"))
        return objects

    for object in data["objects"]["object"]:
        if object['type'] == "route":
            objects.update(
                {object["primary-key"]["attribute"][0]["value"]: object["primary-key"]["attribute"][1]["value"]})

    return objects


# def find_advertised_asn(asn):
#     asns = {'AS43754': 43754}
#     return asns


def delete_prefix(request, id):
    prefix_object = get_object_or_404(Prefix, id=id)
    creator = prefix_object.user.username

    if request.user.is_authenticated and request.user.username == creator:
        prefix_object.delete()
        messages.success(request, _("Prefix deleted successfully"))
        return HttpResponseRedirect("/prefix/")


def prefix_make_policy(request, id):
    try:
        prefix = Prefix.objects.get(id=id)
        if prefix:
            saved_origins = Origins.objects.filter(prefix=prefix).values_list('origin', flat=True)
            if request.user == prefix.user:
                origins = find_origins(prefix.prefix, request)
                return render(request, 'add_prefix/prefix_policy.html', {'origins': origins, 'prefix': prefix, 'saved_origins': saved_origins})
        else:
            messages.error(request, _('No such prefix'))
            return render(request, 'add_prefix/add_prefix.html')
    except Exception as e:
        # messages.error(request, e)
        messages.error(request, _('An error has occured'))
        return render(request, 'add_prefix/add_prefix.html')

def find_database_origins(prefix, request):
    link = "http://rest.db.ripe.net/search.json?query-string=" + prefix + "&type-filter=route&type-filter=route6&flags=all-more&flags=no-referenced&flags=no-irt&source=RIPE"
    objects = {}
    try:
        with urllib.request.urlopen(link, timeout=10) as url:
            data = json.loads(url.read().decode())

    except urllib.request.HTTPError:
        messages.warning(request, _("There is no route object"))
        return objects

    for object in data["objects"]["object"]:
        if object['type'] == "route":
            objects.update(
                object["primary-key"]["attribute"][1]["value"])
    return objects


def find_origins(prefix, request):
    splitted = prefix.split('/')
    link = "http://stat.ripe.net/data/prefix-routing-consistency/data.json?resource=" + splitted[0] + '%2F' + splitted[1]
    objects = {'prefix': prefix, 'in_bgp': [], 'in_db': []}
    try:
        with urllib.request.urlopen(link, timeout=10) as url:
            data = json.loads(url.read().decode())

    except urllib.request.HTTPError:
        messages.warning(request, _("There is no originator"))
        return objects

    for object in data["data"]["routes"]:
        if object['in_whois']:
            if object['origin'] not in objects['in_db']:
                objects['in_db'].append(object['origin'])

        if object['in_bgp']:
            if object['origin'] not in objects['in_bgp']:
                objects['in_bgp'].append(object['origin'])

    return objects



class AddPrefixPolicy(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'add_prefix/make_policy.html')

    def post(self, request, *args, **kwargs):
        try:
            form = MakePolicyForm(request.POST)
            if form.is_valid():
                username = request.user
                prefix = request.POST.getlist('prefix')
                for item in prefix:
                    form = MakePolicyForm(request.POST)
                    if form.is_valid():
                        form.instance.user = username
                        if IPNetwork(item).version is 6:
                            af = socket.AF_INET6
                        else:
                            af = socket.AF_INET
                        form.instance.network = socket.inet_pton(af,str(IPNetwork(item).network))
                        form.instance.broadcast = socket.inet_pton(af, str(IPNetwork(item).broadcast))
                        form.instance.prefix = item
                        form.instance.save()

                        orgs = Origins()
                        orgs.origin = int(request.POST.get('origin'))
                        orgs.prefix = Prefix.objects.filter(prefix=item).first()
                        orgs.save()


                messages.success(request, _('Prefix(s) added successfully'))
                return HttpResponseRedirect("/prefix/")

            else:
                messages.error(request, form.errors)
                return render(request, 'add_prefix/add_prefix.html', {'add_prefix_form': add_prefix})

        except Exception as e:
            messages.error(request, e)
            return render(request, 'add_prefix/add_prefix.html', {'add_prefix_form': add_prefix})

