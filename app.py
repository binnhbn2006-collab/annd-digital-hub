# -*- coding: utf-8 -*-
"""
ANND Digital Hub - mô hình minh họa phục vụ học tập và dự thi.
Chỉ dùng dữ liệu giả lập, không đưa dữ liệu nội bộ hoặc nhạy cảm vào ứng dụng.
Chạy: streamlit run app.py
"""
import sqlite3
from pathlib import Path
from datetime import date
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "annd_hub_demo.db"
# Logo tham chiếu từ cổng thông tin chính thức của Học viện An ninh nhân dân.
APP_LOGO_URL = "https://hvannd.edu.vn/storage/logo/main-logo.png"

st.set_page_config(
    page_title="ANND Digital Hub | Học viện An ninh nhân dân",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            owner TEXT NOT NULL,
            progress INTEGER NOT NULL,
            status TEXT NOT NULL,
            due_date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            proposer TEXT NOT NULL,
            problem TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        count = conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO resources(title,category,source,status,created_at) VALUES(?,?,?,?,?)",
                [
                    ("Hướng dẫn kỹ năng nghiên cứu khoa học", "Nghiên cứu khoa học", "Tài liệu minh họa", "Đã duyệt", "2026-09-15"),
                    ("Nhập môn an toàn thông tin", "Công nghệ", "Tài liệu minh họa", "Đã duyệt", "2026-09-20"),
                    ("Phương pháp học tập chủ động", "Kỹ năng học tập", "Tài liệu minh họa", "Chờ rà soát", "2026-10-01"),
                    ("Đạo đức và liêm chính học thuật", "Nghiên cứu khoa học", "Tài liệu minh họa", "Đã duyệt", "2026-10-05"),
                ],
            )
        count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO projects(title,owner,progress,status,due_date) VALUES(?,?,?,?,?)",
                [
                    ("Ứng dụng công cụ số hỗ trợ học tập", "Nhóm nghiên cứu A", 65, "Đang thực hiện", "2026-12-15"),
                    ("Khảo sát nhu cầu học liệu số", "Nhóm nghiên cứu B", 35, "Đang thực hiện", "2026-11-30"),
                    ("Xây dựng bộ tiêu chí đánh giá sáng kiến", "Nhóm nghiên cứu C", 100, "Hoàn thành", "2026-10-10"),
                ],
            )
        count = conn.execute("SELECT COUNT(*) FROM ideas").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO ideas(title,proposer,problem,status,created_at) VALUES(?,?,?,?,?)",
                [
                    ("Mẫu biểu điện tử theo dõi đề tài", "Học viên minh họa", "Giảm thao tác tổng hợp tiến độ", "Đang xem xét", "2026-10-03"),
                    ("Danh mục học liệu theo chủ đề", "Giảng viên minh họa", "Hỗ trợ tìm tài liệu nhanh hơn", "Đã tiếp nhận", "2026-10-08"),
                ],
            )

init_db()

