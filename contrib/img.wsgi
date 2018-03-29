#!/usr/bin/env python2
"""
This is an image provider as WSGI script.

You can create a directory /opt/images or something
like that and add images.

/opt/images/klitzing

You need to pass the CACHE_PATH as an environment
variable to the script.

You can call this on your server with
http://yoursite/?user=klitzing&s=45
or without a size
http://yoursite/?user=klitzing

Also you can pass a mail adress:
http://yoursite/?user=andre.klitzing@company.de
It will check if "klitzing" file exists.
"""

import datetime as dt
import logging
import os
import json
import urllib3
import certifi
import hashlib
from PIL import Image


class Cache(object):
    class CacheFile(object):
        def __init__(self, path):
            self.path = path

        def __repr__(self):
            return 'CacheFile: %s - %s - %s' % \
                        (self.path, self.getType(), self.getSize())

        def getLastModified(self):
            try:
                mtime = os.path.getmtime(self.path)
            except OSError:
                return None

            last_modified_date = dt.datetime.fromtimestamp(mtime)
            return last_modified_date.strftime('%a, %d %b %Y %H:%M:%S GMT')

        def getSize(self):
            return 0 if self.path is None else os.path.getsize(self.path)

        def getFile(self):
            return os.path.basename(self.path)

        def getPath(self):
            return self.path

        def getType(self):
            with Image.open(self.path) as f:
                return f.format

    def __init__(self):
        env = 'CACHE_PATH'
        self.dir = os.environ[env] if env in os.environ else None
        self.gen = None
        if self.dir and os.path.exists(self.dir):
            self.gen = self.dir + '/generated'
            if not os.path.exists(self.gen):
                os.makedirs(self.gen)
        else:
            logging.error('CACHE_PATH not defined or does not exist')

    def _path(self, dir, identifier):
        if not dir or not identifier:
            return None

        return os.path.realpath(dir + '/' + identifier)

    def _exists(self, identifier):
        p = self._path(self.dir, identifier)
        if p and os.path.exists(p):
            return p

        p = self._path(self.gen, identifier)
        if p and os.path.exists(p):
            return p

        return None

    def exists(self, identifier):
        # hiding path for public API
        p = self._exists(identifier)
        return True if p else False

    def getFile(self, identifier):
        p = self._exists(identifier)
        if p:
            return Cache.CacheFile(p)

        return None


class Extractor(object):
    def __init__(self, cache):
        self.cache = cache

    def getUser(self, data):
        return None


class UserExtractor(Extractor):
    def __init__(self, cache):
        super(UserExtractor, self).__init__(cache)

    def getUser(self, data):
        return data if self.cache.exists(data) else None


class ReviewBoardExtractor(Extractor):
    class Fetcher():
        def __init__(self, hash, rbhost):

            self.hash = hash
            self.user = None
            self.next = rbhost + ('/api/users/'
                                  '?only-links=&only-fields=username,email')
            self.data = None
            env = 'REVIEWBOARD_MAIL_TLD'
            self.tld = os.environ[env] if env in os.environ else ['de', 'com']

        def _fetch(self):
            try:
                http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                           ca_certs=certifi.where())
                r = http.request('GET', self.next)
                self.data = r.data if r.status == 200 else None
                if self.data is None:
                    self.next = None
            except Exception as e:
                logging.error('Cannot fetch next: %s', e)
                self.data = None
                self.next = None

        def _isDigest(self, mail):
            tld = os.path.splitext(mail.split('@')[1])[1]
            if tld:
                mail = mail[:-len(tld)]

            for entry in self.tld:
                sum = hashlib.md5()
                sum.update(mail + '.' + entry)
                if sum.hexdigest().lower() == self.hash:
                    return True

            return False

        def _parse_data(self):
            self._fetch()
            if self.data is not None:
                parsed = json.loads(self.data)
                if 'next' in parsed['links']:
                    self.next = parsed['links']['next']['href']
                else:
                    self.next = None

                for entry in parsed['users']:
                    if 'email' in entry and entry['email']:
                        mail = entry['email'].lower()
                        if self._isDigest(mail):
                            return entry['username']

            return None

        def getUser(self):
            while self.user is None and self.next is not None:
                self.user = self._parse_data()

            return self.user

    def __init__(self, cache):
        super(ReviewBoardExtractor, self).__init__(cache)
        env = 'REVIEWBOARD_HOST'
        self.rbhost = os.environ[env] if env in os.environ else None
        if not self.rbhost:
            logging.error('REVIEWBOARD_HOST not defined')

    def getUser(self, data):
        if not self.rbhost:
            return None

        f = ReviewBoardExtractor.Fetcher(data, self.rbhost)
        u = f.getUser()
        if u and self.cache.exists(u) and self.cache.gen:
            os.chdir(self.cache.gen)
            if not os.path.exists(data):
                os.symlink('../' + u, data)
            return u

        return None


