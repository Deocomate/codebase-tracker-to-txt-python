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

## Tại sao cần Codebase Tracker?

Khi làm việc với AI để phân tích hoặc hỗ trợ phát triển code, việc cung cấp toàn bộ context của dự án thường gặp các trở ngại:

- Giới hạn về kích thước đầu vào của các mô hình AI.
- Khó khăn trong việc chọn lọc file phù hợp để cung cấp cho AI.
- Thiếu cấu trúc và tổ chức khi chia sẻ nhiều file.
- Mất thời gian để sao chép và dán nội dung từng file riêng lẻ.

Codebase Tracker giải quyết các vấn đề này bằng cách tạo ra một tệp duy nhất với cấu trúc rõ ràng, giúp AI hiểu codebase một cách toàn diện và hiệu quả hơn.

## Yêu cầu hệ thống

- Python 3.7 trở lên
- Hệ điều hành: Windows, macOS, hoặc Linux
- Các thư viện phụ thuộc trong file `requirements.txt`

## Cài đặt và sử dụng

### Phương pháp 1: Chạy từ mã nguồn

1.  Clone hoặc tải xuống dự án:
    ```bash
    git clone [https://github.com/your-username/codebase-tracker.git](https://github.com/your-username/codebase-tracker.git)
    cd codebase-tracker
    ```
2.  Cài đặt các thư viện phụ thuộc:
    ```bash
    pip install -r requirements.txt
    ```
3.  Chạy ứng dụng:
    ```bash
    python main.py
    ```

### Phương pháp 2: Chạy từ file thực thi (.exe)

1.  Tải xuống file .exe từ trang Releases.
2.  Chạy file `codebase-tracker.exe`.

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

## Xây dựng file thực thi (.exe)

Để đóng gói ứng dụng thành file .exe cho Windows:

1.  Cài đặt PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Chạy lệnh build từ thư mục gốc của dự án:
    ```bash
    pyinstaller --name "Codebase Tracker" --onefile --windowed --icon=icon.ico --add-data "icon.ico;." main.py
    ```
    * `--windowed`: Ẩn cửa sổ dòng lệnh khi chạy ứng dụng.
    * `--onefile`: Đóng gói thành một file .exe duy nhất.
    * `--icon`: Đặt icon cho ứng dụng.
    * Có thể cần thêm `--collect-all tkinterdnd2` nếu PyInstaller không tự tìm thấy thư viện.

3.  File thực thi sẽ được tạo trong thư mục `dist/`.

## Giấy phép

Phần mềm này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

---

Phát triển bởi Minh Long | © 2025 - Codebase Tracker
