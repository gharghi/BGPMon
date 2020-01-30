from web.apps.jwt_store.models import Group


def user_limit(request):
    return Group.objects.filter(user=request.user).values('asn', 'prefix')[0]
