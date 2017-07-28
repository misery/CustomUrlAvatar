from __future__ import unicode_literals

from django.conf.urls import patterns, url

from custom_url_avatar.extension import CustomUrlAvatar
from custom_url_avatar.forms import CustomUrlAvatarSettingsForm


urlpatterns = patterns(
    '',

    url(r'^$',
        'reviewboard.extensions.views.configure_extension',
        {
            'ext_class': CustomUrlAvatar,
            'form_class': CustomUrlAvatarSettingsForm,
        },
        name='custom_url_avatar-configure'),
)
