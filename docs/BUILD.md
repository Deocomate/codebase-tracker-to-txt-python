# Build Guide

Hướng dẫn đóng gói ứng dụng thành file thực thi độc lập cho các nền tảng.

## Yêu cầu

```bash
pip install pyinstaller
```

---

## Windows

```bash
pyinstaller --name "Codebase Tracker" --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --add-data "icon.png;." --collect-all tkinterdnd2 main.py
```

File `.exe` được tạo trong `dist/`.

---

## macOS

### Bước 1: Tạo icon `.icns` (nếu chưa có)

```bash
mkdir -p icon.iconset && sips -z 16 16 icon.png --out icon.iconset/icon_16x16.png && sips -z 32 32 icon.png --out icon.iconset/icon_16x16@2x.png && sips -z 32 32 icon.png --out icon.iconset/icon_32x32.png && sips -z 64 64 icon.png --out icon.iconset/icon_32x32@2x.png && sips -z 128 128 icon.png --out icon.iconset/icon_128x128.png && sips -z 256 256 icon.png --out icon.iconset/icon_128x128@2x.png && sips -z 256 256 icon.png --out icon.iconset/icon_256x256.png && sips -z 512 512 icon.png --out icon.iconset/icon_256x256@2x.png && sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png && sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png && iconutil -c icns icon.iconset && rm -rf icon.iconset
```

> **Note**: File `icon.icns` đã có sẵn trong repository, nên bước này có thể bỏ qua.

### Bước 2: Build

**Cách 1: Sử dụng file `.spec` (Khuyến nghị)**

```bash
pyinstaller "Codebase Tracker.spec" --clean
```

**Cách 2: Build thủ công**

```bash
pyinstaller --name "Codebase Tracker" --onefile --windowed --icon=icon.icns --add-data "icon.png:." --add-data "icon.icns:." --osx-bundle-identifier "com.minhlong.codebasetracker" --collect-all tkinterdnd2 main.py
```

> **Note**: macOS dùng `:` làm separator trong `--add-data`, Windows dùng `;`.

### Bước 3: Cài đặt

File `.app` tạo trong `dist/Codebase Tracker.app`:

- Kéo thả vào `/Applications` để cài đặt
- Hoặc double-click để chạy trực tiếp

---

## Linux

```bash
pyinstaller --name "Codebase Tracker" --onefile --windowed --add-data "icon.png:." --collect-all tkinterdnd2 main.py
```

Cấp quyền thực thi:

```bash
chmod +x "dist/Codebase Tracker"
```

---

## Xử lý lỗi thường gặp

| Lỗi                                 | Giải pháp                               |
| ----------------------------------- | --------------------------------------- |
| `ModuleNotFoundError: tkinterdnd2`  | `pip install tkinterdnd2`               |
| Icon không hiển thị (macOS)         | Dùng file `.spec` có sẵn                |
| App bị block bởi Gatekeeper (macOS) | `xattr -cr "dist/Codebase Tracker.app"` |
| Permission denied (Linux)           | `chmod +x "dist/Codebase Tracker"`      |
