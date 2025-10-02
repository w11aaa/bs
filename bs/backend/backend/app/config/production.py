from app.config.default import Config
import os

class ProductionConfig(Config):
    # 生产环境配置
    DEBUG = False
    TESTING = False
    
    # 数据库配置 - 生产环境
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost:3306/attendance_system'
    
    # 生产环境下的密钥应从环境变量获取
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY