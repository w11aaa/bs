import os
import secrets

class Config:
    # 基本配置
    SECRET_KEY = secrets.token_hex(16)  # 生成随机密钥
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost:3306/attendance_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 人脸识别配置
    FACE_RECOGNITION_TOLERANCE = 0.6
    
    # 考勤配置
    ATTENDANCE_LATE_MINUTES = 15  # 迟到时间阈值（分钟）