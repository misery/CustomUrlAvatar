"""Admin URLs for the extension."""

from django.urls import path
from reviewboard.extensions.views import configure_extension

from custom_url_avatar.extension import CustomUrlAvatar
from custom_url_avatar.forms import CustomUrlAvatarSettingsForm


urlpatterns = [
    path(r'',
         configure_extension,
         {
            'ext_class': CustomUrlAvatar,
            'form_class': CustomUrlAvatarSettingsForm,
         }, name='custom_url_avatar-configure'),
]
