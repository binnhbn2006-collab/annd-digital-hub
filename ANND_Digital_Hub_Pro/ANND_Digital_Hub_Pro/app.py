# -*- coding: utf-8 -*-
"""ANND Digital Hub - prototype with authentication, role permissions and persistent DB option.
Use sample data only. This is not an official Academy system.
"""
from datetime import datetime, date
import hashlib
import hmac
import os
import secrets
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
from sqlalchemy import (create_engine, String, Integer, Text, Date, DateTime,
                        ForeignKey, select, func, desc)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

APP_DIR = Path(__file__).resolve().parent
DEFAULT_DB = f"sqlite:///{APP_DIR / 'annd_hub.db'}"

st.set_page_config(page_title="ANND Digital Hub", page_icon="🛡️", layout="wide")

# ---------- Database: SQLite locally; PostgreSQL via DATABASE_URL for cloud persistence ----------
def get_database_url():
    url = None
    try:
        url = st.secrets.get("DATABASE_URL", None)
    except Exception:
        pass
    url = url or os.getenv("DATABASE_URL") or DEFAULT_DB
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

DATABASE_URL = get_database_url()
engine_args = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite:"):
    engine_args["connect_args"] = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(20), default="student")
    password_hash: Mapped[str] = mapped_column(String(256))
    active: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(240))
    category: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    status: Mapped[str] = mapped_column(String(30), default="Đã duyệt")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(240))
    objective: Mapped[str] = mapped_column(Text)
    members: Mapped[str] = mapped_column(String(500), default="")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(40), default="Chờ xem xét")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    feedback: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Idea(Base):
    __tablename__ = "ideas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(240))
    problem: Mapped[str] = mapped_column(Text)
    solution: Mapped[str] = mapped_column(Text)
    expected_benefit: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="Mới tiếp nhận")
    feedback: Mapped[str] = mapped_column(Text, default="")
    proposer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# PBKDF2 password hashing. Demo credentials are for demonstration only.
def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 240_000).hex()
    return f"pbkdf2_sha256${salt}${digest}"

def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt, digest = stored.split("$", 2)
        if scheme != "pbkdf2_sha256":
            return False
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 240_000).hex()
        return hmac.compare_digest(check, digest)
    except Exception:
        return False

def log_activity(db, username, action):
    db.add(Activity(username=username, action=action))

def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(func.count(User.id))) == 0:
            db.add_all([
                User(username="hocvien", full_name="Nguyễn Văn A (minh họa)", role="student", password_hash=hash_password("Hocvien@123")),
                User(username="giangvien", full_name="Giảng viên minh họa", role="teacher", password_hash=hash_password("Giangvien@123")),
                User(username="admin", full_name="Quản trị viên minh họa", role="admin", password_hash=hash_password("Admin@123")),
            ])
            db.flush()
            student = db.scalar(select(User).where(User.username == "hocvien"))
            teacher = db.scalar(select(User).where(User.username == "giangvien"))
            db.add_all([
                Resource(title="Hướng dẫn kỹ năng nghiên cứu khoa học", category="Nghiên cứu khoa học", description="Tài liệu mẫu về xác định vấn đề, mục tiêu và phương pháp nghiên cứu.", source_url="https://hvannd.edu.vn/", status="Đã duyệt", created_by=teacher.id),
                Resource(title="Nhập môn an toàn thông tin", category="Công nghệ", description="Mục tài liệu minh họa; thay bằng nguồn hợp pháp đã được kiểm tra.", source_url="https://www.cisa.gov/resources-tools", status="Đã duyệt", created_by=teacher.id),
                Resource(title="Phương pháp học tập chủ động", category="Kỹ năng học tập", description="Tài liệu mẫu về lập kế hoạch học tập.", source_url="", status="Chờ duyệt", created_by=teacher.id),
            ])
            db.add(Project(title="Ứng dụng công cụ số hỗ trợ học tập", objective="Khảo sát khả năng dùng công cụ số để tổ chức học liệu và kế hoạch học tập.", members="Nhóm minh họa", progress=35, status="Đang thực hiện", due_date=date(2026, 12, 15), owner_id=student.id))
            db.add(Idea(title="Danh mục học liệu theo chủ đề", problem="Học viên có thể mất thời gian tìm tài liệu liên quan đến chủ đề nghiên cứu.", solution="Tổ chức danh mục học liệu theo từ khóa và chủ đề.", expected_benefit="Hỗ trợ tìm kiếm học liệu thuận tiện hơn.", status="Mới tiếp nhận", proposer_id=student.id))
            db.commit()

