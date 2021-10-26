import pytest

import asf_search as asf


@pytest.fixture
def s1_results():
    return asf.search(
        platform=[asf.PLATFORM.SENTINEL1],
        maxResults=10)


@pytest.fixture
def s1_metadata_results():
    return asf.search(
        platform=[asf.PLATFORM.SENTINEL1],
        processingLevel=[asf.PRODUCT_TYPE.METADATA_SLC],
        maxResults=10)


def test_length(s1_results):
    assert len(s1_results) > 0


def test_download(s1_metadata_results):
    assert(s1_metadata_results.download(dir='./', token='abcde'))