from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
import os

# 初始化数据库实例
db = SQLAlchemy()
# 初始化数据库迁移工具
migrate = Migrate()
# 初始化登录管理器
login_manager = LoginManager()

# 创建Flask应用实例
def create_app(config_name=None):
    app = Flask(__name__)
    
    # 配置CORS，允许跨域请求，支持凭证
    CORS(app, origins='*', supports_credentials=True)
    
    # 加载配置
    from app.config import config
    app.config.from_object(config.get(config_name, config['default']))
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.teacher import teacher_bp
    from app.routes.course import course_bp
    from app.routes.attendance import attendance_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(course_bp, url_prefix='/course')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # 创建数据库表（仅在开发环境）
    with app.app_context():
        db.create_all()
    
    return app