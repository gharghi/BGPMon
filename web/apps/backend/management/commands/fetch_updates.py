import os
import sys

import time
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from web.apps.main_app.models import Asn, Prefix, Dump, Stats

# Makes the AS Path unique by duplicate sequence ASNs
def unique_path(path):
    path = path.split(' ')
    unique = []
    for i in range(len(path)):
        if path[i] != path[i-1]:
            unique.append(path[i])
    return ' '.join(unique)

def statistics(data):
    Stats.objects.create(
        update_time=data['update_time'],
        update_count=data['update_count'],
        matched_count=data['matched_count'],
        duration=data['duration']
    )

def insert_notifications(notification):
    cs = connection.cursor()
    asn_user = Asn.objects.filter(asn=notification['asn']).values_list('user_id', flat=True)
    prefix_net = notification['prefix'].split('/')[0]
    query = "select id from main_app_prefix where network <= INET6_ATON(\"" + prefix_net + "\") and broadcast >= INET6_ATON(\"" + prefix_net + "\")"
    cs.execute(query)
    prefix_users = []
    if cs.rowcount:
        rows = cs.fetchall()
        for row in rows:
            user = Prefix.objects.get(id=row[0]).user_id
            prefix_users.append(user)

    users = []
    if asn_user:
        users.append(asn_user)
    if prefix_users:
        for user in prefix_users:
            users.append(user)

    if not asn_user and not prefix_users:
        path = notification['path'].split(' ')
        for asn in path:
            path_users = Asn.objects.filter(asn=asn).values_list('user_id', flat=True)
            if path_users:
                users.append(path_users)

    for user in users:
        query = "insert into main_app_notifications (user_id, type, path, prefix, asn, time, status, emailed) values ( " + str(
            user[0]) + " , " + str(notification['type']) + ",\"" + unique_path(notification['path']) + "\",\"" + notification[
                    'prefix'] + "\"," + str(notification['asn']) + "," + str(notification['time']) + ",0, 0)"
        cs.execute(query)
        if cs.rowcount:
            return True, notification
        else:
            return False, 'An error occurred'

class Command(BaseCommand):
    help = 'fetches updates from RIS servers'

    def handle(self, *args, **kwargs):
        stats = {}
        start_time = time.time
        # Creating list of updates
        cs = connection.cursor()
        os.system('/bin/bash ' + settings.BASE_DIR + '/apps/backend/management/commands/import_updates.sh')
        stats['update_time'] = os.path.getmtime(settings.BASE_DIR + '/apps/backend/tmp/latest-update.gz')
        stats['update_count'] = Dump.objects.all().count()
        # searching announced prefixes in our database
        updates = []
        query = "select prefix.prefix, dump.asn, dump.path, dump.time, dump.prefix from main_app_prefix as prefix inner join " \
                "main_app_dump as dump on dump.network >= prefix.network and dump.network <= prefix.broadcast group by prefix.prefix, " \
                "dump.asn, dump.path"
        cs.execute(query)
        rows = cs.fetchall()
        stats['matched_count'] = len(rows)
        for item in rows:
            updates.append({'prefix': item[4], 'asn': item[1], 'path': item[2], 'time': item[3]})

        for update in updates:
            # Checking if upstream provider is in left asns in database
            path = update['path'].split(' ')[::-1]
            asn = path[0]

            try:
                prefix_net = update['prefix'].split('/')[0]
                query = "select id,prefix from main_app_prefix where network <= INET6_ATON(\"" + prefix_net + "\") and broadcast >= INET6_ATON(\"" + prefix_net + "\")"
                cs.execute(query)
                if cs.rowcount:
                    rows = cs.fetchall()
                    for row in rows:
                        prefix_id = row[0]
                        query = "select id from main_app_origins where prefix_id = " + str(prefix_id) + " and origin = " + str(asn)
                        cs.execute(query)
                        if cs.rowcount:
                            flag = 0
                            break
                        else:
                            flag = 1

                    if flag:
                        notification = {'path': update['path'], 'time': update['time'], 'asn': asn,
                                        'prefix': update['prefix'],
                                        'type': 2}
                        print("error, has been hijacked ", insert_notifications(notification))
            except Exception as e:
                print(e, 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno))

        # Searching announced ASNs in our database
        # making a list from updates based on ASN
        updates = []
        try:
            query = "select distinct asns.asn as asn, dump.path as path, dump.prefix as prefix, dump.time as time from main_app_dump as dump inner join main_app_asn as asns on INSTR(Concat(\" \", dump.path, \" \"),Concat(\" \", asns.asn, \" \"))"
            cs.execute(query)
            rows = cs.fetchall()
        except Exception as e:
            print(e)
        # print (len(rows))
        for item in rows:
            updates.append({'asn': item[0], 'path': item[1], 'prefix': item[2], 'time': item[3]})

        for update in updates:
            asn = str(update['asn'])
            path = update['path'].split(' ')[::-1]
            ###########unique path##################
            prefix = update['prefix']
            try:
                if path.index(asn) is 0:
                    # Checking if upstream provider is in left asns in database
                    upstream = path[1]
                    query = "select neighbors.neighbor, asn.asn as asn, asn.id as asn_id, asn.user_id as user from main_app_neighbors as neighbors inner join main_app_asn as asn on neighbors.asn_id = asn.id where asn.asn = " + asn + " and neighbors.type = 1 and neighbors.neighbor = " + upstream
                    cs.execute(query)
                    if not cs.rowcount:
                        notification = {'path': update['path'], 'time': update['time'], 'asn': asn, 'prefix': prefix,
                                        'type': 1}
                        print("error, has been transited ", insert_notifications(notification))

                    # Checking if ASN is advertising prefix that is not in database
                    prefix_net = update['prefix'].split('/')[0]
                    query = "select prefix.prefix as prefix, origins.origin as origin, prefix.user_id as user from main_app_prefix as prefix inner join main_app_origins as origins on origins.prefix_id = prefix.id where prefix.network <= INET6_ATON(\"" + prefix_net + "\") and prefix.broadcast >= INET6_ATON(\"" + prefix_net + "\") and origins.origin = " + str(asn)
                    cs.execute(query)
                    if not cs.rowcount:
                        notification = {'path': update['path'], 'time': update['time'], 'asn': asn, 'prefix': prefix,
                                        'type': 4}
                        print("error, is hijacking ", insert_notifications(notification))

                elif path.index(asn) is 1:
                    # Checking if right ASNs are in database as right hand
                    right = path[0]
                    query = "select neighbors.neighbor as right_neighbor, asn.asn as asn, asn.user_id as user from main_app_neighbors as neighbors inner join main_app_asn as asn on neighbors.asn_id = asn.id where asn.asn = " + \
                            path[1] + " and neighbors.type = 2 and neighbors.neighbor = " + right
                    cs.execute(query)
                    if not cs.rowcount:
                        notification = {'path': update['path'], 'time': update['time'], 'asn': path[0], 'prefix': prefix,
                                        'type': 3}
                        print("error, is transiting ", insert_notifications(notification))
                # else:
                #     print("info, upstream path has changed")
            except Exception as e:
                print(e)
        end_time = time.time
        stats['duration'] = str(round((end_time - start_time) * 1000000, 1))
        statistics(stats)
        # run the send mail command