init_db()

# ---------- Styling ----------
st.markdown("""
<style>
.block-container{padding-top:1.3rem;padding-bottom:2.5rem;max-width:1250px}
.hub-hero{background:linear-gradient(115deg,#123d2b,#176b43);border-top:4px solid #e2b642;border-radius:14px;padding:1.4rem 1.6rem;color:#fff;margin-bottom:1rem}
.hub-hero h1{color:#fff;margin:0;font-size:1.8rem}.hub-hero p{color:#e7f1ea;margin:.35rem 0 0}
.small-muted{color:#6b7280;font-size:.88rem}
</style>
""", unsafe_allow_html=True)

ROLE_LABEL = {"student": "Học viên", "teacher": "Giảng viên / Người phụ trách", "admin": "Quản trị viên"}
PROJECT_STATUSES = ["Chờ xem xét", "Đang thực hiện", "Cần chỉnh sửa", "Hoàn thành", "Không chấp thuận"]
IDEA_STATUSES = ["Mới tiếp nhận", "Đang xem xét", "Yêu cầu bổ sung", "Chấp thuận thử nghiệm", "Không chấp thuận", "Đã kết thúc"]

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------- Authentication ----------
def login_screen():
    st.markdown('<div class="hub-hero"><h1>🛡️ ANND DIGITAL HUB</h1><p>Cổng học tập, nghiên cứu khoa học và phát triển sáng kiến — mô hình trình diễn</p></div>', unsafe_allow_html=True)
    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Đăng nhập hệ thống")
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="Nhập tên tài khoản")
            password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu")
            submitted = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)
        if submitted:
            with SessionLocal() as db:
                user = db.scalar(select(User).where(User.username == username.strip(), User.active == 1))
                if user and verify_password(password, user.password_hash):
                    st.session_state.user_id = user.id
                    log_activity(db, user.username, "Đăng nhập")
                    db.commit()
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không đúng, hoặc tài khoản đã bị khóa.")
        st.info("Tài khoản mẫu để thử nghiệm nằm ở khung bên phải. Hãy đổi mật khẩu và cấu hình bảo mật trước khi dùng thực tế.")
    with right:
        st.subheader("Tài khoản trình diễn")
        st.warning("Chỉ là tài khoản mẫu; không dùng mật khẩu này cho tài khoản cá nhân hoặc hệ thống thật.")
        st.markdown("**Học viên**  \nTên đăng nhập: `hocvien`  \nMật khẩu: `Hocvien@123`")
        st.markdown("**Giảng viên / Người phụ trách**  \nTên đăng nhập: `giangvien`  \nMật khẩu: `Giangvien@123`")
        st.markdown("**Quản trị viên**  \nTên đăng nhập: `admin`  \nMật khẩu: `Admin@123`")
        st.caption("Nếu triển khai công khai, các tài khoản mẫu có thể bị người khác dùng thử. Không đưa dữ liệu thật vào ứng dụng.")
    st.divider()
    st.caption("Nguyên mẫu độc lập phục vụ trình diễn ý tưởng; không phải hệ thống chính thức của Học viện An ninh nhân dân.")

with SessionLocal() as db:
    current_user = db.get(User, st.session_state.user_id) if st.session_state.user_id else None
    if current_user and not current_user.active:
        st.session_state.user_id = None
        current_user = None

if not current_user:
    login_screen()
    st.stop()

