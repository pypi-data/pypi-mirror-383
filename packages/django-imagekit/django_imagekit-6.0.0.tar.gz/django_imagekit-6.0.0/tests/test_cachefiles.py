from hashlib import md5
from unittest import mock
import os

import pytest
from django.conf import settings

from imagekit.cachefiles import ImageCacheFile, LazyImageCacheFile
from imagekit.cachefiles.backends import Simple

from .imagegenerators import TestSpec
from .utils import (DummyAsyncCacheFileBackend, assert_file_is_falsy,
                    assert_file_is_truthy, get_image_file,
                    get_unique_image_file)


def test_no_source_falsiness():
    """
    Ensure cache files generated from sourceless specs are falsy.

    """
    spec = TestSpec(source=None)
    file = ImageCacheFile(spec)
    assert_file_is_falsy(file)


def test_sync_backend_truthiness():
    """
    Ensure that a cachefile with a synchronous cache file backend (the default)
    is truthy.

    """
    with get_unique_image_file() as source_file:
        spec = TestSpec(source=source_file)
        file = ImageCacheFile(spec)
        assert_file_is_truthy(file)


def test_async_backend_falsiness():
    """
    Ensure that a cachefile with an asynchronous cache file backend is falsy.

    """
    with get_unique_image_file() as source_file:
        spec = TestSpec(source=source_file)
        file = ImageCacheFile(spec, cachefile_backend=DummyAsyncCacheFileBackend())
        assert_file_is_falsy(file)


def test_no_source_error():
    spec = TestSpec(source=None)
    file = ImageCacheFile(spec)
    with pytest.raises(TestSpec.MissingSource):
        file.generate()


def test_repr_does_not_send_existence_required():
    """
    Ensure that `__repr__` method does not send `existance_required` signal

    Cachefile strategy may be configured to generate file on
    `existance_required`.
    To generate images, backend passes `ImageCacheFile` instance to worker.
    Both celery and RQ calls `__repr__` method for each argument to enque call.
    And if `__repr__` of object will send this signal, we will get endless
    recursion

    """
    with mock.patch('imagekit.cachefiles.existence_required') as signal:
        # import here to apply mock
        from imagekit.cachefiles import ImageCacheFile

        with get_unique_image_file() as source_file:
            spec = TestSpec(source=source_file)
            file = ImageCacheFile(
                spec,
                cachefile_backend=DummyAsyncCacheFileBackend()
            )
            file.__repr__()
            assert signal.send.called is False


def test_memcached_cache_key():
    """
    Ensure the default cachefile backend is sanitizing its cache key for
    memcached by default.

    """

    class MockFile:
        def __init__(self, name):
            self.name = name

    backend = Simple()
    extra_char_count = len('state-') + len(settings.IMAGEKIT_CACHE_PREFIX)

    length = 199 - extra_char_count
    filename = '1' * length
    file = MockFile(filename)
    assert backend.get_key(file) == '%s%s-state' % (settings.IMAGEKIT_CACHE_PREFIX, file.name)

    length = 200 - extra_char_count
    filename = '1' * length
    file = MockFile(filename)
    assert backend.get_key(file) == '%s%s:%s' % (
        settings.IMAGEKIT_CACHE_PREFIX,
        '1' * (200 - len(':') - 32 - len(settings.IMAGEKIT_CACHE_PREFIX)),
        md5(('%s%s-state' % (settings.IMAGEKIT_CACHE_PREFIX, filename)).encode('utf-8')).hexdigest())


def test_lazyfile_stringification():
    file = LazyImageCacheFile('testspec', source=None)
    assert str(file) == ''
    assert repr(file) == '<ImageCacheFile: None>'

    with get_image_file() as source_file:
        file = LazyImageCacheFile('testspec', source=source_file)
    file.name = 'a.jpg'
    assert str(file) == 'a.jpg'
    assert repr(file) == '<ImageCacheFile: a.jpg>'


def test_generate_file_already_exists(caplog):
    with get_unique_image_file() as source_file:
        spec = TestSpec(source=source_file)
        file_1 = ImageCacheFile(spec)
        file_1._generate()
        # generate another cache image with the same name
        file_2 = ImageCacheFile(spec, name=file_1.name)
        file_2._generate()

    assert len(caplog.records) == 1
    storage, name, actual_name, cachefile_backend = caplog.records[0].args
    assert storage == file_2.storage
    assert name == file_2.name
    assert actual_name != name
    assert os.path.basename(actual_name) in storage.listdir(os.path.dirname(actual_name))[1]
    assert cachefile_backend == file_2.cachefile_backend
