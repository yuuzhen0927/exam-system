from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from database import Base


# ==================== 用户 ====================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    fullname = Column(String(100), nullable=False, default="")
    avatar = Column(String(500), default="")
    role = Column(String(20), nullable=False, default="student")  # admin / teacher / student
    is_active = Column(Boolean, default=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    exam_results = relationship("ExamResult", back_populates="user")
    retake_applications = relationship("RetakeApplication", back_populates="user", cascade="all, delete-orphan")
    practice_records = relationship("PracticeRecord", back_populates="user")
    wrong_answers = relationship("WrongAnswer", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    notes = relationship("Note", back_populates="user")
    feedbacks = relationship("QuestionFeedback", back_populates="user")
    certificates = relationship("UserCertificate", back_populates="user")


# ==================== 科目 & 章节 ====================

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chapters = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan", order_by="Chapter.sort_order")
    questions = relationship("Question", back_populates="subject", cascade="all, delete-orphan")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subject = relationship("Subject", back_populates="chapters")
    questions = relationship("Question", back_populates="chapter")


# ==================== 题库 ====================

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True, index=True)
    specialty = Column(String(100), default="")           # 专项分类
    type = Column(String(20), nullable=False, default="single")  # single / multi / truefalse / composite
    difficulty = Column(Integer, default=1)               # 1-5
    content = Column(Text, nullable=False)                # 题干
    options = Column(Text, nullable=False, default="[]")  # JSON: [{label, text}]
    answer = Column(Text, nullable=False)                 # 正确答案 JSON
    explanation = Column(Text, default="")                # 解析
    reference = Column(Text, default="")                  # 规范引用
    images = Column(Text, default="[]")                   # JSON: [url1, url2] 题目配图
    tags = Column(Text, default="[]")                     # JSON: ["高频考点","易错题","公式题"]
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    subject = relationship("Subject", back_populates="questions")
    chapter = relationship("Chapter", back_populates="questions")
    versions = relationship("QuestionVersion", back_populates="question", cascade="all, delete-orphan")


class QuestionVersion(Base):
    """题目版本历史"""
    __tablename__ = "question_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    options = Column(Text, nullable=False, default="[]")
    answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    changed_by = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    question = relationship("Question", back_populates="versions")


# ==================== 试卷 & 组卷 ====================

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    mode = Column(String(20), nullable=False, default="mock")       # mock / formal
    duration_minutes = Column(Integer, nullable=False, default=60)
    total_score = Column(Integer, nullable=False, default=100)
    pass_score = Column(Integer, nullable=False, default=60)
    question_ids = Column(Text, nullable=False, default="[]")       # JSON array of question IDs
    is_published = Column(Boolean, default=False)
    shuffle_questions = Column(Boolean, default=True)               # 随机抽题顺序
    shuffle_options = Column(Boolean, default=True)                 # 选项乱序
    max_tab_switches = Column(Integer, default=3)                   # 最大切屏次数
    start_time = Column(DateTime, nullable=True)
    invite_code = Column(String(20), nullable=True, default=None)          # 考试邀请码
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    retake_applications = relationship("RetakeApplication", back_populates="exam", cascade="all, delete-orphan")
    results = relationship("ExamResult", back_populates="exam", cascade="all, delete-orphan")
    template = relationship("ExamTemplate", back_populates="exam", uselist=False, cascade="all, delete-orphan")


class ExamTemplate(Base):
    """组卷规则模板"""
    __tablename__ = "exam_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, unique=True)
    subject_ids = Column(Text, default="[]")          # JSON: [subject_id]
    chapter_ids = Column(Text, default="[]")          # JSON: [chapter_id]
    specialties = Column(Text, default="[]")          # JSON: ["专项名"]
    type_config = Column(Text, default="{}")          # JSON: {"single":10,"multi":5,"truefalse":5,"composite":2}
    difficulty_range = Column(Text, default="[1,5]")  # JSON: [min, max]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    exam = relationship("Exam", back_populates="template")


# ==================== 考试结果 ====================

class ExamResult(Base):
    __tablename__ = "exam_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    answers = Column(Text, nullable=False, default="{}")     # {question_id: user_answer}
    auto_score = Column(Float, nullable=False, default=0)    # 自动评分
    manual_score = Column(Float, nullable=True)              # 人工评分（综合题）
    total_score = Column(Integer, nullable=False, default=100)
    passed = Column(Boolean, default=False)
    tab_switches = Column(Integer, default=0)                # 切屏次数
    is_cheating = Column(Boolean, default=False)             # 是否作弊
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    exam = relationship("Exam", back_populates="results")
    user = relationship("User", back_populates="exam_results")


# ==================== 练习记录 ====================

class PracticeRecord(Base):
    __tablename__ = "practice_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = Column(String(30), nullable=False, default="random")  # random / memorize / specialty / chapter
    subject_id = Column(Integer, nullable=True)
    chapter_id = Column(Integer, nullable=True)
    specialty = Column(String(100), default="")
    question_type = Column(String(20), default="")
    total_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    answers = Column(Text, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="practice_records")


# ==================== 错题本 ====================

class WrongAnswer(Base):
    __tablename__ = "wrong_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    wrong_count = Column(Integer, default=1)               # 错误次数
    is_mastered = Column(Boolean, default=False)           # 是否已掌握
    last_wrong_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="wrong_answers")
    question = relationship("Question")


