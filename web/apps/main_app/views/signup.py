from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from web.apps.jwt_store.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils.translation import gettext as _

from web.apps.main_app.forms.sign_up_form import SignUpForm
from web.apps.main_app.tokens.tokens import account_activation_token


@login_required
def home(request):
    return render(request, 'registration/login.html')


def signup(request):
    if request.method == "GET":
        return render(request, 'registration/login.html')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        try:
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                subject = 'Activate Your BGPMon Account'
                message = render_to_string('registration/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)
                messages.success(request,_('Account activation sent. Please check your email for confirmation link.'))
                return redirect('login')
            else:
                messages.error(request, form.errors)
                return redirect('login')
        except Exception as e:
            messages.error(request,e)
            return redirect('login')

    else:
        # return redirect('login/')
        form = SignUpForm()
        return render(request, 'registration/login.html', {'form': form})



def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        # login(request, user)
        messages.success(request, _('Your Account has been activated. Please login to continue.'))
        return redirect('login')
    else:
        messages.error(request, _('There was a problem in activation, please try again'))
        return redirect('login')
