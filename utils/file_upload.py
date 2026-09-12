import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, folder_name='reference'):
    """
    Saves an uploaded file safely into static/uploads/<folder_name>
    Returns the relative web path (e.g. 'uploads/reference/unique_name.jpg') or None.
    """
    if not file or file.filename == '':
        return None

    allowed_exts = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    if not allowed_file(file.filename, allowed_exts):
        return None

    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

    dest_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, unique_filename)
    file.save(dest_path)

    return f"uploads/{folder_name}/{unique_filename}"
