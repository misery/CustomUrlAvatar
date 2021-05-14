"""Admin URLs for the extension."""

from django.conf.urls import url
from reviewboard.extensions.views import configure_extension

from custom_url_avatar.extension import CustomUrlAvatar
from custom_url_avatar.forms import CustomUrlAvatarSettingsForm


urlpatterns = [
    url(r'^$', configure_extension, {
        'ext_class': CustomUrlAvatar,
        'form_class': CustomUrlAvatarSettingsForm,
    }, name='custom_url_avatar-configure'),
]
