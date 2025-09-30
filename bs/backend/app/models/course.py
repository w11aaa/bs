from app import db
from datetime import datetime

# 课程分类模型
class CourseCategory(db.Model):
    __tablename__ = 'course_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联课程
    courses = db.relationship('Course', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<CourseCategory {self.name}>'

# 课程模型
class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    credits = db.Column(db.Float, nullable=True)
    semester = db.Column(db.String(20), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    day_of_week = db.Column(db.String(20), nullable=True)  # 星期几上课
    location = db.Column(db.String(100), nullable=True)
    
    # 外键关联
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('course_categories.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联考勤记录
    attendances = db.relationship('Attendance', backref='course', lazy=True)
    
    # 关联选课记录
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    
    def __repr__(self):
        return f'<Course {self.course_code}: {self.name}>'

# 选课记录模型
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 确保每个学生在每门课程中只有一条记录
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='_student_course_uc'),
    )
    
    def __repr__(self):
        return f'<Enrollment Student {self.student_id} in Course {self.course_id}>'