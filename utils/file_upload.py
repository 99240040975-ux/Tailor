import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename


DEFAULT_ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
}


def allowed_file(filename, allowed_extensions=None):
    """Return True when the filename has an allowed extension."""
    if not filename or "." not in filename:
        return False

    extensions = allowed_extensions or DEFAULT_ALLOWED_EXTENSIONS

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in {
        str(item).lower()
        for item in extensions
    }


def _get_upload_folder():
    """Get the configured upload directory."""
    upload_folder = current_app.config.get("UPLOAD_FOLDER")

    if not upload_folder:
        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
        )

    os.makedirs(upload_folder, exist_ok=True)

    return upload_folder


def save_uploaded_file(file, folder_name="reference"):
    """
    Safely save an uploaded image.

    Returns a web-relative path such as:
        uploads/reference/unique_filename.jpg

    Returns None when:
    - no file was provided
    - the filename is empty
    - the extension is not allowed
    - the filename cannot be secured
    """

    if not file:
        return None

    original_name = getattr(file, "filename", "")

    if not original_name or not original_name.strip():
        return None

    allowed_extensions = current_app.config.get(
        "ALLOWED_IMAGE_EXTENSIONS",
        DEFAULT_ALLOWED_EXTENSIONS,
    )

    if not allowed_file(
        original_name,
        allowed_extensions,
    ):
        return None

    safe_filename = secure_filename(original_name)

    if not safe_filename:
        return None

    if "." not in safe_filename:
        return None

    extension = safe_filename.rsplit(
        ".",
        1,
    )[1].lower()

    folder_name = str(folder_name or "reference").strip()

    # Prevent folder traversal.
    folder_name = os.path.basename(
        folder_name.replace("\\", "/")
    )

    if not folder_name:
        folder_name = "reference"

    upload_root = _get_upload_folder()

    destination_directory = os.path.join(
        upload_root,
        folder_name,
    )

    os.makedirs(
        destination_directory,
        exist_ok=True,
    )

    unique_filename = (
        f"{uuid.uuid4().hex}_{safe_filename}"
    )

    destination_path = os.path.join(
        destination_directory,
        unique_filename,
    )

    file.save(destination_path)

    return (
        f"uploads/{folder_name}/"
        f"{unique_filename}"
    )


def delete_uploaded_file(relative_path):
    """
    Delete a previously uploaded file.

    Accepts a web-relative path such as:
        uploads/reference/example.jpg

    Returns True when deleted, otherwise False.
    """

    if not relative_path:
        return False

    relative_path = str(relative_path).replace(
        "/",
        os.sep,
    )

    upload_root = os.path.abspath(
        _get_upload_folder()
    )

    static_folder = current_app.static_folder
    if not static_folder:
        static_folder = current_app.root_path

    file_path = os.path.abspath(
        os.path.join(
            static_folder,
            relative_path,
        )
    )

    # Only delete files inside static/uploads.
    allowed_root = os.path.abspath(
        upload_root
    )

    try:
        if os.path.commonpath(
            [file_path, allowed_root]
        ) != allowed_root:
            return False
    except ValueError:
        return False

    if not os.path.isfile(file_path):
        return False

    try:
        os.remove(file_path)
        return True
    except OSError:
        return False