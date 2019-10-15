from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.contrib.sessions.backends.signed_cookies import SessionStore


JWT_USER_FIELDS = ['email', 'slug']  # OR: load these from settings


class JwtSessionStore(SessionStore):

    def load(self):
        """
        We load the data from the key itself instead of fetching from
        some external data store. Opposite of _get_session_key(),
        raises BadSignature if signature fails.
        """
        try:
            data = jwt.decode(self.session_key, settings.JWT_SECRET, algorithms='HS256')
            if '_auth_user_id' in data:
                data['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
                data['_auth_user_hash'] = 'oidc'
            return data
        except Exception:
            # BadSignature, ValueError, or unpickling exceptions. If any of
            # these happen, reset the session.
            self.create()
        return {}

    def save(self, must_create=False):
        """
        To save, get the session key as a securely signed string and then set
        the modified flag so that the cookie is set on the client for the
        current request.
        """
        self._session_key = self._get_session_key()
        self.modified = True

    def _get_session_key(self):
        """
        Most session backends don't need to override this method, but we do,
        because instead of generating a random string, we want to actually
        generate a JWT Token with DRF-JWT.
        """
        session_cache = getattr(self, '_session_cache', {})
        if '_auth_user_backend' in session_cache:
            del session_cache['_auth_user_backend']
        if '_auth_user_hash' in session_cache:
            del session_cache['_auth_user_hash']
        return jwt.encode(session_cache, settings.JWT_SECRET, 'HS256').decode("utf-8")
