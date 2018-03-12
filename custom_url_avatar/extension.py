# CustomUrlAvatar Extension for Review Board.

from __future__ import unicode_literals

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
        return self.get_avatar_urls_uncached(user, size)

    def get_avatar_urls_uncached(self, user, size=None):
        url = self._extension.settings[CONFIG_CUSTOM_URL]
        return {
            '%dx' % res: mark_safe(
                url.format(user=user,
                           size='' if size is None else int(size) * res))
            for res in (1, 2, 3)
        }

    def get_etag_data(self, user):
        return [self.avatar_service_id, user.username]


class CustomUrlAvatar(Extension):
    metadata = {
        'Name': 'CustomUrlAvatar',
        'Summary': 'Support easy custom URL for avatars.',
    }

    is_configurable = True
    default_settings = {
        CONFIG_CUSTOM_URL: 'https://img.local/?user={user}&s={size}',
    }

    def initialize(self):
        AvatarServiceHook(self, CustomAvatarService)
