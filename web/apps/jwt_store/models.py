from django.contrib.auth.models import User, AbstractUser, Group
from django.db import models


class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    groups = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    """
    Users within the Django authentication system are represented by this
    model.

    Username, password and email are required. Other fields are optional.
    """

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        db_table = 'users'

    def get_session_auth_hash(self):
        return 'oidc'
