from app import create_app, db
from app.models import Admin, CourseCategory
from werkzeug.security import generate_password_hash
import os

# 创建Flask应用
app = create_app(config_name='development')

with app.app_context():
    # 创建数据库表
    db.create_all()
    
    # 检查是否已存在管理员账号
    admin_exists = Admin.query.first()
    if not admin_exists:
        # 创建默认管理员
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            admin_id='ADM001',
            name='系统管理员',
            email='admin@example.com'
        )
        db.session.add(admin)
        print('默认管理员创建成功！用户名: admin, 密码: admin123')
    
    # 创建默认课程分类
    categories = ['计算机科学', '电子工程', '数学', '物理', '化学', '生物']
    for category_name in categories:
        category = CourseCategory.query.filter_by(name=category_name).first()
        if not category:
            new_category = CourseCategory(name=category_name)
            db.session.add(new_category)
    
    # 提交数据库更改
    db.session.commit()
    
    print('数据库初始化完成！')
    print('\n请记住：')
    print('1. 请在首次登录后修改管理员密码')
    print('2. 通过管理员账号创建教师账户')
    print('3. 学生可以自行注册')