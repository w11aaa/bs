from app.config.default import Config
import os

class DevelopmentConfig(Config):
    # 开发环境配置
    DEBUG = True
    
    # 数据库配置 - 开发环境使用相同的数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost:3306/attendance_system_dev'
    
    # 开发环境下的调试工具栏
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False