"""
This is an image provider as WSGI script.

You create a directory /opt/images or something
like that and add images like this.

/opt/images/klitzing
/opt/images/klitzing.square

The script will use .square files if they
exist.

You can call this on your server with
http://yoursite/img/?user=klitzing&s=45
or without a size
http://yoursite/img/?user=klitzing

Also you can pass a mail adress:
http://yoursite/img/?user=andre.klitzing@company.de
It will check if "klitzing" file exists.

Snippet for mod_wsgi on Apache

  WSGIPassAuthorization On
  WSGIScriptAlias "/img/" "/var/www/htdocs/img.wsgi/"
"""

import cgi
import datetime as dt
import os
import os.path
import re
import requests
import subprocess
from requests_ntlm import HttpNtlmAuth


ntlm_user = 'USER'
ntlm_psw = '123456'
ntlm_url = 'http://some_ntlm_site/picture_%s_thumb.jpg'
cache_path = '/opt/images/'
mail_suffix = '@company'
unknown = 'unknown'


def get_cache_file(user):
	return cache_path + user


def resize_cache_file(cache_file, size):
	resized_file = cache_file + '_' + size
	if not os.path.exists(resized_file):
		subprocess.call(['convert', cache_file, '-resize', size, resized_file])
		trim_cache_file(resized_file)

	return resized_file


def trim_cache_file(cache_file):
	subprocess.call(['mogrify', '-trim', cache_file])

	type = get_type(cache_file)
	if 'jpeg' in type:
		subprocess.call(['jpegoptim', '-s', cache_file])
	elif 'png' in type:
		subprocess.call(['pngquant', '-f', cache_file, '-o', cache_file])


def download_image(user, cache_file):
	session = requests.Session()
	session.auth = HttpNtlmAuth(ntlm_user, ntlm_psw, session)
	r = session.get(ntlm_url % user)
	if r.status_code == 200:
		with open(cache_file, 'wb') as f:
			f.write(r.content)
		f.close()
		trim_cache_file(cache_file)
		return True
	return False


def get_square_file(cache_file):
	square_file = cache_file + '.square'
	if os.path.exists(square_file):
		return square_file

	return None


def get_final_image(form):
	user = unknown
	if 'user' in form:
		user = form['user'].value.lower()
		if mail_suffix in user or '.' in user:
			user = user.split('@')[0].replace('<', '')

			full = user.replace('.', '')
			if os.path.exists(get_cache_file(full)):
				user = full
			else:
				user = user.split('.')[-1]
		if not user.isalpha():
			user = unknown

	cache_file = get_cache_file(user)
	if os.path.exists(cache_file):
		square_file = get_square_file(cache_file)
		cache_file = square_file if square_file else cache_file
	else:
		if not download_image(user, cache_file):
			cache_file = get_cache_file(unknown)

	if 's' in form:
		s = form['s'].value
		if s.isdigit():
			cache_file = resize_cache_file(cache_file, s)

	return cache_file


def get_last_modified(file):
	try:
		mtime = os.path.getmtime(file)
	except OSError:
		return None

	last_modified_date = dt.datetime.fromtimestamp(mtime)
	return last_modified_date.strftime('%a, %d %b %Y %H:%M:%S GMT')


def get_type(file):
	type = 'image'

	try:
		import magic
	except ImportError:
		return type

	ms = magic.open(magic.NONE)
	ms.load()
	data = ms.file(file)
	if 'JPEG' in data:
		type = 'image/jpeg'
	elif 'PNG' in data:
		type = 'image/png'

	return type


def get_header(file):
	header = []

	header.append(('Content-Type', get_type(file)))
	header.append(('Access-Control-Allow-Origin', '*'))

	mDate = get_last_modified(file)
	if mDate:
		header.append(('Last-Modified', mDate))

	return header


def application(environ, start_response):
	form = cgi.FieldStorage(
		fp=environ['wsgi.input'],
		environ=environ,
		keep_blank_values=True)

	final_file = get_final_image(form)
	start_response('200 OK', get_header(final_file))

	f = open(final_file, 'rb')
	if 'wsgi.file_wrapper' in environ:
		return environ['wsgi.file_wrapper'](f)

	return f.read()
