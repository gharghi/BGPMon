from django.forms import ModelForm
from web.apps.main_app.models import Prefix


class MakePolicyForm(ModelForm):
    class Meta:
        model = Prefix
        fields = ['user', 'prefix']

    def __init__(self, *args, **kwargs):
        super(MakePolicyForm, self).__init__(*args, **kwargs)
