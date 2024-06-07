from reviewboard.extensions.packaging import setup


PACKAGE = "rbCustomUrlAvatar"
VERSION = "1.1.0"

setup(
    name=PACKAGE,
    version=VERSION,
    description='Review Board extension: CustomUrlAvatar',
    author='Andre Klitzing',
    author_email='aklitzing@gmail.com',
    url='https://github.com/misery/CustomUrlAvatar',
    packages=[str('custom_url_avatar')],
    install_requires=[
        'reviewboard>=6.0',
    ],
    entry_points={
        'reviewboard.extensions':
            '%s = custom_url_avatar.extension:CustomUrlAvatar' % PACKAGE,
    },
    package_data={
        'custom_url_avatar': [
            'templates/custom_url_avatar/*.txt',
            'templates/custom_url_avatar/*.html',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Review Board',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
