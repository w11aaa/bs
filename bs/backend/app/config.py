import os
from datetime import timedelta


class Config:
    """基础配置类"""
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # 数据库通用配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 登录管理配置
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 允许的图片扩展名
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:123456@127.0.0.1:3306/attendance_system_dev'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql+pymysql://root:123456@127.0.0.1:3306/attendance_system_test'


class ProductionConfig(Config):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@127.0.0.1:3306/attendance_system'


# 配置映射，用于根据环境变量选择配置类
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}