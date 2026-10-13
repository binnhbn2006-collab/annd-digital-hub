# ANND Digital Hub — bản nâng cấp trình diễn

## Chức năng
- Đăng nhập, đăng xuất và phân quyền theo 3 vai trò: Học viên, Giảng viên/Người phụ trách, Quản trị viên.
- Thư viện học liệu: tìm kiếm, lọc chủ đề, thêm học liệu, duyệt/ẩn học liệu.
- Nghiên cứu khoa học: học viên tạo hồ sơ và cập nhật tiến độ; người phụ trách xem xét, cập nhật trạng thái và phản hồi.
- Sáng kiến: học viên gửi vấn đề, giải pháp, lợi ích; người phụ trách phản hồi và cập nhật trạng thái.
- Quản trị viên tạo/khóa/mở khóa tài khoản và xem nhật ký hoạt động.
- SQLite để chạy trên máy cá nhân; hỗ trợ PostgreSQL qua biến `DATABASE_URL` để triển khai có lưu trữ bền vững hơn.

> Đây là nguyên mẫu độc lập phục vụ học tập và dự thi, không phải hệ thống chính thức của Học viện An ninh nhân dân. Không đưa dữ liệu nội bộ, hồ sơ thật, thông tin cá nhân nhạy cảm hoặc tài liệu mật vào ứng dụng. Các tài khoản dưới đây là tài khoản mẫu và phải đổi/xóa trước khi demo công khai.

## Tài khoản mẫu
- Học viên: `hocvien` / `Hocvien@123`
- Giảng viên/người phụ trách: `giangvien` / `Giangvien@123`
- Quản trị viên: `admin` / `Admin@123`

Mật khẩu được lưu dạng băm PBKDF2 trong cơ sở dữ liệu, không lưu dạng văn bản thuần. Tuy vậy, các mật khẩu mẫu được ghi công khai trong README nên chỉ dùng cho demo.

## Chạy trên Windows
1. Cài Python 3.10 trở lên.
2. Giải nén thư mục này.
3. Mở thư mục `ANND_Digital_Hub_Pro`, nhấn thanh địa chỉ File Explorer, gõ `cmd`, nhấn Enter.
4. Chạy từng lệnh:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

5. Mở địa chỉ hiện trong cửa sổ CMD (thường là `http://localhost:8501`). Để dừng ứng dụng, nhấn `Ctrl+C` trong CMD.

## Đưa lên GitHub
Tải lên các tệp `app.py`, `requirements.txt`, `README_HUONG_DAN.md` ở thư mục gốc của repository. Không tải `.venv`, tệp `.db`, mật khẩu thật hay tệp `.streamlit/secrets.toml` lên GitHub.

## Triển khai Streamlit Community Cloud
1. Mở https://share.streamlit.io/ và kết nối GitHub.
2. Chọn repository, branch `main`, main file path `app.py`.
3. Nhấn Deploy.
4. **Lưu ý về dữ liệu:** SQLite trên máy cá nhân lưu dữ liệu trong tệp `annd_hub.db`, nhưng hệ thống tệp của ứng dụng trên môi trường cloud có thể bị thay thế khi khởi động lại/triển khai lại. Để lưu lâu dài trên cloud, cần tạo cơ sở dữ liệu PostgreSQL riêng (ví dụ Supabase) và đặt `DATABASE_URL` trong phần Secrets của Streamlit Cloud.

### Thiết lập PostgreSQL cho lưu trữ lâu dài
1. Tạo dự án PostgreSQL riêng tại nhà cung cấp phù hợp, ví dụ Supabase; lấy connection string dạng `postgresql://...` (ưu tiên chuỗi kết nối phù hợp môi trường IPv4/pooler nếu nhà cung cấp hướng dẫn).
2. Trên Streamlit Cloud, mở ứng dụng → Settings → Secrets.
3. Thêm cấu hình TOML:

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
```

Thay các phần USER, PASSWORD, HOST, DATABASE bằng thông tin do nhà cung cấp cấp. Không chia sẻ URL này, không đưa vào GitHub và không gửi trong ảnh chụp màn hình. Ứng dụng tự chuyển `postgresql://` sang driver `psycopg`.
4. Lưu Secrets và khởi động lại ứng dụng. Bảng và tài khoản mẫu được tạo tự động nếu database còn trống.

## Giới hạn và bảo mật
- Phân quyền trong nguyên mẫu phục vụ demo; chưa được kiểm thử/xác nhận an toàn cho sử dụng chính thức.
- Tài khoản mẫu được khởi tạo khi database trống. Nếu demo công khai, hãy xóa hoặc thay đổi các tài khoản mẫu; không dùng chung dữ liệu nhạy cảm.
- Trước khi áp dụng thật cần đánh giá bảo mật, HTTPS, chính sách mật khẩu, giới hạn đăng nhập, khôi phục mật khẩu, sao lưu/khôi phục, quản lý phiên, kiểm soát tải tệp và phân quyền chi tiết.
- Không tích hợp tài khoản, dữ liệu hoặc hạ tầng nội bộ của Học viện nếu chưa được cấp phép.
