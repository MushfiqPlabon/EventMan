import pytest
from django.contrib.staticfiles.storage import staticfiles_storage


@pytest.fixture(autouse=True, scope="session")
def mock_static_files_globally(session_mocker):
    session_mocker.patch.object(
        staticfiles_storage, "url", return_value="/mock/static/url.js"
    )


@pytest.fixture(autouse=True, scope="session")
def mock_cloudinary_uploader_upload_globally(session_mocker):
    session_mocker.patch(
        "cloudinary.uploader.upload",
        return_value={
            "secure_url": "http://mock.cloudinary.com/image.jpg",
            "public_id": "mock_public_id",
        },
    )
