"""
生成样例数据并存入数据库
"""
import os
import sys
import random
import datetime
from werkzeug.security import generate_password_hash
from faker import Faker
import sqlite3

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入应用程序上下文
from backend.app import create_app
from backend.app.models.user import User
from backend.app.models.student import Student
from backend.app.models.teacher import Teacher
from backend.app.models.admin import Admin
from backend.app.models.course import Course, CourseCategory, StudentCourse
from backend.app.models.attendance import Attendance
from backend.app.extensions import db

# 创建应用程序实例
app = create_app()

# 初始化Faker
fake = Faker('zh_CN')

def generate_users(num_students=50, num_teachers=10, num_admins=3):
    """生成用户数据"""
    print("正在生成用户数据...")
    
    # 生成学生数据
    students = []
    for i in range(num_students):
        student_id = f"S{2023000 + i}"
        name = fake.name()
        email = fake.email()
        gender = random.choice(['male', 'female'])
        age = random.randint(18, 25)
        major = random.choice(['计算机科学与技术', '软件工程', '人工智能', '数据科学', '网络工程', '信息安全'])
        class_name = f"{random.choice(['计科', '软工', '人工智能', '数据'])}{random.randint(1, 4)}班"
        
        # 创建学生用户
        user = User(
            username=student_id,
            password=generate_password_hash('123456'),
            email=email,
            role='student',
            is_active=True
        )
        db.session.add(user)
        db.session.flush()  # 获取user_id
        
        # 创建学生信息
        student = Student(
            user_id=user.id,
            student_id=student_id,
            name=name,
            gender=gender,
            age=age,
            major=major,
            class_name=class_name
        )
        db.session.add(student)
        students.append(student)
    
    # 生成教师数据
    teachers = []
    for i in range(num_teachers):
        teacher_id = f"T{1000 + i}"
        name = fake.name()
        email = fake.email()
        gender = random.choice(['male', 'female'])
        age = random.randint(30, 60)
        title = random.choice(['教授', '副教授', '讲师', '助教'])
        department = random.choice(['计算机学院', '软件学院', '信息学院', '数学学院'])
        research_area = random.choice(['人工智能', '数据挖掘', '计算机视觉', '自然语言处理', '软件工程', '网络安全'])
        
        # 创建教师用户
        user = User(
            username=teacher_id,
            password=generate_password_hash('123456'),
            email=email,
            role='teacher',
            is_active=True
        )
        db.session.add(user)
        db.session.flush()  # 获取user_id
        
        # 创建教师信息
        teacher = Teacher(
            user_id=user.id,
            teacher_id=teacher_id,
            name=name,
            gender=gender,
            age=age,
            title=title,
            department=department,
            research_area=research_area
        )
        db.session.add(teacher)
        teachers.append(teacher)
    
    # 生成管理员数据
    for i in range(num_admins):
        admin_id = f"A{100 + i}"
        name = fake.name()
        email = fake.email()
        
        # 创建管理员用户
        user = User(
            username=admin_id,
            password=generate_password_hash('123456'),
            email=email,
            role='admin',
            is_active=True
        )
        db.session.add(user)
        db.session.flush()  # 获取user_id
        
        # 创建管理员信息
        admin = Admin(
            user_id=user.id,
            admin_id=admin_id,
            name=name
        )
        db.session.add(admin)
    
    # 提交事务
    db.session.commit()
    print(f"成功生成 {num_students} 名学生, {num_teachers} 名教师, {num_admins} 名管理员")
    
    return students, teachers

def generate_course_categories():
    """生成课程类别数据"""
    print("正在生成课程类别数据...")
    
    categories = [
        '计算机基础',
        '编程语言',
        '数据结构与算法',
        '数据库系统',
        '操作系统',
        '计算机网络',
        '软件工程',
        '人工智能',
        '机器学习',
        '深度学习',
        '计算机视觉',
        '自然语言处理',
        '数据挖掘',
        '云计算',
        '大数据',
        '网络安全',
        '区块链',
        '物联网',
        '移动开发',
        '前端开发',
        '后端开发',
        '全栈开发'
    ]
    
    category_objects = []
    for category_name in categories:
        category = CourseCategory(name=category_name)
        db.session.add(category)
        category_objects.append(category)
    
    db.session.commit()
    print(f"成功生成 {len(categories)} 个课程类别")
    
    return category_objects

