import socket

from django.http import JsonResponse
from netaddr import IPNetwork

from web.apps.main_app.models import Prefix, Notifications, Asn, Origins, Neighbors


def fix_notification(request, id):
    try:
        notification = Notifications.objects.get(id=id)

        if notification.type is 1:  # Transited
            # Creating a left neighbor
            path = notification.path.split(' ')[::-1]
            for i in range(len(path)):
                if Asn.objects.filter(asn=path[i]):
                    Neighbors.objects.update_or_create(
                        asn=Asn.objects.get(asn=path[i], user=request.user),
                        neighbor=int(path[i + 1]),
                        type=1,
                    )
            notification.status = 1
            notification.save()

            response = {'status': True}
            return JsonResponse(response)

        if notification.type is 2:  # Hijacked
            prefix = Prefix.objects.filter(user=request.user, prefix=notification.prefix)
            if not prefix:
                prefix = notification.prefix
                if IPNetwork(prefix).version is 6:
                    af = socket.AF_INET6
                else:
                    af = socket.AF_INET
                # Adding Prefix
                prefix = Prefix.objects.create(
                    user_id=request.user.id,
                    network=socket.inet_pton(af, str(IPNetwork(prefix).network)),
                    broadcast=socket.inet_pton(af, str(IPNetwork(prefix).broadcast)),
                    prefix=prefix
                )
                # Creting Policy
                Origins.objects.create(
                    prefix=prefix,
                    origin=notification.asn
                )
                # Setting Notification Saved
                notification.status = 1
                notification.save()

                response = {'status': True}
                return JsonResponse(response)

            else:
                prefix = Prefix.objects.get(user=request.user, prefix=notification.prefix)
                # Creting Policy
                Origins.objects.create(
                    prefix=prefix,
                    origin=notification.asn
                )
                # Setting Notification Saved
                notification.status = 1
                notification.save()

                response = {'status': True}
                return JsonResponse(response)

        if notification.type is 3:  # Transiting
            # Creating a right neighbor
            path = notification.path.split(' ')[::-1]
            for i in range(len(path)):
                if Asn.objects.filter(asn=path[i]):
                    Neighbors.objects.update_or_create(
                        asn=Asn.objects.get(asn=path[i], user=request.user),
                        neighbor=int(path[i - 1]),
                        type=2,
                    )
            # Setting Notification Saved
            notification.status = 1
            notification.save()

            response = {'status': True}
            return JsonResponse(response)

        if notification.type is 4:  # Hijacking
            prefix = Prefix.objects.filter(user=request.user, prefix=notification.prefix)
            if not prefix:
                prefix = notification.prefix
                if IPNetwork(prefix).version is 6:
                    af = socket.AF_INET6
                else:
                    af = socket.AF_INET
                # Adding Prefix
                prefix = Prefix.objects.create(
                    user_id=request.user.id,
                    network=socket.inet_pton(af, str(IPNetwork(prefix).network)),
                    broadcast=socket.inet_pton(af, str(IPNetwork(prefix).broadcast)),
                    prefix=prefix
                )
                # Creting Policy
                Origins.objects.create(
                    prefix=prefix,
                    origin=notification.asn
                )
                # Setting Notification Saved
                notification.status = 1
                notification.save()

                response = {'status': True}
                return JsonResponse(response)

            response = {'status': False, 'message': 'Notification already fixed'}
            return JsonResponse(response)

    except Exception as e:

        response = {'status': False, 'message': 'Unknown Error'}
        return JsonResponse(response)
