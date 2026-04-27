import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# استيراد الإعدادات واللوجر
from ..Config import Config
from ..core.logger import logging

LOGS = logging.getLogger(__name__)

def start() -> scoped_session:
    # 1. البحث عن رابط قاعدة البيانات في كل المصادر الممكنة
    db_uri = Config.DB_URI or os.environ.get("DB_URI") or os.environ.get("DATABASE_URL")

    # 2. التحقق من وجود الرابط قبل البدء بالعمليات لتجنب خطأ NoneType
    if not db_uri:
        LOGS.error("DB_URI is not configured. Using temporary SQLite database.")
        # حل احتياطي لتشغيل البوت حتى لو نسيت الرابط
        db_uri = "sqlite:///temp.db"

    # 3. تعديل الرابط ليتوافق مع SQLAlchemy الحديثة (postgresql:// بدلاً من postgres://)
    database_url = (
        db_uri.replace("postgres:", "postgresql:")
        if db_uri and "postgres://" in db_uri
        else db_uri
    )
    
    # 4. إنشاء محرك قاعدة البيانات والاتصال
    engine = create_engine(database_url)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))

# تشغيل الجلسة ومعالجة الأخطاء
try:
    BASE = declarative_base()
    SESSION = start()
except Exception as e:
    LOGS.error(f"حدث خطأ أثناء تشغيل قاعدة البيانات: {str(e)}")
    # إنشاء قاعدة بيانات وهمية في الذاكرة كحل أخير لمنع انهيار البوت بالكامل
    engine = create_engine("sqlite:///:memory:")
    SESSION = scoped_session(sessionmaker(bind=engine, autoflush=False))