# Style
st.markdown("""
<style>
:root { --hvannd-green: #176b43; --hvannd-red: #b51f2b; --hvannd-gold: #e2b642; }
.block-container {padding-top: 1.25rem; padding-bottom: 2rem;}
.hero {
    padding: 1.15rem 1.4rem; border-radius: 12px;
    background: linear-gradient(110deg, #145b3b 0%, #176b43 72%, #1d754c 100%);
    border-top: 4px solid #e2b642;
    color: white; margin-bottom: 1rem;
}
.hero h1 {font-size: 1.85rem; margin: 0 0 .35rem 0; color: white; letter-spacing: .01em;}
.hero p {margin: 0; opacity: .96;}
.hero .institution {font-size: .92rem; font-weight: 700; letter-spacing: .045em; margin-bottom: .45rem;}
.small-note {font-size: .85rem; color: #64748b;}
[data-testid="stSidebar"] {border-right: 3px solid #e2b642;}
[data-testid="stSidebar"] h3 {color: #176b43;}
.stButton button[kind="primary"] {background: #176b43; border-color: #176b43;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    try:
        st.image(APP_LOGO_URL, width=112)
    except Exception:
        st.markdown("### HỌC VIỆN AN NINH NHÂN DÂN")
    st.markdown("### ANND Digital Hub")
    st.caption("Không gian số hỗ trợ học tập và nghiên cứu")
    st.caption("Mô hình đề xuất • Dữ liệu giả lập")
    page = st.radio(
        "Điều hướng",
        ["Tổng quan", "Thư viện học liệu", "Nghiên cứu khoa học", "Tiếp nhận sáng kiến", "Giới thiệu mô hình"],
        label_visibility="visible",
    )
    st.divider()
    st.caption("Phiên bản thử nghiệm phục vụ trình diễn.")
    st.caption("Không dùng để lưu dữ liệu nội bộ hoặc dữ liệu nhạy cảm.")

logo_col, title_col = st.columns([1, 7], vertical_alignment="center")
with logo_col:
    try:
        st.image(APP_LOGO_URL, width=92)
    except Exception:
        st.markdown("### HVANND")
with title_col:
    st.markdown("""
    <div class="hero">
      <div class="institution">HỌC VIỆN AN NINH NHÂN DÂN</div>
      <h1>ANND Digital Hub</h1>
      <p>Không gian số kết nối học tập, nghiên cứu khoa học và đổi mới sáng tạo</p>
    </div>
    """, unsafe_allow_html=True)

def read_df(query, params=()):
    with get_conn() as conn:
        return pd.read_sql_query(query, conn, params=params)

def metric_row():
    resources = read_df("SELECT * FROM resources")
    projects = read_df("SELECT * FROM projects")
    ideas = read_df("SELECT * FROM ideas")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Học liệu mẫu", len(resources))
    c2.metric("Đề tài nghiên cứu", len(projects))
    c3.metric("Sáng kiến tiếp nhận", len(ideas))
    c4.metric("Đề tài hoàn thành", int((projects["status"] == "Hoàn thành").sum()) if not projects.empty else 0)

if page == "Tổng quan":
    st.subheader("Bảng điều hành")
    st.write("Tổng hợp dữ liệu minh họa của các phân hệ. Các con số thay đổi khi bạn thêm hoặc cập nhật hồ sơ.")
    metric_row()
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("### Tiến độ đề tài")
        projects = read_df("SELECT title AS 'Tên đề tài', owner AS 'Đơn vị/nhóm phụ trách', progress AS 'Tiến độ (%)', status AS 'Trạng thái' FROM projects")
        st.dataframe(projects, use_container_width=True, hide_index=True)
        if not projects.empty:
            chart_df = projects[["Tên đề tài", "Tiến độ (%)"]].set_index("Tên đề tài")
            st.bar_chart(chart_df)
    with right:
        st.markdown("### Trạng thái sáng kiến")
        ideas = read_df("SELECT status, COUNT(*) AS so_luong FROM ideas GROUP BY status")
        if not ideas.empty:
            st.bar_chart(ideas.set_index("status"))
        st.markdown("### Hoạt động gần đây")
        recent = read_df("SELECT title AS 'Nội dung', created_at AS 'Ngày ghi nhận' FROM ideas ORDER BY id DESC LIMIT 5")
        st.dataframe(recent, use_container_width=True, hide_index=True)
    st.info("Lưu ý: Dữ liệu trên được tạo sẵn để minh họa giao diện, không phải số liệu thực tế của Học viện.")

elif page == "Thư viện học liệu":
    st.subheader("Thư viện học liệu số")
    st.write("Chỉ quản lý thông tin danh mục học liệu mẫu. Chức năng tải tài liệu thật chưa được bật.")
    with st.expander("＋ Thêm học liệu mẫu", expanded=False):
        with st.form("resource_form", clear_on_submit=True):
            title = st.text_input("Tên học liệu", placeholder="Ví dụ: Phương pháp nghiên cứu khoa học")
            category = st.selectbox("Chủ đề", ["Nghiên cứu khoa học", "Công nghệ", "Kỹ năng học tập", "Lý luận chính trị", "Khác"])
            source = st.text_input("Nguồn tài liệu", value="Tài liệu minh họa")
            status = st.selectbox("Trạng thái rà soát", ["Chờ rà soát", "Đã duyệt"])
            submitted = st.form_submit_button("Lưu học liệu")
            if submitted:
                if not title.strip():
                    st.error("Bạn cần nhập tên học liệu.")
                else:
                    with get_conn() as conn:
                        conn.execute(
                            "INSERT INTO resources(title,category,source,status,created_at) VALUES(?,?,?,?,?)",
                            (title.strip(), category, source.strip() or "Chưa khai báo", status, date.today().isoformat())
                        )
                    st.success("Đã thêm học liệu mẫu.")
                    st.rerun()
    q = st.text_input("Tìm kiếm học liệu", placeholder="Nhập tên hoặc chủ đề...")
    df = read_df("SELECT id AS 'Mã', title AS 'Tên học liệu', category AS 'Chủ đề', source AS 'Nguồn', status AS 'Trạng thái', created_at AS 'Ngày tạo' FROM resources")
    if q:
        mask = df.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
        df = df[mask]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Trong triển khai thật, cần bổ sung phê duyệt tài liệu, phân quyền truy cập và kiểm soát bản quyền.")

elif page == "Nghiên cứu khoa học":
    st.subheader("Quản lý nghiên cứu khoa học")
    with st.expander("＋ Thêm đề tài", expanded=False):
        with st.form("project_form", clear_on_submit=True):
            title = st.text_input("Tên đề tài")
            owner = st.text_input("Người/nhóm phụ trách")
            progress = st.slider("Tiến độ (%)", 0, 100, 0)
            status = st.selectbox("Trạng thái", ["Mới đề xuất", "Đang thực hiện", "Chờ nghiệm thu", "Hoàn thành", "Tạm dừng"])
            due = st.date_input("Ngày dự kiến hoàn thành", value=date(2026, 12, 31))
            submitted = st.form_submit_button("Lưu đề tài")
            if submitted:
                if not title.strip() or not owner.strip():
                    st.error("Vui lòng nhập tên đề tài và người/nhóm phụ trách.")
                else:
                    with get_conn() as conn:
                        conn.execute(
                            "INSERT INTO projects(title,owner,progress,status,due_date) VALUES(?,?,?,?,?)",
                            (title.strip(), owner.strip(), int(progress), status, due.isoformat())
                        )
                    st.success("Đã thêm đề tài.")
                    st.rerun()
    projects = read_df("SELECT id AS 'Mã', title AS 'Tên đề tài', owner AS 'Phụ trách', progress AS 'Tiến độ (%)', status AS 'Trạng thái', due_date AS 'Hạn dự kiến' FROM projects ORDER BY id DESC")
    st.dataframe(projects, use_container_width=True, hide_index=True)
    st.markdown("### Cập nhật tiến độ")
    ids = read_df("SELECT id, title FROM projects")
    if not ids.empty:
        chosen = st.selectbox("Chọn đề tài", ids["id"].tolist(), format_func=lambda x: f"#{x} — {ids.loc[ids.id == x, 'title'].iloc[0]}")
        current = read_df("SELECT progress, status FROM projects WHERE id=?", (int(chosen),)).iloc[0]
        with st.form("update_project_form"):
            new_progress = st.slider("Tiến độ mới (%)", 0, 100, int(current["progress"]))
            new_status = st.selectbox("Trạng thái mới", ["Mới đề xuất", "Đang thực hiện", "Chờ nghiệm thu", "Hoàn thành", "Tạm dừng"], index=["Mới đề xuất", "Đang thực hiện", "Chờ nghiệm thu", "Hoàn thành", "Tạm dừng"].index(current["status"]))
            if st.form_submit_button("Cập nhật"):
                with get_conn() as conn:
                    conn.execute("UPDATE projects SET progress=?, status=? WHERE id=?", (int(new_progress), new_status, int(chosen)))
                st.success("Đã cập nhật.")
                st.rerun()

elif page == "Tiếp nhận sáng kiến":
    st.subheader("Cổng tiếp nhận sáng kiến")
    st.write("Quy trình mẫu: tiếp nhận → đánh giá chuyên môn → thẩm định an toàn → thí điểm → đánh giá kết quả.")
    with st.expander("＋ Gửi sáng kiến", expanded=True):
        with st.form("idea_form", clear_on_submit=True):
            title = st.text_input("Tên sáng kiến")
            proposer = st.text_input("Người đề xuất (tên giả lập)")
            problem = st.text_area("Vấn đề cần giải quyết", placeholder="Mô tả ngắn gọn vấn đề và lợi ích dự kiến...")
            submitted = st.form_submit_button("Gửi đề xuất")
            if submitted:
                if not title.strip() or not proposer.strip() or not problem.strip():
                    st.error("Vui lòng điền đủ các trường bắt buộc.")
                else:
                    with get_conn() as conn:
                        conn.execute(
                            "INSERT INTO ideas(title,proposer,problem,status,created_at) VALUES(?,?,?,?,?)",
                            (title.strip(), proposer.strip(), problem.strip(), "Đã tiếp nhận", date.today().isoformat())
                        )
                    st.success("Đã ghi nhận sáng kiến mẫu.")
                    st.rerun()
    ideas = read_df("SELECT id AS 'Mã', title AS 'Tên sáng kiến', proposer AS 'Người đề xuất', problem AS 'Vấn đề', status AS 'Trạng thái', created_at AS 'Ngày gửi' FROM ideas ORDER BY id DESC")
    st.dataframe(ideas, use_container_width=True, hide_index=True)
    st.markdown("### Cập nhật trạng thái xử lý")
    raw = read_df("SELECT id, title, status FROM ideas")
    if not raw.empty:
        statuses = ["Đã tiếp nhận", "Đang đánh giá", "Cần bổ sung", "Được chọn thí điểm", "Không lựa chọn", "Đã hoàn thành"]
        chosen = st.selectbox("Chọn sáng kiến", raw["id"].tolist(), format_func=lambda x: f"#{x} — {raw.loc[raw.id == x, 'title'].iloc[0]}")
        old_status = raw.loc[raw.id == chosen, "status"].iloc[0]
        with st.form("update_idea_form"):
            new_status = st.selectbox("Trạng thái", statuses, index=statuses.index(old_status) if old_status in statuses else 0)
            if st.form_submit_button("Lưu trạng thái"):
                with get_conn() as conn:
                    conn.execute("UPDATE ideas SET status=? WHERE id=?", (new_status, int(chosen)))
                st.success("Đã cập nhật trạng thái.")
                st.rerun()

else:
    st.subheader("Giới thiệu mô hình")
    st.markdown("""
    ### Mục đích
    Mô phỏng không gian số tích hợp hỗ trợ học tập, nghiên cứu khoa học và tiếp nhận sáng kiến.

    ### Phạm vi phiên bản hiện tại
    - Giao diện tổng quan và số liệu mẫu.
    - Danh mục học liệu giả lập, có tìm kiếm và thêm mới.
    - Quản lý đề tài giả lập, cập nhật tiến độ.
    - Tiếp nhận sáng kiến và cập nhật trạng thái.
    - Lưu dữ liệu demo bằng SQLite trên máy chạy ứng dụng.

    ### Chưa có trong phiên bản demo
    - Đăng nhập và phân quyền thật.
    - Kết nối hệ thống chính thức của Học viện.
    - Tích hợp AI.
    - Thẩm định bảo mật cho triển khai thực tế.
    - Cơ chế sao lưu, giám sát và vận hành ở quy mô tổ chức.

    ### Nguyên tắc sử dụng
    Chỉ sử dụng dữ liệu giả lập hoặc dữ liệu công khai được phép. Không nhập tài liệu nội bộ, dữ liệu cá nhân thật hoặc thông tin thuộc bí mật nhà nước.
    """)

st.divider()
st.caption("ANND Digital Hub • Mô hình đề xuất phục vụ học tập và trình bày sáng kiến • Không phải hệ thống chính thức của Học viện.")