class MailExtractor(Extractor):
    def __init__(self, cache):
        super(MailExtractor, self).__init__(cache)

    def getUser(self, data):
        if '.' in data:
            data = data.split('@')[0].replace('<', '')
            full = data.replace('.', '')
            if self.cache.exists(full):
                data = full
            else:
                data = data.split('.')[-1]

        if not data.isalpha():
            return None

        return data


class ImageProvider(object):
    def __init__(self):
        self.cache = Cache()
        self.extractor = [UserExtractor(self.cache)]

    def _fetch_cache(self, identifier):
        if self.cache.exists(identifier):
            return self.cache.getFile(identifier)

        return None

    def _resize(self, file, size):
        maxSize = os.environ.get('IMAGE_MAX_SIZE')
        maxSize = 1000 if maxSize is None else int(maxSize)
        if size > maxSize:
            size = maxSize

        if not self.cache.gen:
            return file

        thumbnail = self.cache.gen + '/' + file.getFile() + '_' + str(size)
        if not os.path.exists(thumbnail):
            with Image.open(file.getPath()) as f:
                r = f
                r = r.convert('RGBA' if 'PNG' in f.format else 'RGB')
                r = r.resize((size, size), Image.LANCZOS)
                r.save(thumbnail, f.format)

        return self.cache.CacheFile(thumbnail)

    def addExtractor(self, classname):
        self.extractor.append(classname(self.cache))

    def getImagePath(self, search, size=None):
        for entry in self.extractor:
            user = entry.getUser(search)
            if self.cache.exists(user):
                p = self.cache.getFile(user)
                return self._resize(p, size) if size else p

        return None

    def getDefaultImage(self, size=None):
        p = self._fetch_cache('unknown')
        return self._resize(p, size) if size and p else p


def application(environ, start_response):
    import cgi

    def generateHeader(file=None):
        header = []

        size = '0'
        if file:
            ext = file.getType().lower()
            type = 'image/' + ext

            header.append(('Content-Disposition',
                           str('inline; filename="%s.%s"'
                               % (file.getFile(), ext))))
            header.append(('Content-Type', type))
            header.append(('Access-Control-Allow-Origin', '*'))

            size = str(file.getSize())
            mDate = file.getLastModified()
            if mDate:
                header.append(('Last-Modified', mDate))

        header.append(('Content-Length', size))
        return header

    form = cgi.FieldStorage(
        fp=environ['wsgi.input'],
        environ=environ,
        keep_blank_values=True)

    if not form:
        start_response('405 Method Not Allowed', generateHeader())
        return []

    p = ImageProvider()
    search = None
    if 'user' in form:
        p.addExtractor(MailExtractor)
        search = form.getfirst('user')
    elif 'md5' in form:
        p.addExtractor(ReviewBoardExtractor)
        search = form.getfirst('md5')

    size = None
    if 's' in form:
        s = form.getfirst('s')
        if s.isdigit():
            size = int(s)

    cFile = None
    if search:
        search = search.lower()
        cFile = p.getImagePath(search, size)

    status = '404 Not Found'
    if cFile:
        status = '200 OK'
    else:
        cFile = p.getDefaultImage(size)

    start_response(status, generateHeader(cFile))

    if cFile is None:
        logging.error('No image to return: %s', search)
        return []

    f = open(cFile.getPath(), 'rb')
    if 'wsgi.file_wrapper' in environ:
        return environ['wsgi.file_wrapper'](f)

    def file_wrapper(obj):
        try:
            data = obj.read()
            while data:
                yield data
                data = obj.read()
        finally:
            obj.close()

    return file_wrapper(f)


if __name__ == '__main__':
    import six
    import sys

    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger('image_provider')

    try:
        p = ImageProvider()
        p.addExtractor(MailExtractor)
        p.addExtractor(ReviewBoardExtractor)
        for entry in sys.argv[1:]:
            print(p.getImagePath(entry))
    except Exception as e:
        if logger.getEffectiveLevel() == logging.DEBUG:
            logger.exception('Backtrace of error: %s' % e)
        else:
            for line in six.text_type(e).split('\n'):
                logger.error(line)
