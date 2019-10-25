from django import forms
from web.apps.jwt_store.models import User

class ProfileForm(forms.ModelForm):


    class Meta:
        model = User
        fields = ('first_name', 'last_name')


    def save(self, commit=True):
        user = super(ProfileForm, self).save(commit=False)

        if commit:
            user.save()
        return user