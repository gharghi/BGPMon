from django.contrib import admin
from web.apps.jwt_store.models import User, Group
from django.contrib.auth.models import Group as grp

admin.site.unregister(grp)
admin.site.register(User)
admin.site.register(Group)