import urllib, json
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from web.apps.main_app.forms import NotificationRuleForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from web.apps.main_app.models import NotificationRule
from django.utils.translation import gettext as _

@login_required
# @is_user_in_group('Customers')  # for authorization with group name
def notification_rules(request):
    return render(request, 'notifications/view_rules.html')


class AddNotificationRule(TemplateView):
    def get(self, request, *args, **kwargs):
        rules = NotificationRule.objects.filter(user=request.user)
        return render(request, 'notifications/view_rules.html', {'rules': rules})

    def post(self, request, *args, **kwargs):
        try:
            form = NotificationRuleForm(request.POST)
            if form.is_valid():
                id = request.POST.get("id", "")
                if id:
                    rule_object = get_object_or_404(NotificationRule, id=id)
                    creator = rule_object.user
                    if request.user.is_authenticated and request.user == creator:
                        instance = NotificationRule.objects.get(id=id)
                        form = NotificationRuleForm(request.POST, instance=instance)
                        form = form.save(commit=False)
                        form.user = request.user
                        form.save()
                        messages.success(request, _("Notification Rule Edited successfully"))
                        return HttpResponseRedirect("/notifications/rules/")
                else:
                    form = NotificationRuleForm(request.POST)
                    form = form.save(commit=False)
                    form.user = request.user
                    form.save()
                    messages.success(request, _("Notification Rule Edited successfully"))
                    return HttpResponseRedirect("/notifications/rules/")

            else:
                messages.error(request, _("something is wrong"))
                return HttpResponseRedirect("/notifications/rules/")

        except Exception as e:
            messages.error(request, e)
            return HttpResponseRedirect("/notifications/rules/")
