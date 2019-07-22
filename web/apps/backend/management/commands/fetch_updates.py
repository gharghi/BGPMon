import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from web.apps.main_app.models import Asn, Prefix


def insert_notifications(notification):
    cs = connection.cursor()
    asn_user = Asn.objects.filter(asn=notification['asn']).values('user_id')
    prefix_user = Prefix.objects.filter(prefix=notification['prefix']).values('user_id')
    if not asn_user:
        users = prefix_user
    elif not prefix_user:
        users = asn_user
    else:
        users = prefix_user

    for user_id in users:
        print("insert into main_app_notifications (user_id, type, path, prefix, asn, time, status) values (" + str(
            user_id['user_id']) + "," + str(notification['type']) + ",'" + str(notification['path']) + "','" + str(
            notification['prefix']) + "'," + str(notification['asn']) + "," + str(
            notification['time']) + ", 0)")
        cs.execute(
            "insert into main_app_notifications (user_id, type, path, prefix, asn, time, status) values (" + str(
                user_id['user_id']) + "," + str(notification['type']) + ",'" + str(notification['path']) + "','" + str(
                notification['prefix']) + "'," + str(notification['asn']) + "," + str(
                notification['time']) + ", 0)")
        if cs.rowcount:
            return True, notification
        else:
            return False, 'An error occurred'


class Command(BaseCommand):
    help = 'fetches updates from RIS servers'

    def handle(self, *args, **kwargs):
        cs = connection.cursor()
        os.system('/bin/bash ' + settings.BASE_DIR + '/apps/backend/management/commands/import_updates.sh')
        # searching announced prefixes in our database
        updates = []
        query = "select prefix.prefix, dump.asn, dump.path, dump.community, dump.time from main_app_prefix as prefix inner join " \
                "main_app_dump as dump on dump.network >= prefix.network and dump.network <= prefix.broadcast group by prefix.prefix, " \
                "dump.asn, dump.path, dump.community, dump.time"
        cs.execute(query)
        rows = cs.fetchall()
        for item in rows:
            updates.append({'prefix': item[0], 'asn': item[1], 'path': item[2], 'community': item[3], 'time': item[4]})
        # print(updates)

        for update in updates:
            # Checking if upstream provider is in left asns in database
            path = update['path'].split(' ')[::-1]
            asn = path[0]
            upstream = path[1]
            query = "select neighbors.left as left_neighbor, neighbors.right as right_neighbor, asn.asn as asn, asn.user_id as user " \
                    "from main_app_neighbors as neighbors inner join main_app_asn as asn on neighbors.asn_id = asn.id where " \
                    "asn.asn = '" + str(asn) + "' and neighbors.left = " + str(upstream)
            cs.execute(query)
            if not cs.rowcount:
                notification = {'path': update['path'], 'time': update['time'], 'asn': asn, 'prefix': update['prefix'],
                                'type': 1}

                print("error, has been transited ", insert_notifications(notification))

            # Checking if prefix is announcing with other ASBs that are not in database
            prefix = update['prefix']
            query = "select origins.origin as origin, prefix.prefix as prefix, prefix.user_id as user from main_app_origins as origins " \
                    "inner join main_app_prefix as prefix on origins.prefix_id = prefix.id where prefix.prefix = '" + prefix + \
                    "' and origins.origin = " + str(asn)
            cs.execute(query)
            if not cs.rowcount:
                notification = {'path': update['path'], 'time': update['time'], 'asn': asn, 'prefix': prefix,
                                'type': 2}
                print("error, has been hijacked ", insert_notifications(notification))

        # Searching announced ASNs in our database
        updates = []
        query = "select distinct main_app_asn.asn as asn, main_app_dump.path as path, INET6_NTOA(main_app_dump.network) as prefix, main_app_dump.time as time from main_app_dump inner join main_app_asn on main_app_asn.asn in (SUBSTRING_INDEX( main_app_dump.path, ' ', 100))"
        cs.execute(query)
        rows = cs.fetchall()
        # print (len(rows))
        for item in rows:
            updates.append({'asn': item[0], 'path': item[1], 'prefix': item[2], 'time': item[3]})

        for update in updates:
            asn = str(update['asn'])
            path = update['path'].split(' ')[::-1]
            prefix = update['prefix']

            if path.index(asn) is 0:
                # Checking if upstream provider is in left asns in database
                upstream = path[1]
                query = "select neighbors.left as left_neighbor, neighbors.right as right_neighbor, asn.asn as asn, asn.id as asn_id, asn.user_id as user from main_app_neighbors as neighbors inner join main_app_asn as asn on neighbors.asn_id = asn.id where asn.asn = " + str(
                    asn) + " and neighbors.left = " + str(upstream)
                # print(query)
                cs.execute(query)
                if not cs.rowcount:
                    notification = {'path': update['path'], 'time': update['time'], 'asn': asn, 'prefix': prefix,
                                    'type': 1}
                    print("error, has been transited ", insert_notifications(notification))

                # Checking if ASN is advertising prefix that is not in database
                query = "select prefix.prefix as prefix, origins.origin as origin, prefix.user_id as user from main_app_prefix as prefix inner join main_app_origins as origins on origins.prefix_id = prefix.id where prefix.prefix = '" + prefix + "' and origins.origin = " + str(
                    asn)
                cs.execute(query)
                if not cs.rowcount:
                    notification = {'path': update['path'], 'time': update['time'], 'asn': asn, 'prefix': prefix,
                                    'type': 4}
                    print("error, is hijacking ", insert_notifications(notification))

            elif path.index(asn) is 1:
                # Checking if right ASNs are in database as right hand
                right = path[0]
                query = "select neighbors.right as right_neighbor, asn.asn as asn, asn.user_id as user from main_app_neighbors as neighbors inner join main_app_asn as asn on neighbors.asn_id = asn.id where asn.asn = " + str(
                    path[1]) + " and neighbors.right = " + str(right)
                cs.execute(query)
                if not cs.rowcount:
                    notification = {'path': update['path'], 'time': update['time'], 'asn': asn, 'prefix': prefix,
                                    'type': 3}
                    print("error, is transiting ", insert_notifications(notification))
            else:
                print("info, upstream path has changed")
        # run the send mail command
        # return render(request, 'notify/send_mail.html')
