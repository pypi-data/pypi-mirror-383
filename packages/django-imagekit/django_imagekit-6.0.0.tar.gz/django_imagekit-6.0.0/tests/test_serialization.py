"""
Make sure that the various IK classes can be successfully serialized and
deserialized. This is important when using IK with Celery.

"""
import pytest

from imagekit.cachefiles import ImageCacheFile

from .imagegenerators import TestSpec
from .utils import (clear_imagekit_cache, create_photo, get_unique_image_file,
                    pickleback)


@pytest.mark.django_db(transaction=True)
def test_imagespecfield():
    clear_imagekit_cache()
    instance = create_photo('pickletest2.jpg')
    thumbnail = pickleback(instance.thumbnail)
    thumbnail.generate()


@pytest.mark.django_db(transaction=True)
def test_circular_ref():
    """
    A model instance with a spec field in its dict shouldn't raise a KeyError.

    This corresponds to #234

    """
    clear_imagekit_cache()
    instance = create_photo('pickletest3.jpg')
    instance.thumbnail  # Cause thumbnail to be added to instance's __dict__
    pickleback(instance)


def test_cachefiles():
    clear_imagekit_cache()
    with get_unique_image_file() as source_file:
        spec = TestSpec(source=source_file)
        file = ImageCacheFile(spec)
        file.url
        # remove link to file from spec source generator
        # test __getstate__ of ImageCacheFile
        file.generator.source = None
        restored_file = pickleback(file)
        assert file is not restored_file
        # Assertion for #437 and #451
        assert file.storage is restored_file.storage
