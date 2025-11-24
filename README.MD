# Codebase Tracker

![Codebase Tracker Logo](icon.ico)

## Tổng quan

Codebase Tracker là một ứng dụng Python với giao diện hiện đại giúp quét và gộp toàn bộ mã nguồn dự án của bạn thành một tệp văn bản duy nhất. Được thiết kế đặc biệt để phục vụ các mục đích AI, giúp các mô hình như ChatGPT, Claude, Gemini và các trợ lý AI khác hiểu toàn bộ cấu trúc và chi tiết của codebase một cách nhanh chóng và chính xác.

## Tính năng chính

- **Giao diện hiện đại**: Giao diện người dùng trực quan, sạch sẽ và dễ sử dụng.
- **Kéo & Thả**: Dễ dàng chọn thư mục dự án bằng cách kéo và thả trực tiếp vào ứng dụng.
- **Gộp mã nguồn**: Kết hợp tất cả các tệp văn bản trong dự án thành một tệp duy nhất (`codebase.txt`).
- **Sao chép nhanh**: Nút "Copy to Clipboard" cho phép sao chép toàn bộ nội dung đã gộp chỉ với một cú nhấp chuột.
- **Phân loại thông minh**: Tự động phân biệt giữa tệp văn bản và tệp nhị phân.
- **Hỗ trợ quy tắc ignore**: Tự động nhận diện và tuân thủ các quy tắc trong `.gitignore`.
- **Tùy chỉnh ignore**: Cho phép thêm các quy tắc bỏ qua tùy chỉnh thông qua tệp `.watchignore`.
- **Hiển thị cấu trúc dự án**: Tự động tạo một cây thư mục trong file kết quả để AI dễ dàng hình dung cấu trúc.
- **Thống kê chi tiết**: Cung cấp thông tin trực quan về số lượng file, tổng số ký tự và các mục đã bỏ qua.
- **Manifest JSON chi tiết**: Tạo kèm `manifest.json` ghi lại hash, kích thước và số dòng của từng file, giúp tích hợp dễ dàng với các pipeline AI khác.

## Tại sao cần Codebase Tracker?

Khi làm việc với AI để phân tích hoặc hỗ trợ phát triển code, việc cung cấp toàn bộ context của dự án thường gặp các trở ngại:

- Giới hạn về kích thước đầu vào của các mô hình AI.
- Khó khăn trong việc chọn lọc file phù hợp để cung cấp cho AI.
- Thiếu cấu trúc và tổ chức khi chia sẻ nhiều file.
- Mất thời gian để sao chép và dán nội dung từng file riêng lẻ.

Codebase Tracker giải quyết các vấn đề này bằng cách tạo ra một tệp duy nhất với cấu trúc rõ ràng, giúp AI hiểu codebase một cách toàn diện và hiệu quả hơn.

## Yêu cầu hệ thống

- **Python 3.7 trở lên** (khuyến nghị sử dụng Python 3.9+ để có hiệu suất tốt nhất)
- **Hệ điều hành hỗ trợ**: Windows 10+, macOS 10.14+, Ubuntu 18.04+ và các bản phân phối Linux khác
- **RAM**: Tối thiểu 2GB (khuyến nghị 4GB+ cho các dự án lớn)
- **Dung lượng ổ cứng**: 50MB cho ứng dụng + không gian cho file output tùy thuộc vào kích thước codebase

## Cài đặt chi tiết

### Cài đặt từ mã nguồn (Khuyến nghị cho lập trình viên)

#### Cài đặt trên Windows

1. **Kiểm tra phiên bản Python:**
   ```cmd
   python --version
   ```
   Hoặc:
   ```cmd
   py --version
   ```