# ---------- Shared app shell ----------
with st.sidebar:
    st.markdown("## 🛡️ ANND Digital Hub")
    st.caption("Mô hình nền tảng số")
    st.write(f"**{current_user.full_name}**")
    st.caption(ROLE_LABEL[current_user.role])
    st.divider()
    if st.button("Đăng xuất", use_container_width=True):
        with SessionLocal() as db:
            log_activity(db, current_user.username, "Đăng xuất")
            db.commit()
        st.session_state.user_id = None
        st.rerun()
    st.divider()
    st.caption("Dùng dữ liệu mẫu. Không nhập thông tin nội bộ hoặc nhạy cảm.")

st.markdown('<div class="hub-hero"><h1>ANND DIGITAL HUB</h1><p>Kết nối học liệu · Quản lý nghiên cứu · Tiếp nhận và xử lý sáng kiến</p></div>', unsafe_allow_html=True)

pages = ["Tổng quan", "Thư viện học liệu", "Nghiên cứu khoa học", "Tiếp nhận sáng kiến"]
if current_user.role in ("teacher", "admin"):
    pages += ["Xử lý hồ sơ"]
if current_user.role == "admin":
    pages += ["Quản lý tài khoản", "Nhật ký hoạt động"]
page = st.sidebar.radio("Danh mục chức năng", pages)

# ---------- Dashboard ----------
if page == "Tổng quan":
    with SessionLocal() as db:
        resource_count = db.scalar(select(func.count(Resource.id)).where(Resource.status == "Đã duyệt")) or 0
        if current_user.role == "student":
            project_count = db.scalar(select(func.count(Project.id)).where(Project.owner_id == current_user.id)) or 0
            idea_count = db.scalar(select(func.count(Idea.id)).where(Idea.proposer_id == current_user.id)) or 0
        else:
            project_count = db.scalar(select(func.count(Project.id))) or 0
            idea_count = db.scalar(select(func.count(Idea.id))) or 0
        pending_ideas = db.scalar(select(func.count(Idea.id)).where(Idea.status.in_(["Mới tiếp nhận", "Đang xem xét", "Yêu cầu bổ sung"]))) or 0
    st.subheader(f"Xin chào, {current_user.full_name}")
    st.write("Sử dụng các phân hệ bên trái để tìm học liệu, theo dõi đề tài và quản lý sáng kiến theo quyền tài khoản.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Học liệu đã duyệt", resource_count)
    c2.metric("Đề tài của tôi" if current_user.role == "student" else "Tổng đề tài", project_count)
    c3.metric("Sáng kiến của tôi" if current_user.role == "student" else "Tổng sáng kiến", idea_count)
    c4.metric("Hồ sơ cần xem xét", pending_ideas if current_user.role != "student" else "—")
    st.markdown("### Bạn có thể làm gì?")
    a, b, c = st.columns(3)
    a.info("**Thư viện học liệu**\n\nTìm theo tên, chủ đề; mở liên kết nguồn khi có.")
    b.info("**Nghiên cứu khoa học**\n\nTạo hồ sơ đề tài, cập nhật tiến độ và xem phản hồi.")
    c.info("**Tiếp nhận sáng kiến**\n\nGửi vấn đề, giải pháp, lợi ích dự kiến và theo dõi trạng thái.")
    if current_user.role in ("teacher", "admin"):
        st.warning("Bạn có quyền xem xét hồ sơ. Hãy mở mục **Xử lý hồ sơ** để cập nhật trạng thái và phản hồi.")

