# Codebase Tracker

![Codebase Tracker Logo](icon.ico)

## Tổng quan

**Codebase Tracker** là một công cụ Python mạnh mẽ với giao diện đồ họa (GUI) hiện đại, giúp bạn quét, phân tích và gộp toàn bộ mã nguồn dự án thành một tệp văn bản duy nhất. Công cụ này được thiết kế đặc biệt để tối ưu hóa quy trình làm việc với các mô hình AI như ChatGPT, Claude, Gemini, giúp AI hiểu sâu và toàn diện về cấu trúc cũng như nội dung dự án của bạn.

## 🌟 Tính năng nổi bật

*   **Giao diện hiện đại & Dễ sử dụng**: Hỗ trợ Kéo & Thả (Drag & Drop) thư mục dự án trực tiếp vào ứng dụng.
*   **Gộp mã nguồn thông minh**: Tự động quét và gộp nội dung của tất cả các tệp văn bản vào `codebase.txt`.
*   **Cây thư mục trực quan**: Tạo sơ đồ cấu trúc thư mục giúp AI dễ dàng hình dung tổ chức dự án.
*   **Hệ thống Ignore linh hoạt**:
    *   Tự động tuân thủ `.gitignore`.
    *   Hỗ trợ quy tắc tùy chỉnh qua `.watchignore`.
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

## 🛠️ Xây dựng file thực thi (Build)

Nếu bạn muốn đóng gói ứng dụng thành file chạy độc lập:

1.  Cài đặt PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Chạy lệnh build:
    *   **Windows**:
        ```bash
        pyinstaller --name "Codebase Tracker" --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --collect-all tkinterdnd2 main.py
        ```
    *   **Linux/macOS**:
        ```bash
        pyinstaller --name "Codebase Tracker" --onefile --windowed --add-data "icon.png:." --collect-all tkinterdnd2 main.py
        ```
    *(Lưu ý: Trên Linux/macOS dùng dấu hai chấm `:` để ngăn cách trong `--add-data`, Windows dùng dấu chấm phẩy `;`)*

## 📄 Giấy phép

Dự án này được phân phối dưới giấy phép **MIT License**. Xem file `LICENSE` để biết thêm chi tiết.

---

Phát triển bởi Minh Long | © 2025 - Codebase Tracker
