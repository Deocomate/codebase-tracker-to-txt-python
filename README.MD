# Codebase Tracker

![Codebase Tracker Logo](icon.png)

## Tổng quan

**Codebase Tracker** là một công cụ Python mạnh mẽ với giao diện đồ họa (GUI) hiện đại, giúp bạn quét, phân tích và gộp toàn bộ mã nguồn dự án thành một tệp văn bản duy nhất. Công cụ này được thiết kế đặc biệt để tối ưu hóa quy trình làm việc với các mô hình AI như ChatGPT, Claude, Gemini, giúp AI hiểu sâu và toàn diện về cấu trúc cũng như nội dung dự án của bạn.

## 🌟 Tính năng nổi bật

*   **Giao diện hiện đại & Dễ sử dụng**: Hỗ trợ Kéo & Thả (Drag & Drop) thư mục dự án trực tiếp vào ứng dụng.
*   **Gộp mã nguồn thông minh**: Tự động quét và gộp nội dung của tất cả các tệp văn bản vào `codebase.txt`.
*   **Cây thư mục trực quan**: Tạo sơ đồ cấu trúc thư mục giúp AI dễ dàng hình dung tổ chức dự án.
*   **Hệ thống Cấu hình linh hoạt**:
    *   Tự động tuân thủ `.gitignore`.
    *   Quản lý tập trung qua `codebase_tracker_settings.json`.
    *   Hỗ trợ chế độ `track_only` (chỉ quét file chỉ định) và `ignore_patterns` (bỏ qua file).
    *   Tự động phát hiện và bỏ qua các tệp nhị phân (binary files).
*   **Thống kê & Báo cáo**: Hiển thị số lượng file, tổng dung lượng và các file bị bỏ qua.
*   **Sao chép nhanh**: Tính năng "Copy to Clipboard" giúp đưa toàn bộ context vào AI chỉ với một cú click.

## 🚀 Cài đặt

### Yêu cầu hệ thống
*   **Python**: Phiên bản 3.7 trở lên (Khuyến nghị 3.9+).
*   **Git**: Để clone mã nguồn.
*   **Hệ điều hành**: Windows 10+, macOS 10.14+, Ubuntu 18.04+ (và các distro Linux khác).

### 1. Windows

**Cách 1: Chạy từ mã nguồn (Khuyến nghị cho Developer)**

1.  Mở Command Prompt (cmd) hoặc PowerShell.
2.  Clone repository:
    ```bash
    git clone https://github.com/your-username/codebase-tracker-to-txt-python.git
    cd codebase-tracker-to-txt-python
    ```
3.  Tạo và kích hoạt môi trường ảo (tùy chọn nhưng khuyến nghị):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
4.  Cài đặt các thư viện cần thiết:
    ```bash
    pip install -r requirements.txt
    ```
5.  Chạy ứng dụng:
    ```bash
    python main.py
    ```

