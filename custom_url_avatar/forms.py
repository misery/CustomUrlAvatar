from __future__ import unicode_literals

from django.forms import CharField
from djblets.extensions.forms import SettingsForm


class CustomUrlAvatarSettingsForm(SettingsForm):
    custom_url = CharField(
        label='URL of avatar',
        help_text='URL allows you to configure another avatar server application. The following variables of the URL will be replaced accordingly. {scheme} "http" or "https" sent from server, {user} name of user, {size} size of the image that is expected, {host} server host of running server')
