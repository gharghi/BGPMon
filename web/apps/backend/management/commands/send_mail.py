import requests
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from web.apps.jwt_store.models import User
from web.apps.main_app.models import Notifications, NotificationRule


def send_telegram(content):
    url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s' % (
    settings.TELEGRAM_BOT_KEY, '-1001425080891', content)
    requests.get(url, timeout=10)


def status(text):
    code = {
        1: "Has been transited",
        2: "Has been hijacked",
        3: "Is Transiting",
        4: "Is Hijacking",
        0: "Path has been changed",
    }
    return code[text]


def get_notifications(user):
    if NotificationRule.objects.filter(user=user).exists():
        rule = NotificationRule.objects.get(user=user)
        notifications = Notifications.objects.filter(emailed=0, user__id=user.id).order_by('-time')
        if notifications.exists():  ##prevent sending empty notification
            mail = "BGPMon Alerts\n"
            for notification in notifications:
                if notification.type == 1 and not rule.transited:
                    continue
                if notification.type == 2 and not rule.hijacked:
                    continue
                if notification.type == 3 and not rule.transiting:
                    continue
                if notification.type == 4 and not rule.hijacking:
                    continue
                mail = mail + notification.prefix + '\t\t' + status(
                    notification.type) + '\t\t\t ' + notification.path + '\n'

            if rule.email:
                email = EmailMessage('BGPMon Alert', mail, to=[rule.email])
                if email.send():
                    notifications.update(emailed=True)

            send_telegram(mail)


class Command(BaseCommand):
    help = 'Sending notifications to users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            get_notifications(user)
