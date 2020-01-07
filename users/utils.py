from calendar import timegm
from datetime import datetime

from rest_framework_jwt.settings import api_settings


def jwt_payload_handler(user):
    payload = {
        # TODO: delete user name and is's
        'user_id': user.pk,
        'username': user.username,
        'phone_number': user.phone_number,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload
