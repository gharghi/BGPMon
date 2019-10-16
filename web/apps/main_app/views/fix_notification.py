import socket

from django.contrib import messages
from django.shortcuts import render
from netaddr import IPNetwork

from web.apps.main_app.forms import AddNeighborsForm
from web.apps.main_app.models import Prefix, Notifications, Asn, Origins, Neighbors

def fix_notification(request, id):
    try:
        notification = Notifications.objects.get(id=id)

        if notification.type is 1:  # Transited
            #Creating a left neighbor
            path = notification.path.split(' ')[::-1]
            asn_index = path.index(str(notification.asn))
            Neighbors.objects.create(
                asn=Asn.objects.get(asn=notification.asn),
                neighbor=int(path[asn_index + 1]),
                type=1,
            )
            # Setting Notification Saved
            notification.status = 1
            notification.save()
            messages.success(request, 'Notification fixed successfully')
            return render(request, 'notifications/list_notifications.html')

        if notification.type is 2:  # Hijacked
            prefix = Prefix.objects.filter(user=request.user, prefix=notification.prefix)
            if not prefix:
                prefix = notification.prefix
                if IPNetwork(prefix).version is 6:
                    af = socket.AF_INET6
                else:
                    af = socket.AF_INET
                #Adding Prefix
                prefix = Prefix.objects.create(
                    user_id=request.user.id,
                    network=socket.inet_pton(af, str(IPNetwork(prefix).network)),
                    broadcast=socket.inet_pton(af, str(IPNetwork(prefix).broadcast)),
                    prefix=prefix
                )
                #Creting Policy
                Origins.objects.create(
                    prefix = prefix,
                    origin=notification.asn
                )
                #Setting Notification Saved
                notification.status = 1
                notification.save()

                messages.success(request, 'Notification fixed successfully')
                return render(request, 'notifications/list_notifications.html')
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
                messages.success(request, 'Notification fixed successfully')
                return render(request, 'notifications/list_notifications.html')

        if notification.type is 3:  # Transiting
            # Creating a right neighbor
            path = notification.path.split(' ')[::-1]
            asn_index = path.index(str(notification.asn))
            Neighbors.objects.create(
                asn=Asn.objects.get(asn=notification.asn),
                neighbor=int(path[asn_index - 1]),
                type=2,
            )
            # Setting Notification Saved
            notification.status = 1
            notification.save()
            messages.success(request, 'Notification fixed successfully')
            return render(request, 'notifications/list_notifications.html')

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

                messages.success(request, 'Notification fixed successfully')
                return render(request, 'notifications/list_notifications.html')


            messages.error(request, 'Notification already fixed')
            return render(request, 'notifications/list_notifications.html')

    except Exception as e:
        messages.error(request, e)
        return render(request, 'notifications/list_notifications.html')

        # asn_id = Asn.objects.filter(user=request.user).filter(asn = notification.asn)
        # if not asn_id:
        #     form = AddAsnForm()
        #     form.asn = notification[0].asn
        #     form.user = request.user
        #     if form.is_valid():
        #         form.save()
        #         asn_id = form.auto_id

        # try:
        #     Origins(origin=notification.asn, prefix= prefix).save()
        #
        #
        #
        # except Exception as e:
        #     messages.warning(request,e)
        # return render(request, 'add_prefix/add_prefix.html')
