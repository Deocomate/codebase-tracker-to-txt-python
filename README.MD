# Codebase Tracker

![Codebase Tracker Logo](icon.ico)

## Tổng quan

Codebase Tracker là một ứng dụng Python giúp quét và gộp toàn bộ mã nguồn dự án của bạn thành một tệp văn bản duy nhất.
Được thiết kế đặc biệt để phục vụ các mục đích AI, giúp các mô hình AI như ChatGPT, Claude, và các trợ lý AI khác hiểu
toàn bộ cấu trúc và chi tiết của codebase một cách nhanh chóng và chính xác.

## Tính năng chính

- **Gộp mã nguồn**: Kết hợp tất cả các tệp văn bản trong dự án thành một tệp duy nhất
- **Phân loại thông minh**: Phân biệt giữa tệp văn bản và tệp nhị phân
- **Hỗ trợ quy tắc ignore**: Tự động nhận diện và tuân thủ quy tắc `.gitignore`
- **Tùy chỉnh ignore**: Cho phép tùy chỉnh thêm các quy tắc bỏ qua qua tệp `.watchignore`
- **Kéo & thả đơn giản**: Dễ dàng chọn thư mục dự án bằng cách kéo và thả
- **Giao diện thân thiện**: Hiển thị tiến trình quét và thông tin kết quả trực quan

## Tại sao cần Codebase Tracker?

Khi làm việc với AI để phân tích hoặc hỗ trợ phát triển code, việc cung cấp toàn bộ context của dự án thường gặp các trở
ngại:

- Giới hạn về kích thước đầu vào của các mô hình AI
- Khó khăn trong việc chọn lọc file phù hợp để cung cấp cho AI
- Thiếu cấu trúc và tổ chức khi chia sẻ nhiều file
- Mất thời gian để cắt dán từng file riêng lẻ

Codebase Tracker giải quyết các vấn đề này bằng cách tạo ra một tệp duy nhất với cấu trúc rõ ràng, đánh dấu đường dẫn
file, và bỏ qua các file không liên quan, giúp AI hiểu codebase một cách toàn diện hơn.

## Yêu cầu hệ thống

- Python 3.7 trở lên
- Hệ điều hành: Windows, macOS, hoặc Linux
- Các thư viện phụ thuộc trong file `requirements.txt`

## Cài đặt và sử dụng

### Phương pháp 1: Chạy từ mã nguồn

1. Clone hoặc tải xuống dự án:

```bash
git clone https://github.com/your-username/codebase-tracker.git
cd codebase-tracker
```

2. Cài đặt các thư viện phụ thuộc:

```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:

```bash
python main.py
```

### Phương pháp 2: Chạy từ file thực thi (.exe)

1. Tải xuống file .exe từ trang Releases
2. Chạy file `codebase-tracker.exe`

## Hướng dẫn sử dụng

1. **Chọn thư mục dự án**:
    - Nhấn nút "Browse" để chọn thư mục dự án, hoặc
    - Kéo và thả thư mục dự án vào ô nhập liệu đường dẫn

2. **Quét và tạo tệp tổng hợp**:
    - Nhấn nút "Scan & Generate" để bắt đầu quét dự án
    - Theo dõi tiến trình qua thanh tiến độ và nhật ký

3. **Xem kết quả**:
    - Sau khi hoàn thành, thống kê về số lượng file và ký tự sẽ hiển thị
    - Nhấn "Open Output File" để mở tệp kết quả, hoặc
    - Nhấn "Open Output Directory" để mở thư mục chứa tệp kết quả

4. **Tùy chỉnh quy tắc bỏ qua**:
    - Nhấn "Edit .watchignore" để tùy chỉnh các quy tắc bỏ qua bổ sung
    - Định dạng giống với file `.gitignore`

## Tệp kết quả

Tệp `codebase.txt` được tạo trong thư mục `.codebase` của dự án và chứa:

- **Header**: Thông tin tổng quan về thời gian tạo, tên dự án, số lượng file
- **Nội dung file text**: Toàn bộ nội dung của các file văn bản, đi kèm đường dẫn
- **Danh sách file nhị phân**: Đường dẫn đến các file nhị phân
- **Danh sách mục bỏ qua**: Các thư mục và file bị bỏ qua theo quy tắc

## Xây dựng file thực thi (.exe)

Để đóng gói ứng dụng thành file .exe:

1. Cài đặt PyInstaller:

```bash
pip install pyinstaller
```

2. Tạo file .exe từ thư mục dự án:

```bash
# Đơn giản nhất
pyinstaller --name codebase-tracker --onefile --windowed main.py

# Hoặc chi tiết hơn với icon và thông tin bổ sung
pyinstaller --name "Codebase Tracker" --onefile --windowed --icon=icon.ico --add-data "icon.ico;." main.py
```

3. File thực thi sẽ được tạo trong thư mục `dist/`

### Lưu ý khi build .exe:

- Đảm bảo các thư viện phụ thuộc đã được cài đặt trước khi build
- Nếu gặp lỗi với tkinterdnd2, hãy thêm option `--hidden-import tkinterdnd2` vào lệnh PyInstaller
- Trên Windows, có thể cần thêm option `--collect-all tkinterdnd2` để đảm bảo đóng gói đầy đủ

## Sử dụng với các mô hình AI

1. **Chạy ứng dụng và tạo tệp tổng hợp** cho dự án cần phân tích
2. **Mở tệp `codebase.txt`** trong thư mục `.codebase`
3. **Sao chép nội dung** và dán vào cuộc hội thoại với AI
4. **Yêu cầu AI phân tích** với các câu hỏi cụ thể về dự án

Ví dụ câu hỏi hiệu quả:

- "Hãy giải thích cấu trúc tổng thể của dự án này."
- "Có vấn đề bảo mật tiềm ẩn nào trong code không?"
- "Làm thế nào để tôi có thể cải thiện hiệu suất của chức năng X?"
- "Hãy giúp tôi thêm tính năng Y vào dự án này."

## Giấy phép

Phần mềm này được phân phối dưới giấy phép MIT. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

Phát triển bởi Minh Long | © 2025 - Codebase Tracker