from django.contrib import admin
from django.contrib.auth.models import Group as grp
from django.db.models import Count

from web.apps.jwt_store.models import User, Group
from web.apps.main_app.models import Asn, Prefix, Neighbors, Origins

admin.site.unregister(grp)
admin.site.register(Group)


# Define the admin class
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email_confirmed', 'groups', 'email', 'asn_count', 'prefix_count', 'notifications_count')

    # Count number of registered ASNs
    def asn_count(self, obj):
        return obj._asn_count

    # Count number of Prefixes
    def prefix_count(self, obj):
        return obj._prefix_count

    # Count number of Notifications
    def notifications_count(self, obj):
        return obj._notifications_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _asn_count=Count("asn", distinct=True),
        )
        queryset = queryset.annotate(
            _prefix_count=Count("prefix", distinct=True),
        )
        queryset = queryset.annotate(
            _notifications_count=Count("notifications", distinct=True),
        )
        return queryset


class AsnAdmin(admin.ModelAdmin):
    list_display = ('asn', 'owner', 'left_neighbors_count', 'right_neighbors_count', 'prefix_count')

    def owner(self, obj):
        return obj.user.username

    def left_neighbors_count(self, obj):
        return Neighbors.objects.filter(type=1, asn=obj).count()

    def right_neighbors_count(self, obj):
        return Neighbors.objects.filter(type=2, asn=obj).count()

    def prefix_count(self, obj):
        return Origins.objects.filter(origin=obj.asn).count()


admin.site.register(User, UserAdmin)
admin.site.register(Prefix)
admin.site.register(Asn, AsnAdmin)
