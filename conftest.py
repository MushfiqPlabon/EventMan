import pytest
from django.contrib.staticfiles.storage import staticfiles_storage

pytest_plugins = ["pytest_mock"]


@pytest.fixture(autouse=True)
def mock_static_files_globally(mocker):
    mocker.patch.object(staticfiles_storage, "url", return_value="/mock/static/url.js")


@pytest.fixture(autouse=True)
def mock_cloudinary_uploader_upload_globally(mocker):
    mocker.patch(
        "cloudinary.uploader.upload",
        return_value={
            "secure_url": "http://mock.cloudinary.com/image.jpg",
            "public_id": "mock_public_id",
        },
    )
