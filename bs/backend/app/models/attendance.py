from app import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    # 外键关联
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    # 考勤相关字段
    attendance_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='absent')  # present, late, absent
    
    # 人脸识别相关
    face_match_score = db.Column(db.Float, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)  # 存储考勤时的截图
    
    # 备注信息
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 确保每个学生每天在每门课程中只有一条考勤记录
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', 'attendance_date', name='_student_course_date_uc'),
    )
    
    def __repr__(self):
        return f'<Attendance Student {self.student_id} in Course {self.course_id} on {self.attendance_date}>'