2. **Nếu chưa có Python, tải và cài đặt:**
   - Truy cập [python.org](https://www.python.org/downloads/windows/)
   - Tải Python 3.9+ (chọn phiên bản 64-bit)
   - Cài đặt và **quan trọng**: tích vào ô "Add Python to PATH"
   - Khởi động lại Command Prompt sau khi cài đặt

3. **Cài đặt Git (nếu chưa có):**
   ```cmd
   git --version
   ```
   Nếu chưa có, tải từ [git-scm.com](https://git-scm.com/download/win)

4. **Clone dự án:**
   ```cmd
   git clone https://github.com/your-username/codebase-tracker-to-txt-python.git
   cd codebase-tracker-to-txt-python
   ```

5. **Tạo môi trường ảo (khuyến nghị):**
   ```cmd
   python -m venv codebase-tracker-venv
   codebase-tracker-venv\Scripts\activate
   ```

6. **Cài đặt các thư viện phụ thuộc:**
   ```cmd
   pip install -r requirements.txt
   ```

7. **Chạy ứng dụng:**
   ```cmd
   python main.py
   ```

#### Cài đặt trên macOS

1. **Kiểm tra phiên bản Python:**
   ```bash
   python3 --version
   ```

2. **Nếu chưa có Python 3.7+, cài đặt qua Homebrew:**
   ```bash
   # Cài đặt Homebrew (nếu chưa có)
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Cài đặt Python
   brew install python
   ```

3. **Cài đặt Git (nếu chưa có):**
   ```bash
   git --version
   # Nếu chưa có:
   brew install git
   ```

4. **Clone dự án:**
   ```bash
   git clone https://github.com/your-username/codebase-tracker-to-txt-python.git
   cd codebase-tracker-to-txt-python
   ```

5. **Tạo môi trường ảo (khuyến nghị):**
   ```bash
   python3 -m venv codebase-tracker-venv
   source codebase-tracker-venv/bin/activate
   ```

6. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

7. **Cài đặt phụ thuộc cho GUI (nếu cần):**
   ```bash
   # Cho macOS với Python từ Homebrew
   brew install python-tk
   ```

8. **Chạy ứng dụng:**
   ```bash
   python main.py
   ```

#### Cài đặt trên Ubuntu/Linux

1. **Kiểm tra phiên bản Python:**
   ```bash
   python3 --version
   ```

2. **Cài đặt Python 3.7+ (nếu chưa có):**
   ```bash
   # Cho Ubuntu 20.04+
   sudo apt update
   sudo apt install python3 python3-pip python3-venv python3-tk

   # Cho Ubuntu 18.04, có thể cần PPA cho Python mới hơn:
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install python3.9 python3.9-pip python3.9-venv python3.9-tk
   ```

3. **Cài đặt Git (nếu chưa có):**
   ```bash
   sudo apt install git
   ```

4. **Clone dự án:**
   ```bash
   git clone https://github.com/your-username/codebase-tracker-to-txt-python.git
   cd codebase-tracker-to-txt-python
   ```

5. **Tạo môi trường ảo (khuyến nghị):**
   ```bash
   python3 -m venv codebase-tracker-venv
   source codebase-tracker-venv/bin/activate
   ```

6. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

7. **Cài đặt thêm thư viện tkinter (nếu cần):**
   ```bash
   # Cho các hệ thống dựa trên Debian/Ubuntu
   sudo apt install python3-tk

   # Cho Fedora/CentOS
   sudo dnf install python3-tkinter
   ```

8. **Chạy ứng dụng:**
   ```bash
   python main.py
   ```

### Phương pháp 2: Chạy từ file thực thi (Windows only)

1. **Tải xuống file .exe:**
   - Truy cập trang [Releases](https://github.com/your-username/codebase-tracker-to-txt-python/releases)
   - Tải file `codebase-tracker-setup.exe` mới nhất

2. **Cài đặt:**
   - Nhấp đúp vào file .exe đã tải
   - Theo dõi hướng dẫn cài đặt
   - Chọn "Create Desktop Shortcut" để tạo shortcut trên desktop

3. **Chạy ứng dụng:**
   - Từ Start Menu hoặc desktop shortcut
   - Hoặc tìm "Codebase Tracker" trong Windows Search

### Cài đặt nhanh với script (Linux/macOS)

**Script cài đặt tự động cho Linux/macOS:**
```bash
# Tải và chạy script cài đặt
curl -fsSL https://raw.githubusercontent.com/your-username/codebase-tracker-to-txt-python/main/install.sh | bash

# Hoặc tải script về trước rồi chạy
wget https://raw.githubusercontent.com/your-username/codebase-tracker-to-txt-python/main/install.sh
chmod +x install.sh
./install.sh
```

**Script cài đặt tự động cho Windows (PowerShell):**
```powershell
# Tải và chạy script cài đặt
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/your-username/codebase-tracker-to-txt-python/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

### Khắc phục sự cố phổ biến

#### Windows
- **"python is not recognized"**: Cài lại Python và tích "Add Python to PATH"
- **"ModuleNotFoundError: No module named 'tkinter'"**: Cài đặt lại Python với tùy chọn "tcl/tk and IDLE"
- **Lỗi 1603 khi cài đặt Python**: Tắt antivirus tạm thời và chạy installer as Administrator

#### macOS
- **"python3: command not found"**: Cài đặt Python qua Homebrew hoặc python.org
- **Lỗi tkinter**: Xóa Python cũ và cài lại phiên bản đầy đủ từ python.org
- **Permission denied**: Sử dụng `sudo` hoặc kiểm tra quyền truy cập thư mục

#### Linux
- **"ModuleNotFoundError: No module named '_tkinter'"**: Cài đặt `python3-tk` package
- **Permission denied**: Kiểm tra quyền thực thi `chmod +x main.py`
- **Pip không hoạt động**: Sử dụng `python3 -m pip` thay vì `pip`

### Cập nhật ứng dụng

Để cập nhật lên phiên bản mới nhất:

```bash
# Từ mã nguồn
git pull origin main
pip install -r requirements.txt --upgrade

# Hoặc clone lại nếu có thay đổi lớn
rm -rf codebase-tracker-to-txt-python
git clone https://github.com/your-username/codebase-tracker-to-txt-python.git
```

## Hướng dẫn sử dụng

1.  **Chọn thư mục dự án**:
    * Kéo và thả thư mục dự án của bạn vào khu vực được chỉ định trong ứng dụng.
    * Hoặc, nhấn nút "Browse Folder..." để chọn thủ công.

2.  **Quét và tạo tệp tổng hợp**:
    * Nhấn nút "Scan & Generate" để bắt đầu quá trình quét và gộp file.
    * Theo dõi tiến trình qua thanh trạng thái và cửa sổ nhật ký.

3.  **Lấy kết quả**:
    * Sau khi hoàn thành, nhấn **"Copy to Clipboard"** để sao chép toàn bộ nội dung.
    * Nhấn "Open Output File" để mở tệp `codebase.txt` đã tạo.
    * Nhấn "Open Output Directory" để mở thư mục `.codebase` chứa tệp kết quả.

4.  **Tùy chỉnh quy tắc bỏ qua**:
    * Nhấn "Edit .watchignore" để mở và tùy chỉnh các quy tắc bỏ qua bổ sung. Định dạng giống với file `.gitignore`.

## Tệp kết quả

Tệp `codebase.txt` được tạo trong thư mục `.codebase` của dự án và chứa:

- **Header**: Thông tin tổng quan về thời gian tạo, tên dự án, số lượng file.
- **Cấu trúc dự án**: Sơ đồ cây thư mục của dự án.
- **Nội dung file text**: Toàn bộ nội dung của các file văn bản, đi kèm đường dẫn tương đối.
- **Danh sách file nhị phân**: Chỉ liệt kê đường dẫn đến các file nhị phân.
- **Danh sách mục bỏ qua**: Các thư mục và file bị bỏ qua theo quy tắc.
- **Manifest JSON**: Tệp `manifest.json` chứa metadata (SHA-256, kích thước, số dòng tối ưu, quy tắc ignore) của từng file và toàn bộ phiên quét.

## Xây dựng file thực thi (Build)

### Cho Windows (.exe)

1.  Cài đặt PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Chạy lệnh build từ thư mục gốc của dự án:
    ```bash
    pyinstaller --name "Codebase Tracker" --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --collect-all tkinterdnd2 main.py
    ```
    * `--windowed`: Ẩn cửa sổ dòng lệnh khi chạy ứng dụng.
    * `--onefile`: Đóng gói thành một file .exe duy nhất.
    * `--icon`: Đặt icon cho ứng dụng.
    * `--collect-all tkinterdnd2`: Thu thập đầy đủ thư viện kéo thả.

3.  File thực thi sẽ được tạo trong thư mục `dist/`.

### Cho Linux (Binary)

Bạn có thể tạo file thực thi chạy trên Linux (tương tự .exe) bằng cách:

1.  **Sử dụng script có sẵn (Khuyến nghị):**
    ```bash
    chmod +x build_linux.sh
    ./build_linux.sh
    ```

2.  **Hoặc chạy lệnh thủ công:**
    ```bash
    pip install pyinstaller
    pyinstaller --name "Codebase Tracker" --onefile --windowed --add-data "icon.png:." --collect-all tkinterdnd2 main.py
    ```
    * Lưu ý: Trên Linux dùng dấu hai chấm (`:`) để ngăn cách trong `--add-data` thay vì dấu chấm phẩy (`;`).

3.  File thực thi sẽ nằm trong thư mục `dist/` với tên `Codebase Tracker`. Bạn có thể chạy nó bằng cách nhấp đúp hoặc gõ `./dist/"Codebase Tracker"` trong terminal.

## Giấy phép

Phần mềm này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

---

Phát triển bởi Minh Long | © 2025 - Codebase Tracker
