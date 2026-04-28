import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# استيراد الإعدادات واللوجر
from ..Config import Config
from ..core.logger import logging

LOGS = logging.getLogger(__name__)

def start() -> scoped_session:
    # البيانات التي استخرجناها من قاعدة بياناتك (wild-wind-1156)
    db_credentials = "postgres://postgres:1BQPjBsXjmYPwqV@wild-wind-1156.flycast:5432"

    # 1. محاولة جلب الرابط من ملف الكونفنج أو المتغيرات، وإذا لم يوجد نستخدم الرابط الثابت أعلاه
    db_uri = Config.DB_URI or os.environ.get("DB_URI") or db_credentials

    # 2. التحقق من الرابط وتعديل البروتوكول فقط دون المساس باسم المستخدم
    # استبدال أول postgres:// فقط بـ postgresql://
    if db_uri and db_uri.startswith("postgres://"):
        database_url = db_uri.replace("postgres://", "postgresql://", 1)
    else:
        database_url = db_uri
    
    # 3. إنشاء محرك قاعدة البيانات والاتصال
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
    # إنشاء قاعدة بيانات في الذاكرة كحل أخير لمنع الانهيار
    engine = create_engine("sqlite:///:memory:")
    SESSION = scoped_session(sessionmaker(bind=engine, autoflush=False))