# ---------- Library ----------
elif page == "Thư viện học liệu":
    st.subheader("📚 Thư viện học liệu")
    search = st.text_input("Tìm theo tên, chủ đề hoặc mô tả", key="resource_search")
    category_filter = st.selectbox("Lọc theo chủ đề", ["Tất cả", "Nghiên cứu khoa học", "Công nghệ", "Kỹ năng học tập", "Lý luận chính trị", "Khác"])
    with SessionLocal() as db:
        query = select(Resource).order_by(desc(Resource.created_at))
        if current_user.role == "student":
            query = query.where(Resource.status == "Đã duyệt")
        if category_filter != "Tất cả":
            query = query.where(Resource.category == category_filter)
        resources = list(db.scalars(query))
    resources = [r for r in resources if not search or search.lower() in f"{r.title} {r.category} {r.description}".lower()]
    if not resources:
        st.info("Chưa có học liệu phù hợp. Người phụ trách có thể bổ sung tài liệu đã được phép chia sẻ.")
    for r in resources:
        with st.container(border=True):
            st.markdown(f"**{r.title}**")
            st.caption(f"Chủ đề: {r.category} · Trạng thái: {r.status} · Mã học liệu: {r.id}")
            st.write(r.description or "Chưa có mô tả.")
            if r.source_url:
                st.markdown(f"[Mở nguồn tài liệu]({r.source_url})")
            if current_user.role in ("teacher", "admin"):
                x, y = st.columns([2, 1])
                with x:
                    new_status = st.selectbox("Trạng thái", ["Chờ duyệt", "Đã duyệt", "Ẩn"], index=["Chờ duyệt", "Đã duyệt", "Ẩn"].index(r.status) if r.status in ["Chờ duyệt", "Đã duyệt", "Ẩn"] else 0, key=f"res_status_{r.id}")
                with y:
                    if st.button("Lưu trạng thái", key=f"res_save_{r.id}"):
                        with SessionLocal() as db:
                            obj = db.get(Resource, r.id)
                            obj.status = new_status
                            log_activity(db, current_user.username, f"Cập nhật trạng thái học liệu #{r.id}: {new_status}")
                            db.commit()
                        st.success("Đã cập nhật.")
                        st.rerun()
    if current_user.role in ("teacher", "admin"):
        st.divider()
        st.markdown("### Thêm học liệu")
        with st.form("add_resource", clear_on_submit=True):
            title = st.text_input("Tên học liệu *")
            category = st.selectbox("Chủ đề", ["Nghiên cứu khoa học", "Công nghệ", "Kỹ năng học tập", "Lý luận chính trị", "Khác"])
            description = st.text_area("Mô tả")
            source_url = st.text_input("Đường dẫn nguồn (nếu có)", placeholder="https://...")
            status = st.selectbox("Trạng thái ban đầu", ["Chờ duyệt", "Đã duyệt"])
            save = st.form_submit_button("Thêm học liệu", type="primary")
        if save:
            if not title.strip():
                st.error("Vui lòng nhập tên học liệu.")
            elif source_url and not source_url.startswith(("https://", "http://")):
                st.error("Đường dẫn cần bắt đầu bằng http:// hoặc https://")
            else:
                with SessionLocal() as db:
                    db.add(Resource(title=title.strip(), category=category, description=description.strip(), source_url=source_url.strip(), status=status, created_by=current_user.id))
                    log_activity(db, current_user.username, f"Thêm học liệu: {title.strip()}")
                    db.commit()
                st.success("Đã thêm học liệu.")
                st.rerun()

