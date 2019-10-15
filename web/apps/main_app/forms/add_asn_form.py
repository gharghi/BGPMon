from django.forms import ModelForm
from web.apps.main_app.models import Asn


class AddAsnForm(ModelForm):

    class Meta:
        model = Asn
        fields = ['user', 'asn']

    def __init__(self, *args, **kwargs):
        super(AddAsnForm, self).__init__(*args, **kwargs)
