import os
import mimetypes
from pathlib import Path
import chardet

# Binary file extensions - always skip
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

# Force text extensions - override MIME type detection
# This fixes .ts files being detected as video/mp2t (MPEG Transport Stream)
FORCE_TEXT_EXTENSIONS = {
    'ts', 'tsx', 'mts', 'cts',      # TypeScript
    'jsx',                           # React JSX
    'vue', 'svelte',                 # Frontend frameworks
    'astro', 'mdx',                  # Content frameworks
    'prisma', 'graphql', 'gql',      # Schema languages
    'tf', 'tfvars',                  # Terraform
    'proto',                         # Protocol Buffers
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
    """Determine if a file is likely a text file that can be safely read."""
    file_path = Path(file_path)
    ext = file_path.suffix.lower().lstrip('.')

    # 1. Check common text files by name
    if file_path.name.lower() in COMMON_TEXT_FILES:
        return True

    # 2. Check .env and .lock files
    if file_path.name.endswith('.env') or file_path.name.endswith('.lock'):
        return True

    # 3. Skip known binary extensions
    if ext in NON_TEXT_EXTENSIONS:
        return False

    # 4. Force text for modern dev extensions (fixes .ts MIME issue)
    if ext in FORCE_TEXT_EXTENSIONS:
        return True

    # 5. Check MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type:
        if any(mime_type.startswith(prefix) for prefix in READABLE_MIME_PREFIXES):
            return True
        if (mime_type.startswith('image/') or mime_type.startswith('audio/') or
                mime_type.startswith('video/') or mime_type.startswith('font/')):
            return False

    # 6. Fallback: check for NULL bytes and detect encoding
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(4096)
            if not chunk:
                return True
            if b'\0' in chunk:
                return False
        result = chardet.detect(chunk)
        encoding = result.get('encoding')
        confidence = result.get('confidence', 0)
        if encoding and confidence > 0.5:
            return True
        try:
            chunk.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    except (IOError, OSError):
        return False


def detect_encoding(file_path: str, sample_size: int = 8192) -> str:
    """Detect file encoding using chardet with safe fallback."""
    try:
        with open(file_path, 'rb') as f:
            raw = f.read(sample_size)
        if not raw:
            return 'utf-8'
        result = chardet.detect(raw)
        encoding = result.get('encoding')
        confidence = result.get('confidence', 0)
        if encoding and confidence > 0.5:
            return encoding
        return 'utf-8'
    except (IOError, OSError):
        return 'utf-8'


def format_file_size(size_bytes):
    """Format file size in a human-readable format."""
    if size_bytes == 0:
        return "0 Bytes"
    size_units = ["Bytes", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_units[i]}"


def ensure_directory(directory_path):
    """Ensure a directory exists, create it if it doesn't."""
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_relative_path(file_path, base_path):
    """Get the path of a file relative to the base path."""
    return os.path.relpath(file_path, base_path)