def generate_courses(teachers, categories, num_courses=30):
    """生成课程数据"""
    print("正在生成课程数据...")
    
    courses = []
    course_codes = set()
    
    for i in range(num_courses):
        # 生成唯一的课程编号
        while True:
            course_code = f"C{random.randint(1000, 9999)}"
            if course_code not in course_codes:
                course_codes.add(course_code)
                break
        
        name = fake.sentence(nb_words=3)[:-1]  # 去掉句号
        teacher = random.choice(teachers)
        category = random.choice(categories)
        credits = random.choice([1, 2, 3, 4, 5])
        capacity = random.randint(30, 100)
        description = fake.paragraph(nb_sentences=3)
        
        # 随机生成开始和结束日期
        start_date = datetime.date.today() - datetime.timedelta(days=random.randint(0, 60))
        end_date = start_date + datetime.timedelta(days=random.randint(90, 180))
        
        # 确定课程状态
        today = datetime.date.today()
        if today < start_date:
            status = 'pending'
        elif today > end_date:
            status = 'ended'
        else:
            status = 'active'
        
        course = Course(
            course_code=course_code,
            name=name,
            teacher_id=teacher.id,
            category_id=category.id,
            credits=credits,
            capacity=capacity,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        db.session.add(course)
        courses.append(course)
    
    db.session.commit()
    print(f"成功生成 {num_courses} 门课程")
    
    return courses

def generate_student_courses(students, courses):
    """生成学生选课数据"""
    print("正在生成学生选课数据...")
    
    student_courses = []
    count = 0
    
    for student in students:
        # 每个学生随机选择2-5门课程
        num_courses = random.randint(2, 5)
        selected_courses = random.sample(courses, min(num_courses, len(courses)))
        
        for course in selected_courses:
            enroll_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))
            
            student_course = StudentCourse(
                student_id=student.id,
                course_id=course.id,
                enroll_date=enroll_date
            )
            db.session.add(student_course)
            student_courses.append(student_course)
            count += 1
    
    db.session.commit()
    print(f"成功生成 {count} 条学生选课记录")
    
    return student_courses

def generate_attendance_records(student_courses):
    """生成考勤记录数据"""
    print("正在生成考勤记录数据...")
    
    attendance_records = []
    count = 0
    
    # 获取当前日期
    today = datetime.date.today()
    
    for student_course in student_courses:
        # 为每个学生课程生成5-15条考勤记录
        num_records = random.randint(5, 15)
        
        for i in range(num_records):
            # 生成考勤日期，在过去30天内
            record_date = today - datetime.timedelta(days=random.randint(0, 30))
            record_time = datetime.time(
                hour=random.randint(8, 17),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            # 生成考勤状态，大部分为出席
            status_weights = {'present': 0.8, 'absent': 0.1, 'late': 0.08, 'leave': 0.02}
            status = random.choices(
                list(status_weights.keys()),
                weights=list(status_weights.values()),
                k=1
            )[0]
            
            # 根据状态生成备注
            note = ''
            if status == 'absent':
                note = random.choice(['未到', '无故缺席', ''])
            elif status == 'late':
                note = f"迟到{random.randint(5, 30)}分钟"
            elif status == 'leave':
                note = random.choice(['病假', '事假', '请假已批准'])
            
            attendance = Attendance(
                student_id=student_course.student_id,
                course_id=student_course.course_id,
                date=record_date,
                time=record_time,
                status=status,
                note=note
            )
            db.session.add(attendance)
            attendance_records.append(attendance)
            count += 1
    
    db.session.commit()
    print(f"成功生成 {count} 条考勤记录")
    
    return attendance_records

def main():
    """主函数"""
    with app.app_context():
        # 清空现有数据
        print("正在清空现有数据...")
        db.session.execute(db.text("PRAGMA foreign_keys = OFF"))
        
        # 清空表中的数据而不是删除表
        db.session.execute(db.text("DELETE FROM attendance"))
        db.session.execute(db.text("DELETE FROM student_courses"))
        db.session.execute(db.text("DELETE FROM courses"))
        db.session.execute(db.text("DELETE FROM course_categories"))
        db.session.execute(db.text("DELETE FROM students"))
        db.session.execute(db.text("DELETE FROM teachers"))
        db.session.execute(db.text("DELETE FROM admins"))
        db.session.execute(db.text("DELETE FROM users"))
        db.session.commit()
        
        print("已清空表数据，准备生成新数据...")
        
        # 生成样例数据
        students, teachers = generate_users(num_students=50, num_teachers=10, num_admins=3)
        categories = generate_course_categories()
        courses = generate_courses(teachers, categories, num_courses=30)
        student_courses = generate_student_courses(students, courses)
        attendance_records = generate_attendance_records(student_courses)
        
        print("样例数据生成完成！")
        print("默认密码: 123456")
        print("学生账号示例: S2023000")
        print("教师账号示例: T1000")
        print("管理员账号示例: A100")

if __name__ == "__main__":
    main()