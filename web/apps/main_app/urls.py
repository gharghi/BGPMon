from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path

from web.apps.main_app.views.profile.change_password import change_password
from web.apps.main_app.views.profile.edit import EditProfile
from .views.add_prefix import CreatePrefix, MakePolicy, delete_prefix, prefix_make_policy, AddPrefixPolicy
from .views.asn import AddAsn, delete_asn, asn_make_policy
from .views.asn_policy import MakeAsnPolicy, list_neighbors, delete_neighbors, list_prefixes
from .views.fix_notification import fix_notification
from .views.home import home
from .views.notification_rules import AddNotificationRule
from .views.notifications import view_notifications
from .views.prefix_policy import MakePrefixPolicy, list_origins, delete_origin
from .views.signup import signup, activate

urlpatterns = [
    path('', login_required(home), name='home'),
    path('prefix/', login_required(CreatePrefix.as_view()), name='add_prefix'),
    path('prefix/policy/', login_required(MakePolicy.as_view()), name='make_policy'),
    path('prefix/<int:id>/delete/', login_required(delete_prefix)),
    path('prefix/<int:id>/policy/', login_required(prefix_make_policy)),
    path('prefix/<int:id>/origins/', login_required(list_origins)),
    path('prefix/<int:id>/origin/delete/', login_required(delete_origin)),
    path('prefix/add/policy/', login_required(MakePrefixPolicy.as_view()), name='prefix_policy'),

    path('asn/', login_required(AddAsn.as_view()), name='asn'),
    path('asn/<int:asn>/delete/', login_required(delete_asn)),
    path('asn/<int:asn>/policy/', login_required(asn_make_policy)),
    path('asn/<int:asn>/policy/add/', login_required(MakeAsnPolicy.as_view())),
    path('asn/<int:asn>/prefix/add/', login_required(AddPrefixPolicy.as_view())),
    path('asn/<int:asn>/neighbors/', login_required(list_neighbors)),
    path('neighbor/<int:id>/delete/', login_required(delete_neighbors)),
    path('asn/<int:asn>/prefixes/', login_required(list_prefixes)),

    path('notifications/', login_required(view_notifications), name='notifications'),
    path('notifications/rules/', login_required(AddNotificationRule.as_view())),
    path('notifications/<int:id>/fix/', login_required(fix_notification)),

    path('profile/', login_required(EditProfile.as_view()), name='edit_profile'),
    path('changePassword/', login_required(change_password), name='change_password'),

    url(r'^accounts/signup/$', signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),

]
