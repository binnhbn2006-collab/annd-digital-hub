# ANND Digital Hub — bản demo

Đây là ứng dụng minh họa cho sáng kiến phục vụ bài dự thi. Dữ liệu mẫu được lưu bằng SQLite trong tệp `annd_hub_demo.db`.

## 1. Yêu cầu
- Máy tính Windows 10/11, macOS hoặc Linux
- Python 3.10 trở lên
- Kết nối Internet lần đầu để cài thư viện (nếu chưa có sẵn)
- Có kết nối Internet khi chạy để tải logo tham chiếu từ cổng thông tin Học viện: https://hvannd.edu.vn/storage/logo/main-logo.png

## 2. Cài đặt trên Windows
1. Giải nén ZIP vào một thư mục dễ tìm, ví dụ `Desktop\annd_digital_hub_demo`.
2. Cài Python từ https://www.python.org/downloads/ nếu máy chưa có. Khi cài, tích chọn **Add Python to PATH**.
3. Mở thư mục vừa giải nén.
4. Bấm vào thanh địa chỉ của File Explorer, gõ `cmd` rồi nhấn Enter.
5. Trong cửa sổ Command Prompt, chạy lần lượt:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Nếu lệnh `py` không chạy, thử thay bằng `python`.

## 3. Mở ứng dụng
Sau lệnh `streamlit run app.py`, trình duyệt thường tự mở địa chỉ cục bộ:
`http://localhost:8501`

Nếu không tự mở, sao chép địa chỉ đó vào Chrome/Edge.

## 4. Cách trình diễn
- Chọn **Tổng quan** để giới thiệu bảng điều hành.
- Vào **Thư viện học liệu** để tìm kiếm và thêm học liệu mẫu.
- Vào **Nghiên cứu khoa học** để thêm đề tài, thay đổi tiến độ.
- Vào **Tiếp nhận sáng kiến** để gửi ý tưởng và cập nhật trạng thái.
- Vào **Giới thiệu mô hình** để trình bày phạm vi và giới hạn.

Dữ liệu được lưu trên máy chạy ứng dụng. Không nhập dữ liệu nội bộ, dữ liệu cá nhân thật hoặc thông tin thuộc bí mật nhà nước.

## 5. Dừng và chạy lại
- Dừng ứng dụng: quay lại cửa sổ Command Prompt và nhấn `Ctrl + C`.
- Chạy lại: mở Command Prompt trong thư mục dự án, kích hoạt môi trường:
  `.venv\Scripts\activate`
  rồi chạy:
  `streamlit run app.py`

## 6. Lưu ý quan trọng
Giao diện sử dụng logo tham chiếu từ cổng thông tin Học viện An ninh nhân dân và bảng màu xanh lá, đỏ, vàng theo hướng trang trọng. Logo được tải từ địa chỉ chính thức nên cần kết nối Internet để hiển thị. Tên ANND Digital Hub là tên mô hình đề xuất, không có nghĩa đây là hệ thống được Học viện ban hành.

Đây là bản demo chạy cục bộ để minh họa ý tưởng. Bản này **chưa có đăng nhập/phân quyền thực, chưa được thẩm định an toàn và không được dùng để quản lý dữ liệu chính thức**. Muốn triển khai tại đơn vị cần được cấp có thẩm quyền phê duyệt, rà soát pháp lý, an toàn thông tin và kiến trúc hạ tầng.