# ---------- Research projects ----------
elif page == "Nghiên cứu khoa học":
    st.subheader("🔬 Quản lý nghiên cứu khoa học")
    with st.form("new_project", clear_on_submit=True):
        title = st.text_input("Tên đề tài *")
        objective = st.text_area("Mục tiêu và nội dung nghiên cứu *", height=100)
        members = st.text_input("Thành viên / nhóm nghiên cứu")
        due_date = st.date_input("Ngày dự kiến hoàn thành", value=date.today())
        submit_project = st.form_submit_button("Tạo hồ sơ đề tài", type="primary")
    if submit_project:
        if not title.strip() or not objective.strip():
            st.error("Cần nhập tên đề tài và mục tiêu nghiên cứu.")
        else:
            with SessionLocal() as db:
                obj = Project(title=title.strip(), objective=objective.strip(), members=members.strip(), progress=0, status="Chờ xem xét", due_date=due_date, owner_id=current_user.id)
                db.add(obj)
                log_activity(db, current_user.username, f"Tạo hồ sơ đề tài: {title.strip()}")
                db.commit()
            st.success("Đã gửi hồ sơ đề tài. Người phụ trách có thể xem xét trong mục Xử lý hồ sơ.")
            st.rerun()
    st.divider()
    st.markdown("### Danh sách đề tài")
    with SessionLocal() as db:
        q = select(Project).order_by(desc(Project.created_at))
        if current_user.role == "student":
            q = q.where(Project.owner_id == current_user.id)
        projects = list(db.scalars(q))
        owners = {u.id: u.full_name for u in db.scalars(select(User))}
    if not projects:
        st.info("Bạn chưa có đề tài nào. Hãy tạo hồ sơ ở biểu mẫu phía trên.")
    for p in projects:
        with st.container(border=True):
            st.markdown(f"**{p.title}**")
            st.caption(f"Mã đề tài: {p.id} · Người tạo: {owners.get(p.owner_id, 'Không xác định')} · Hạn dự kiến: {p.due_date or 'Chưa đặt'}")
            st.write(p.objective)
            st.progress(max(0, min(100, p.progress)) / 100, text=f"Tiến độ: {p.progress}%")
            st.write(f"**Trạng thái:** {p.status}")
            if p.feedback:
                st.info(f"**Phản hồi:** {p.feedback}")
            if current_user.role == "student" and p.owner_id == current_user.id:
                with st.form(f"update_project_{p.id}"):
                    new_progress = st.slider("Cập nhật tiến độ (%)", 0, 100, p.progress)
                    progress_note = st.text_area("Ghi chú tiến độ", key=f"project_note_{p.id}")
                    update = st.form_submit_button("Lưu cập nhật tiến độ")
                if update:
                    with SessionLocal() as db:
                        obj = db.get(Project, p.id)
                        obj.progress = new_progress
                        if progress_note.strip():
                            obj.objective = obj.objective + "\n\nCập nhật tiến độ: " + progress_note.strip()
                        if obj.status == "Chờ xem xét":
                            obj.status = "Đang thực hiện"
                        log_activity(db, current_user.username, f"Cập nhật tiến độ đề tài #{p.id}: {new_progress}%")
                        db.commit()
                    st.success("Đã lưu tiến độ.")
                    st.rerun()

# ---------- Ideas ----------
elif page == "Tiếp nhận sáng kiến":
    st.subheader("💡 Gửi và theo dõi sáng kiến")
    with st.form("new_idea", clear_on_submit=True):
        title = st.text_input("Tên sáng kiến *")
        problem = st.text_area("Vấn đề cần giải quyết *", height=90)
        solution = st.text_area("Nội dung giải pháp đề xuất *", height=110)
        benefit = st.text_area("Lợi ích dự kiến *", height=80)
        submit_idea = st.form_submit_button("Gửi sáng kiến", type="primary")
    if submit_idea:
        if not all([title.strip(), problem.strip(), solution.strip(), benefit.strip()]):
            st.error("Vui lòng điền đầy đủ tên, vấn đề, giải pháp và lợi ích dự kiến.")
        else:
            with SessionLocal() as db:
                db.add(Idea(title=title.strip(), problem=problem.strip(), solution=solution.strip(), expected_benefit=benefit.strip(), status="Mới tiếp nhận", proposer_id=current_user.id))
                log_activity(db, current_user.username, f"Gửi sáng kiến: {title.strip()}")
                db.commit()
            st.success("Đã tiếp nhận sáng kiến. Bạn có thể theo dõi trạng thái bên dưới.")
            st.rerun()
    st.divider()
    st.markdown("### Sáng kiến đã gửi")
    with SessionLocal() as db:
        q = select(Idea).order_by(desc(Idea.created_at))
        if current_user.role == "student":
            q = q.where(Idea.proposer_id == current_user.id)
        ideas = list(db.scalars(q))
        proposer_names = {u.id: u.full_name for u in db.scalars(select(User))}
    if not ideas:
        st.info("Chưa có sáng kiến. Hãy gửi ý tưởng đầu tiên bằng biểu mẫu phía trên.")
    for idea in ideas:
        with st.container(border=True):
            st.markdown(f"**{idea.title}**")
            st.caption(f"Mã sáng kiến: {idea.id} · Người đề xuất: {proposer_names.get(idea.proposer_id, 'Không xác định')} · Ngày gửi: {idea.created_at:%d/%m/%Y}")
            st.write(f"**Vấn đề:** {idea.problem}")
            st.write(f"**Giải pháp:** {idea.solution}")
            st.write(f"**Lợi ích dự kiến:** {idea.expected_benefit}")
            st.write(f"**Trạng thái:** {idea.status}")
            if idea.feedback:
                st.info(f"**Phản hồi của người phụ trách:** {idea.feedback}")

