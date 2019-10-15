from django.forms import ModelForm
from web.apps.main_app.models import Origins


class AddOriginsForm(ModelForm):

    class Meta:
        model = Origins
        fields = ['prefix']

    def __init__(self, *args, **kwargs):
        super(AddOriginsForm, self).__init__(*args, **kwargs)
