from app.models.user import User
from app import db

class Teacher(User):
    __tablename__ = 'teachers'
    
    # 教师特有字段
    teacher_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(50), nullable=True)  # 职称
    department = db.Column(db.String(100), nullable=True)  # 所属院系
    
    # 关联教授的课程
    courses = db.relationship('Course', backref='teacher', lazy=True)
    
    def __init__(self, *args, **kwargs):
        super(Teacher, self).__init__(*args, **kwargs)
        self.role = 'teacher'  # 设置角色为教师
    
    def __repr__(self):
        return f'<Teacher {self.teacher_id}: {self.name}>'