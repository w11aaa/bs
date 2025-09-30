from app.models.user import User
from app import db

class Admin(User):
    __tablename__ = 'admins'
    
    # 管理员特有字段
    admin_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
    def __init__(self, *args, **kwargs):
        super(Admin, self).__init__(*args, **kwargs)
        self.role = 'admin'  # 设置角色为管理员
    
    def __repr__(self):
        return f'<Admin {self.admin_id}: {self.name}>'