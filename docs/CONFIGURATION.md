# Configuration Guide

Hướng dẫn cấu hình Codebase Tracker.

## Tổng quan

Ứng dụng sử dụng file `_codebase/settings.json` để quản lý các quy tắc quét. File được tự động tạo khi chọn dự án lần đầu.

---

## Cấu trúc settings.json

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
    ".git/", "node_modules/", "dist/", "build/",
    "__pycache__/", "*.log", "*.tmp"
  ],
  "description": "Configure multiple output files based on track patterns."
}
```

---

## Các tùy chọn cấu hình

### track_config

Định nghĩa các nhóm output file:

| Thuộc tính | Mô tả | Ví dụ |
|------------|-------|-------|
| `name` | Tên file output (không có `.txt`) | `"backend"` |
| `tracks` | Pattern glob các file cần quét | `["src/**/*.ts"]` |
| `ignore_patterns` | Pattern glob riêng để bỏ qua | `["**/*.test.ts"]` |

**Ví dụ nhiều output:**

```json
{
  "track_config": [
    {
      "name": "frontend",
      "tracks": ["src/components/**/*", "src/pages/**/*"],
      "ignore_patterns": ["**/*.test.*"]
    },
    {
      "name": "backend",
      "tracks": ["api/**/*", "server/**/*"],
      "ignore_patterns": []
    }
  ]
}
```

→ Tạo ra `frontend.txt` và `backend.txt`

### global_ignore_patterns

Danh sách pattern bỏ qua toàn cục (áp dụng cho tất cả configs):

```json
{
  "global_ignore_patterns": [
    ".git/",
    "node_modules/",
    "vendor/",
    "dist/",
    "build/",
    "__pycache__/",
    "*.log",
    "*.lockb"
  ]
}
```

> **Note**: Ứng dụng tự động đọc thêm quy tắc từ `.gitignore` của dự án.

---

## Pattern Syntax

Sử dụng glob pattern (gitwildmatch style):

| Pattern | Match |
|---------|-------|
| `*` | Bất kỳ file nào trong folder hiện tại |
| `**/*` | Tất cả file trong folder và subfolder |
| `*.ts` | Tất cả file `.ts` trong folder hiện tại |
| `**/*.ts` | Tất cả file `.ts` ở mọi cấp độ |
| `src/` | Toàn bộ folder `src` |
| `!test/` | Không bao gồm folder `test` |

---

## Các nút chức năng

- **Edit Settings**: Mở file `settings.json` trong editor mặc định
- **Reset Settings**: Khôi phục cấu hình về mặc định

---

## Output Files

Sau khi scan, các file được tạo trong `_codebase/`:

| File | Mô tả |
|------|-------|
| `codebase_structure.txt` | Cây thư mục của dự án |
| `{config_name}.txt` | Nội dung source code theo từng config |

**Format output tối ưu cho AI:**

```
# codebase | 42 files | 2026-01-07 21:50:00

// src/app.ts
export class App {
  ...
}

// src/utils/helper.ts
export function helper() {
  ...
}
```
