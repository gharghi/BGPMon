from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
from web.apps.main_app.forms.profile_form import ProfileForm
from web.apps.jwt_store.models import User

class EditProfile(TemplateView):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        return render(request, 'profile/edit.html', {'user': user})

    def post(self, request, *args, **kwargs):
        try:
            form = ProfileForm(request.POST, instance=request.user)

            if form.is_valid():
                form.save()
            else:
                messages.error(request,form)


            return HttpResponseRedirect("/profile/")

        except Exception as e:
            messages.error(request, 'There is an error')
            # messages.error(request, e)
            return HttpResponseRedirect("/profile/")