# ---------- Staff review queue ----------
elif page == "Xử lý hồ sơ":
    st.subheader("🗂️ Xử lý đề tài và sáng kiến")
    tab_projects, tab_ideas, tab_resources = st.tabs(["Đề tài nghiên cứu", "Sáng kiến", "Duyệt học liệu"])
    with tab_projects:
        with SessionLocal() as db:
            projects = list(db.scalars(select(Project).order_by(desc(Project.created_at))))
            users = {u.id: u.full_name for u in db.scalars(select(User))}
        if not projects:
            st.info("Chưa có đề tài.")
        for p in projects:
            with st.expander(f"Đề tài #{p.id}: {p.title} — {p.status}"):
                st.write(f"**Người tạo:** {users.get(p.owner_id, 'Không rõ')}")
                st.write(f"**Mục tiêu:** {p.objective}")
                with st.form(f"review_project_{p.id}"):
                    status = st.selectbox("Trạng thái", PROJECT_STATUSES, index=PROJECT_STATUSES.index(p.status) if p.status in PROJECT_STATUSES else 0, key=f"pstatus_{p.id}")
                    progress = st.slider("Tiến độ (%)", 0, 100, p.progress, key=f"pprogress_{p.id}")
                    feedback = st.text_area("Phản hồi cho nhóm nghiên cứu", value=p.feedback, key=f"pfeedback_{p.id}")
                    save = st.form_submit_button("Lưu xử lý đề tài")
                if save:
                    with SessionLocal() as db:
                        obj = db.get(Project, p.id)
                        obj.status, obj.progress, obj.feedback = status, progress, feedback.strip()
                        log_activity(db, current_user.username, f"Xử lý đề tài #{p.id}: {status}")
                        db.commit()
                    st.success("Đã lưu xử lý đề tài.")
                    st.rerun()
    with tab_ideas:
        with SessionLocal() as db:
            ideas = list(db.scalars(select(Idea).order_by(desc(Idea.created_at))))
            users = {u.id: u.full_name for u in db.scalars(select(User))}
        if not ideas:
            st.info("Chưa có sáng kiến.")
        for idea in ideas:
            with st.expander(f"Sáng kiến #{idea.id}: {idea.title} — {idea.status}"):
                st.write(f"**Người đề xuất:** {users.get(idea.proposer_id, 'Không rõ')}")
                st.write(f"**Vấn đề:** {idea.problem}")
                st.write(f"**Giải pháp:** {idea.solution}")
                st.write(f"**Lợi ích dự kiến:** {idea.expected_benefit}")
                with st.form(f"review_idea_{idea.id}"):
                    status = st.selectbox("Trạng thái xử lý", IDEA_STATUSES, index=IDEA_STATUSES.index(idea.status) if idea.status in IDEA_STATUSES else 0, key=f"istatus_{idea.id}")
                    feedback = st.text_area("Ý kiến phản hồi", value=idea.feedback, key=f"ifeedback_{idea.id}")
                    save = st.form_submit_button("Lưu phản hồi")
                if save:
                    with SessionLocal() as db:
                        obj = db.get(Idea, idea.id)
                        obj.status, obj.feedback = status, feedback.strip()
                        log_activity(db, current_user.username, f"Xử lý sáng kiến #{idea.id}: {status}")
                        db.commit()
                    st.success("Đã lưu phản hồi sáng kiến.")
                    st.rerun()
    with tab_resources:
        with SessionLocal() as db:
            resources = list(db.scalars(select(Resource).order_by(desc(Resource.created_at))))
        for r in resources:
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f"**{r.title}**")
            c2.write(f"Trạng thái: {r.status}")
            with c3:
                target = "Đã duyệt" if r.status != "Đã duyệt" else "Chờ duyệt"
                if st.button(target, key=f"quick_resource_{r.id}"):
                    with SessionLocal() as db:
                        obj = db.get(Resource, r.id)
                        obj.status = target
                        log_activity(db, current_user.username, f"Đổi trạng thái học liệu #{r.id}: {target}")
                        db.commit()
                    st.rerun()