# ==================== 收藏 ====================

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    tags = Column(Text, default="[]")                     # JSON: ["易错","重要"]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="favorites")
    question = relationship("Question")


# ==================== 笔记 ====================

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(200), default="")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="notes")
    question = relationship("Question")


# ==================== 公告 ====================

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    created_by = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==================== 证书 ====================

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    template_image = Column(String(500), default="")       # 证书模板图
    issue_rule = Column(Text, default="{}")                # 颁发规则 JSON
    cert_type = Column(String(20), default="exam")  # exam / practice
    chapter_id = Column(Integer, nullable=True)       # 练习证书关联章节
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_certificates = relationship("UserCertificate", back_populates="certificate", cascade="all, delete-orphan")


class UserCertificate(Base):
    __tablename__ = "user_certificates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_result_id = Column(Integer, nullable=True)        # 关联的考试结果
    certificate_no = Column(String(100), unique=True)      # 证书编号
    is_revoked = Column(Boolean, default=False)
    auto_issued = Column(Boolean, default=False)  # 是否自动颁发
    issue_reason = Column(String(50), default='')  # exam_pass / practice_pass / manual / apply
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)

    certificate = relationship("Certificate", back_populates="user_certificates")
    user = relationship("User", back_populates="certificates")


# ==================== 题目反馈 ====================

class QuestionFeedback(Base):
    __tablename__ = "question_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), nullable=False, default="doubt")  # doubt / error_report
    content = Column(Text, nullable=False)
    images = Column(Text, default="[]")                          # JSON: [url] 截图
    status = Column(String(20), default="pending")               # pending / accepted / rejected
    reply = Column(Text, default="")
    replied_by = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="feedbacks")
    question = relationship("Question")


# ==================== 视频课程 ====================

class VideoCourse(Base):
    __tablename__ = "video_courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    video_url = Column(String(500), nullable=False)
    cover_url = Column(String(500), default="")
    duration_seconds = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==================== 异常报告 ====================

class AbnormalReport(Base):
    __tablename__ = "abnormal_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_result_id = Column(Integer, ForeignKey("exam_results.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(String(100), nullable=False)       # tab_switch / time_anomaly / ip_change
    detail = Column(Text, default="")
    is_judged = Column(Boolean, default=False)
    judgment = Column(String(20), default="")
    judged_by = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    exam_result = relationship("ExamResult")
    user = relationship("User")


# ==================== 学习资料 ====================

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), default="")
    file_size = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_by = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==================== 操作审计日志 ====================

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String(100), default="")
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=True)
    detail = Column(Text, default="")
    ip_address = Column(String(50), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==================== 视频播放进度 ====================

class VideoProgress(Base):
    __tablename__ = "video_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("video_courses.id", ondelete="CASCADE"), nullable=False, index=True)
    current_time = Column(Integer, default=0)
    duration = Column(Integer, default=0)
    is_finished = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RetakeApplication(Base):
    __tablename__ = "retake_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(Text, default="")
    status = Column(String(20), default="pending")  # pending / approved / rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    exam = relationship("Exam", back_populates="retake_applications")
    user = relationship("User", back_populates="retake_applications")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), default="")
    is_manager = Column(Boolean, default=False)  # can access admin pages
    is_system = Column(Boolean, default=False)   # cannot delete
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==================== 通知 ====================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), default="system")  # announcement / exam / certificate / feedback / system
    title = Column(String(200), nullable=False)
    content = Column(Text, default="")
    link = Column(String(500), default="")  # 跳转路径
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
