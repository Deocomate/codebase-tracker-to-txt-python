# Codebase Tracker

<div align="center">
  <img src="icon.png" alt="Codebase Tracker Logo" width="128">
  
  **Quét và gộp mã nguồn thành văn bản tối ưu cho AI**
  
  [![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)]()
</div>

---

## 📋 Tổng quan

**Codebase Tracker** là công cụ Python với GUI hiện đại, giúp quét và gộp toàn bộ mã nguồn dự án thành file văn bản được tối ưu cho các AI như ChatGPT, Claude, Gemini.

### Tính năng chính

- 🖱️ **Drag & Drop** - Kéo thả thư mục trực tiếp vào ứng dụng
- 📁 **Multi-output** - Tạo nhiều file output theo cấu hình và format
- 🌳 **Cây thư mục** - Tự động tạo sơ đồ cấu trúc dự án
- ⚡ **Tối ưu token** - Output gọn gàng, tiết kiệm token cho AI
- 🔧 **Cấu hình linh hoạt** - Hỗ trợ `.gitignore` và custom patterns
- 📋 **Auto Copy File** - Copy nhanh 2 file output vào clipboard dạng file

---

## 🚀 Cài đặt nhanh

### Yêu cầu

- Python 3.12+
- Git

### Cài đặt

```bash
# Clone repository
git clone https://github.com/your-username/codebase-tracker-to-txt-python.git
cd codebase-tracker-to-txt-python

# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python3 main.py
```

<details>
<summary><b>📦 Sử dụng file thực thi (không cần Python)</b></summary>

Tải file `.exe` / `.app` từ [Releases](https://github.com/your-username/codebase-tracker-to-txt-python/releases).

</details>

<details>
<summary><b>🐧 Hướng dẫn cài đặt chi tiết cho Linux</b></summary>

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk git
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip python3-tkinter git
```

</details>

---

## 📖 Hướng dẫn sử dụng

1. **Khởi động** - Chạy `python3 main.py`
2. **Chọn dự án** - Kéo thả hoặc Browse thư mục
3. **Scan & Generate** - Nhấn nút để bắt đầu
4. **Kết quả** - Mở thư mục `_codebase/` hoặc bấm **Auto Copy File** để copy file

### Output Files

| File | Mô tả |
|------|-------|
| `codebase_structure.txt` | Cây thư mục dự án |
| `{config}.{format}` | Nội dung source code theo format đã chọn |

---

## ⚙️ Cấu hình

Ứng dụng sử dụng `_codebase/settings.json` để quản lý quy tắc quét:

```json
{
  "track_config": [
    {
      "name": "codebase",
      "tracks": ["*"],
      "ignore_patterns": []
    }
  ],
  "global_ignore_patterns": [
    ".git/", "node_modules/", "dist/", "*.log"
  ]
}
```

📄 **Chi tiết:** [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 🏗️ Cấu trúc dự án

```
codebase-tracker-to-txt-python/
├── main.py                 # Entry point
├── app/
│   ├── core/               # Business logic
│   │   ├── scanner.py      # File scanning
│   │   ├── combiner.py     # Content combining
│   │   ├── processor.py    # Processing orchestration
│   │   └── ignore_rules.py # Pattern matching
│   ├── utils/              # Utilities
│   │   └── file_utils.py   # File type detection
│   └── gui/                # User interface
│       └── ui.py           # Tkinter GUI
├── docs/                   # Documentation
│   ├── BUILD.md            # Build instructions
│   └── CONFIGURATION.md    # Configuration guide
└── requirements.txt        # Dependencies
```

---

## 🛠️ Build

Đóng gói ứng dụng thành file thực thi độc lập.

📄 **Hướng dẫn chi tiết:** [docs/BUILD.md](docs/BUILD.md)

**Quick build (macOS):**
```bash
pip install pyinstaller
pyinstaller "Codebase Tracker.spec" --clean
```

---

## 📄 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

<div align="center">
  Phát triển bởi <b>Minh Long</b> | © 2025
</div>