# ---------- User administration ----------
elif page == "Quản lý tài khoản":
    st.subheader("👥 Quản lý tài khoản")
    st.warning("Chỉ tạo tài khoản thử nghiệm. Không dùng thông tin cá nhân hoặc mật khẩu đang sử dụng ở dịch vụ khác.")
    with st.form("create_user", clear_on_submit=True):
        username = st.text_input("Tên đăng nhập (không dấu, không khoảng trắng)")
        full_name = st.text_input("Tên hiển thị")
        role = st.selectbox("Vai trò", ["student", "teacher", "admin"], format_func=lambda x: ROLE_LABEL[x])
        password = st.text_input("Mật khẩu tạm thời (tối thiểu 10 ký tự)", type="password")
        confirm = st.text_input("Nhập lại mật khẩu", type="password")
        create = st.form_submit_button("Tạo tài khoản", type="primary")
    if create:
        normalized = username.strip().lower()
        if not normalized or any(ch.isspace() for ch in normalized) or not normalized.replace("_", "").replace("-", "").isalnum():
            st.error("Tên đăng nhập chỉ nên gồm chữ, số, dấu gạch dưới hoặc gạch ngang.")
        elif not full_name.strip():
            st.error("Vui lòng nhập tên hiển thị.")
        elif len(password) < 10:
            st.error("Mật khẩu phải có ít nhất 10 ký tự.")
        elif password != confirm:
            st.error("Hai mật khẩu không trùng nhau.")
        else:
            with SessionLocal() as db:
                if db.scalar(select(User).where(User.username == normalized)):
                    st.error("Tên đăng nhập đã tồn tại.")
                else:
                    db.add(User(username=normalized, full_name=full_name.strip(), role=role, password_hash=hash_password(password)))
                    log_activity(db, current_user.username, f"Tạo tài khoản {normalized} với vai trò {ROLE_LABEL[role]}")
                    db.commit()
                    st.success("Đã tạo tài khoản.")
                    st.rerun()
    st.divider()
    with SessionLocal() as db:
        users = list(db.scalars(select(User).order_by(User.username)))
    for u in users:
        with st.container(border=True):
            a, b, c, d = st.columns([2, 3, 2, 2])
            a.write(f"**{u.username}**")
            b.write(u.full_name)
            c.write(ROLE_LABEL.get(u.role, u.role))
            d.write("Đang hoạt động" if u.active else "Đã khóa")
            if u.id != current_user.id:
                if st.button("Khóa tài khoản" if u.active else "Mở khóa", key=f"toggle_user_{u.id}"):
                    with SessionLocal() as db:
                        obj = db.get(User, u.id)
                        obj.active = 0 if obj.active else 1
                        log_activity(db, current_user.username, f"Thay đổi trạng thái tài khoản {u.username}")
                        db.commit()
                    st.rerun()

# ---------- Activity log ----------
elif page == "Nhật ký hoạt động":
    st.subheader("🧾 Nhật ký hoạt động")
    st.caption("Nhật ký phục vụ kiểm thử nguyên mẫu, chưa thay thế hệ thống giám sát và kiểm toán an toàn thông tin chuyên dụng.")
    with SessionLocal() as db:
        logs = list(db.scalars(select(Activity).order_by(desc(Activity.created_at)).limit(200)))
    if logs:
        st.dataframe([{"Thời gian": x.created_at.strftime("%d/%m/%Y %H:%M:%S"), "Tài khoản": x.username, "Hoạt động": x.action} for x in logs], use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có hoạt động được ghi nhận.")

st.divider()
st.caption("ANND Digital Hub là nguyên mẫu độc lập phục vụ học tập và dự thi. Không phải hệ thống chính thức của Học viện An ninh nhân dân. Chỉ sử dụng dữ liệu giả lập hoặc dữ liệu được phép công khai.")
