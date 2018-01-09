# CustomUrlAvatar Extension for Review Board.

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include
from django.utils.html import mark_safe

from reviewboard.extensions.base import Extension

from djblets.avatars.services import AvatarService

from reviewboard.extensions.base import get_extension_manager
from reviewboard.extensions.hooks import AvatarServiceHook

CONFIG_CUSTOM_URL = 'custom_url'

class CustomAvatarService(AvatarService):
    def __init__(self, settings_manager):
        super(CustomAvatarService, self).__init__(settings_manager)
        self._extension = get_extension_manager().get_enabled_extension(
            'custom_url_avatar.extension.CustomUrlAvatar'
        )

    avatar_service_id = 'CustomAvatar'
    name = 'Custom Avatar Service'

    def get_avatar_urls(self, request, user, size=None):
        """Return the avatar urls.

        Args:
            request (django.http.HttpRequest):
                The HTTP request.

            user (django.contrib.auth.models.User):
                The user.

            size (int, optional):
                The requested avatar size.

        Returns:
            dict:
            A dictionary of avatars.
        """
        return {
            '1x': mark_safe(
                self._extension.settings[CONFIG_CUSTOM_URL].format(
               scheme='https' if request.is_secure() else 'http',
               host=request.get_host(),
               user=user,
               size=size,
            ))
        }

    def get_etag_data(self, user):
        return [self.avatar_service_id, user.email]


class CustomUrlAvatar(Extension):
    metadata = {
        'Name': 'CustomUrlAvatar',
        'Summary': 'Support easy custom URL for avatars.',
    }

    is_configurable = True
    default_settings = {
        CONFIG_CUSTOM_URL: '{scheme}://{host}/img/?user={user}&s={size}',
    }


    def initialize(self):
        AvatarServiceHook(self, CustomAvatarService)

