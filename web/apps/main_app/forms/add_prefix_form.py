from django.forms import ModelForm
from web.apps.main_app.models import Prefix


class AddPrefixForm(ModelForm):

    class Meta:
        model = Prefix
        fields = ['user', 'prefix']

    def __init__(self, *args, **kwargs):
        super(AddPrefixForm, self).__init__(*args, **kwargs)
