from django.forms import ModelForm
from web.apps.main_app.models import Neighbors


class AddNeighborsForm(ModelForm):

    class Meta:
        model = Neighbors
        fields = ['asn']

    def __init__(self, *args, **kwargs):
        super(AddNeighborsForm, self).__init__(*args, **kwargs)
