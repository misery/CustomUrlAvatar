from __future__ import unicode_literals

from reviewboard.extensions.packaging import setup


PACKAGE = "rbCustomUrlAvatar"
VERSION = "0.3"

setup(
    name=PACKAGE,
    version=VERSION,
    description="Extension CustomUrlAvatar",
    author="Andre Klitzing",
    packages=[str("custom_url_avatar")],
    entry_points={
        'reviewboard.extensions':
            '%s = custom_url_avatar.extension:CustomUrlAvatar' % PACKAGE,
    },
    package_data={
        b'custom_url_avatar': [
            'templates/custom_url_avatar/*.txt',
            'templates/custom_url_avatar/*.html',
        ],
    }
)
