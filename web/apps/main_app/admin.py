from django.contrib import admin
from web.apps.jwt_store.models import User

admin.site.register(User)