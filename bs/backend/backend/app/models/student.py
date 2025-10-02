from app.models.user import User
from app import db
from datetime import datetime

class Student(User):
    __tablename__ = 'students'
    
    # 学生特有字段
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    major = db.Column(db.String(100), nullable=True)
    class_name = db.Column(db.String(50), nullable=True)
    face_image_path = db.Column(db.String(255), nullable=True)  # 存储人脸图片路径
    face_encoding = db.Column(db.LargeBinary, nullable=True)  # 存储人脸特征编码
    
    # 关联考勤记录
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    
    # 关联选课记录
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    
    def __init__(self, *args, **kwargs):
        super(Student, self).__init__(*args, **kwargs)
        self.role = 'student'  # 设置角色为学生
    
    def __repr__(self):
        return f'<Student {self.student_id}: {self.name}>'