**Cách 2: Sử dụng file thực thi (.exe)**
*   Tải file `.exe` mới nhất từ mục [Releases](https://github.com/your-username/codebase-tracker-to-txt-python/releases).
*   Chạy trực tiếp không cần cài đặt Python.

---

### 2. macOS

1.  Mở Terminal.
2.  Cài đặt Python 3 và Git (nếu chưa có) qua Homebrew:
    ```bash
    brew install python git
    ```
3.  Cài đặt `python-tk` (cần thiết cho giao diện):
    ```bash
    brew install python-tk
    ```
4.  Clone repository:
    ```bash
    git clone https://github.com/your-username/codebase-tracker-to-txt-python.git
    cd codebase-tracker-to-txt-python
    ```
5.  Tạo và kích hoạt môi trường ảo:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
6.  Cài đặt thư viện:
    ```bash
    pip install -r requirements.txt
    ```
7.  Chạy ứng dụng:
    ```bash
    python3 main.py
    ```

---

### 3. Linux (Ubuntu/Debian/Fedora)

1.  Mở Terminal.
2.  Cài đặt Python 3, Git và Tkinter:
    *   **Ubuntu/Debian**:
        ```bash
        sudo apt update
        sudo apt install python3 python3-pip python3-venv python3-tk git
        ```
    *   **Fedora**:
        ```bash
        sudo dnf install python3 python3-pip python3-tkinter git
        ```
3.  Clone repository:
    ```bash
    git clone https://github.com/your-username/codebase-tracker-to-txt-python.git
    cd codebase-tracker-to-txt-python
    ```
4.  Tạo và kích hoạt môi trường ảo:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
5.  Cài đặt thư viện:
    ```bash
    pip install -r requirements.txt
    ```
6.  Chạy ứng dụng:
    ```bash
    python3 main.py
    ```

## 📖 Hướng dẫn sử dụng

1.  **Khởi động ứng dụng**: Chạy `python main.py`.
2.  **Chọn dự án**:
    *   Kéo thả thư mục dự án vào cửa sổ ứng dụng.
    *   Hoặc nhấn **"Browse Folder..."** để chọn.
3.  **Quét & Gộp**: Nhấn **"Scan & Generate"**. Ứng dụng sẽ xử lý và hiển thị tiến trình.
4.  **Kết quả**:
    *   Nhấn **"Copy to Clipboard"** để sao chép toàn bộ nội dung.
    *   File kết quả `codebase.txt` (nội dung mã nguồn) và `codebase_structure.txt` (cấu trúc thư mục) sẽ được lưu trong thư mục `_codebase/` bên trong dự án của bạn.
    *   Bạn có thể mở nhanh file hoặc thư mục kết quả bằng các nút tương ứng.

## ⚙️ Cấu hình (Configuration)

Ứng dụng sử dụng file `_codebase/codebase_tracker_settings.json` để quản lý các quy tắc quét. File này sẽ tự động được tạo khi bạn chọn dự án.

**Cấu trúc file:**
```json
{
    "track_only": ["*"],          // Danh sách file/folder CẦN quét (Allow-list). Mặc định "*" là tất cả.
    "ignore_patterns": [          // Danh sách file/folder CẦN BỎ QUA (Deny-list).
        ".git/",
        "node_modules/",
        "*.log"
    ]
}
```

**Các nút chức năng:**
*   **Edit Settings**: Mở file cấu hình JSON để chỉnh sửa.
*   **Reset Settings**: Khôi phục cấu hình về mặc định.

---

## 🛠️ Xây dựng file thực thi (Build)

Nếu bạn muốn đóng gói ứng dụng thành file chạy độc lập:

### Chuẩn bị

```bash
pip install pyinstaller
```

### Build cho Windows

```bash
pyinstaller --name "Codebase Tracker" --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --add-data "icon.png;." --collect-all tkinterdnd2 main.py
```

File `.exe` sẽ được tạo trong thư mục `dist/`.

---

### Build cho macOS

#### Bước 1: Tạo file icon `.icns` (nếu chưa có)

macOS yêu cầu file `.icns` để hiển thị icon trong Finder và Dock. Chạy lệnh sau:

```bash
# Tạo iconset folder với các kích thước cần thiết
mkdir -p icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# Chuyển đổi iconset thành file .icns
iconutil -c icns icon.iconset

# Dọn dẹp (tuỳ chọn)
rm -rf icon.iconset
```

> **Lưu ý**: File `icon.icns` đã được bao gồm sẵn trong repository, bạn chỉ cần chạy bước này nếu muốn tạo lại icon từ file `icon.png` mới.

#### Bước 2: Build ứng dụng

**Cách 1: Sử dụng file `.spec` có sẵn (Khuyến nghị)**

```bash
pyinstaller "Codebase Tracker.spec" --clean
```

**Cách 2: Build thủ công bằng lệnh**

```bash
pyinstaller --name "Codebase Tracker" \
    --onefile \
    --windowed \
    --icon=icon.icns \
    --add-data "icon.png:." \
    --add-data "icon.icns:." \
    --osx-bundle-identifier "com.minhlong.codebasetracker" \
    --collect-all tkinterdnd2 \
    main.py
```

> **Lưu ý**: Trên macOS, dùng dấu hai chấm `:` để ngăn cách trong `--add-data` (Windows dùng dấu chấm phẩy `;`).

#### Bước 3: Kiểm tra kết quả

File `.app` sẽ được tạo trong thư mục `dist/Codebase Tracker.app`. Bạn có thể:

1. **Kéo thả vào Applications**: Di chuyển `Codebase Tracker.app` vào thư mục `/Applications` để cài đặt.
2. **Chạy trực tiếp**: Double-click vào file `.app` trong Finder.

---

### Build cho Linux

```bash
pyinstaller --name "Codebase Tracker" --onefile --windowed --add-data "icon.png:." --collect-all tkinterdnd2 main.py
```

File thực thi sẽ được tạo trong thư mục `dist/`.

---

### Xử lý lỗi thường gặp

| Lỗi | Giải pháp |
|-----|-----------|
| `ModuleNotFoundError: tkinterdnd2` | Cài đặt: `pip install tkinterdnd2` |
| Icon không hiển thị trên macOS | Đảm bảo đã tạo file `icon.icns` và sử dụng file `.spec` có cấu hình đúng |
| App bị block bởi Gatekeeper (macOS) | Chuột phải → Open → Open lần đầu, hoặc xoá extended attributes: `xattr -cr "dist/Codebase Tracker.app"` |
| Permission denied (Linux) | Cấp quyền thực thi: `chmod +x "dist/Codebase Tracker"` |

---

## 📄 Giấy phép

Dự án này được phân phối dưới giấy phép **MIT License**. Xem file `LICENSE` để biết thêm chi tiết.

---

Phát triển bởi Minh Long | © 2025 - Codebase Tracker
