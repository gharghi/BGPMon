from django.forms import ModelForm
from web.apps.main_app.models import NotificationRule


class NotificationRuleForm(ModelForm):

    class Meta:
        model = NotificationRule
        fields = ['user', 'phone', 'email', 'telegram', 'hijacked', 'hijacking', 'transited', 'transiting']

    def __init__(self, *args, **kwargs):
        super(NotificationRuleForm, self).__init__(*args, **kwargs)