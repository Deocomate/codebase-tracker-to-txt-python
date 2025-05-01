import os
import mimetypes
import chardet
from pathlib import Path

# Common binary file extensions
NON_TEXT_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'ico', 'heic', 'heif', 'avif',
    'icns', 'cur', 'mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a', 'opus', 'mp4', 'mov',
    'avi', 'mkv', 'webm', 'flv', 'wmv', 'woff', 'woff2', 'ttf', 'otf', 'eot', 'zip',
    'rar', 'tar', 'gz', '7z', 'bz2', 'xz', 'iso', 'img', 'dmg', 'pdf', 'doc', 'docx',
    'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp', 'key', 'numbers', 'pages', 'exe',
    'dll', 'so', 'dylib', 'app', 'msi', 'deb', 'rpm', 'jar', 'db', 'sqlite', 'sqlite3',
    'mdb', 'accdb', 'sqlitedb', 'bin', 'dat', 'class', 'pyd', 'pyc', 'pyo', 'o', 'a',
    'lib', 'swf', 'psd', 'ai', 'eps', 'bak', 'tmp', 'temp', 'swp'
}

# MIME types that are typically text-based
READABLE_MIME_PREFIXES = [
    'text/', 'application/json', 'application/xml', 'application/javascript',
    'application/typescript', 'application/x-httpd-php', 'application/x-sh',
    'application/xhtml+xml', 'image/svg+xml', 'application/yaml',
    'application/toml', 'application/sql', 'application/rtf', 'application/csv'
]

# Common files that are always text regardless of extension
COMMON_TEXT_FILES = [
    'dockerfile', 'makefile', 'readme', 'license', 'authors', 'changelog',
    'contributing', 'procfile', 'gemfile', 'rakefile', 'jenkinsfile', 'vagrantfile',
    'pipeline', '.env', '.gitattributes', '.gitignore', '.gitmodules', '.npmrc',
    '.yarnrc', '.npmignore', '.babelrc', '.eslintrc', '.prettierrc', '.editorconfig',
    '.browserslistrc', 'requirements.txt', 'pipfile', 'go.mod', 'go.sum', 'composer.json',
    'composer.lock', 'package.json', 'package-lock.json', 'yarn.lock', 'tsconfig.json',
    'manifest.json', 'config.xml', 'pom.xml', 'build.gradle', 'settings.gradle',
    'cmakelists.txt'
]


def is_text_file(file_path):
    """
    Determine if a file is likely a text file that can be safely read.
    Returns True if file is text, False if not.
    """
    file_path = Path(file_path)

    # Check by name for common text files - check this first to ensure these are always treated as text
    if file_path.name.lower() in COMMON_TEXT_FILES:
        return True

    # Special case for .env files and lock files
    if file_path.name.endswith('.env') or file_path.name.endswith('.lock'):
        return True

    # Skip by extension
    if file_path.suffix.lower().lstrip('.') in NON_TEXT_EXTENSIONS:
        return False

    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type:
        if any(mime_type.startswith(prefix) for prefix in READABLE_MIME_PREFIXES):
            return True
        if (mime_type.startswith('image/') or mime_type.startswith('audio/') or
                mime_type.startswith('video/') or mime_type.startswith('font/')):
            return False

    # For files without extension or unknown MIME type, try to detect encoding
    try:
        if file_path.stat().st_size > 1024 * 1024:  # Skip files larger than 1MB
            return False

        # Read a sample of the file to detect encoding
        with open(file_path, 'rb') as f:
            sample = f.read(4096)  # Read first 4KB
            if not sample:
                return True  # Empty file is considered text

            # Try to detect the encoding
            result = chardet.detect(sample)
            return result['encoding'] is not None and result['confidence'] > 0.7
    except (IOError, OSError):
        return False

    # Default to non-text if we couldn't determine
    return False


def format_file_size(size_bytes):
    """Format file size in a human-readable format"""
    if size_bytes == 0:
        return "0 Bytes"

    size_units = ["Bytes", "KB", "MB", "GB", "TB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_units) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.2f} {size_units[i]}"


def ensure_directory(directory_path):
    """Ensure a directory exists, create it if it doesn't"""
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_relative_path(file_path, base_path):
    """Get the path of a file relative to the base path"""
    return os.path.relpath(file_path, base_path)
