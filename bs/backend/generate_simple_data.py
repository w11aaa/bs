"""
简化版样例数据生成脚本
"""
import os
import sys
import random
import datetime
import sqlite3
from werkzeug.security import generate_password_hash

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'attendance_system_dev.db')

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def clear_data():
    """清空现有数据"""
    print("正在清空现有数据...")
    
    # 关闭外键约束
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # 清空表数据
    tables = [
        "attendances",
        "enrollments",
        "courses",
        "course_categories",
        "students",
        "teachers",
        "admins"
    ]
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"已清空表 {table}")
        except sqlite3.Error as e:
            print(f"清空表 {table} 时出错: {e}")
    
    # 重置自增ID
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        except sqlite3.Error as e:
            print(f"重置表 {table} 的自增ID时出错: {e}")
    
    conn.commit()
    print("已清空所有表数据")

def generate_users():
    """生成用户数据"""
    print("正在生成用户数据...")
    
    # 生成管理员
    admin_data = [
        ('A100', '管理员100', generate_password_hash('123456'), 'admin1@example.com'),
        ('A101', '管理员101', generate_password_hash('123456'), 'admin2@example.com'),
        ('A102', '管理员102', generate_password_hash('123456'), 'admin3@example.com')
    ]
    
    for admin_id, name, password_hash, email in admin_data:
        try:
            # 直接插入管理员表
            cursor.execute(
                """INSERT INTO admins 
                   (admin_id, name, username, password_hash, email, created_at, updated_at, role) 
                   VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'), 'admin')""",
                (admin_id, name, admin_id, password_hash, email)
            )
        except sqlite3.Error as e:
            print(f"插入管理员 {admin_id} 时出错: {e}")
    
    # 生成教师
    for i in range(10):
        teacher_id = f"T{1000 + i}"
        email = f"teacher{i}@example.com"
        name = f"教师{i+1}"
        gender = random.choice(['male', 'female'])
        age = random.randint(30, 60)
        title = random.choice(['教授', '副教授', '讲师', '助教'])
        department = random.choice(['计算机学院', '软件学院', '信息学院', '数学学院'])
        
        try:
            # 直接插入教师表
            cursor.execute(
                """INSERT INTO teachers 
                   (teacher_id, name, username, password_hash, email, gender, age, title, 
                    department, created_at, updated_at, role) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), 'teacher')""",
                (teacher_id, name, teacher_id, generate_password_hash('123456'), email, 
                 gender, age, title, department)
            )
        except sqlite3.Error as e:
            print(f"插入教师 {teacher_id} 时出错: {e}")
    
    # 生成学生
    for i in range(50):
        student_id = f"S{2023000 + i}"
        email = f"student{i}@example.com"
        name = f"学生{i+1}"
        gender = random.choice(['male', 'female'])
        age = random.randint(18, 25)
        major = random.choice(['计算机科学与技术', '软件工程', '人工智能', '数据科学', '网络工程', '信息安全'])
        class_name = f"{random.choice(['计科', '软工', '人工智能', '数据'])}{random.randint(1, 4)}班"
        
        try:
            # 直接插入学生表
            cursor.execute(
                """INSERT INTO students 
                   (student_id, name, username, password_hash, email, gender, age, 
                    major, class_name, created_at, updated_at, role) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), 'student')""",
                (student_id, name, student_id, generate_password_hash('123456'), email, 
                 gender, age, major, class_name)
            )
        except sqlite3.Error as e:
            print(f"插入学生 {student_id} 时出错: {e}")
    
    conn.commit()
    print("用户数据生成完成")

def generate_course_categories():
    """生成课程分类数据"""
    print("正在生成课程分类数据...")
    
    categories = [
        '计算机基础', '编程语言', '数据结构与算法', '数据库系统', '操作系统',
        '计算机网络', '软件工程', '人工智能', '机器学习', '深度学习',
        '计算机视觉', '自然语言处理', '大数据技术', '云计算', '区块链',
        '网络安全', '移动开发', '前端开发', 'Web开发', '游戏开发',
        '嵌入式系统', '物联网'
    ]
    
    for category in categories:
        try:
            cursor.execute(
                "INSERT INTO course_categories (name, description, created_at) VALUES (?, ?, datetime('now'))",
                (category, f"{category}相关课程")
            )
        except sqlite3.Error as e:
            print(f"插入课程分类 {category} 时出错: {e}")
    
    conn.commit()
    print("课程分类数据生成完成")

def generate_courses():
    """生成课程数据"""
    print("正在生成课程数据...")
    
    # 获取所有课程分类ID
    cursor.execute("SELECT id FROM course_categories")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取所有教师ID
    cursor.execute("SELECT id FROM teachers")
    teacher_ids = [row[0] for row in cursor.fetchall()]
    
    if not category_ids or not teacher_ids:
        print("错误：没有课程分类或教师数据")
        return
    
    course_names = [
        'Python编程基础', 'Java程序设计', 'C++程序设计', '数据结构', '算法分析与设计',
        '数据库原理', 'MySQL实践', '操作系统原理', 'Linux系统管理', '计算机网络',
        '网络协议分析', '软件工程', '敏捷开发', '人工智能导论', '机器学习',
        '深度学习', '计算机视觉', '自然语言处理', '大数据技术', 'Hadoop与Spark',
        '云计算技术', 'Docker与Kubernetes', '网络安全', '密码学', '前端开发',
        'Vue.js实战', 'React开发', '移动应用开发', '微信小程序开发', 'Unity游戏开发'
    ]
    
    for i, course_name in enumerate(course_names):
        category_id = random.choice(category_ids)
        teacher_id = random.choice(teacher_ids)
        credits = random.randint(1, 4)
        semester = random.choice(['2023-2024-1', '2023-2024-2', '2024-2025-1'])
        year = random.choice([2023, 2024])
        course_code = f"C{2000+i}"
        description = f"{course_name}课程描述"
        
        # 随机生成上课时间
        days = ['周一', '周二', '周三', '周四', '周五']
        day_of_week = random.choice(days)
        start_hour = random.randint(8, 16)
        start_time = f"{start_hour:02d}:00:00"
        end_time = f"{start_hour+2:02d}:00:00"
        location = f"{random.choice(['主教学楼', '综合楼', '科技楼', '信息楼'])}{random.randint(1, 5)}-{random.randint(100, 500)}"
        
        try:
            cursor.execute(
                """INSERT INTO courses 
                   (course_code, name, description, credits, semester, year, 
                    start_time, end_time, day_of_week, location, teacher_id, category_id, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
                (course_code, course_name, description, credits, semester, year, 
                 start_time, end_time, day_of_week, location, teacher_id, category_id)
            )
        except sqlite3.Error as e:
            print(f"插入课程 {course_name} 时出错: {e}")
    
    conn.commit()
    print("课程数据生成完成")

def generate_enrollments():
    """生成学生选课数据"""
    print("正在生成学生选课数据...")
    
    # 获取所有学生ID
    cursor.execute("SELECT id FROM students")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取所有课程ID
    cursor.execute("SELECT id FROM courses")
    course_ids = [row[0] for row in cursor.fetchall()]
    
    if not student_ids or not course_ids:
        print("错误：没有学生或课程数据")
        return
    
    # 为每个学生随机选择2-5门课程
    for student_id in student_ids:
        # 随机选择2-5门不重复的课程
        num_courses = random.randint(2, min(5, len(course_ids)))
        selected_courses = random.sample(course_ids, num_courses)
        
        for course_id in selected_courses:
            try:
                cursor.execute(
                    """INSERT INTO enrollments 
                       (student_id, course_id, enrollment_date) 
                       VALUES (?, ?, datetime('now'))""",
                    (student_id, course_id)
                )
            except sqlite3.Error as e:
                print(f"插入选课记录 学生:{student_id} 课程:{course_id} 时出错: {e}")
    
    conn.commit()
    print("学生选课数据生成完成")

def generate_attendances():
    """生成考勤记录数据"""
    print("正在生成考勤记录数据...")
    
    # 获取所有选课记录
    cursor.execute("SELECT student_id, course_id FROM enrollments")
    enrollments = cursor.fetchall()
    
    if not enrollments:
        print("错误：没有选课记录")
        return
    
    # 获取当前日期
    today = datetime.date.today()
    
    # 为每个学生课程生成5-15条考勤记录
    for student_id, course_id in enrollments:
        num_records = random.randint(5, 15)
        
        for i in range(num_records):
            # 生成考勤日期，在过去30天内
            record_date = today - datetime.timedelta(days=random.randint(0, 30))
            
            # 生成考勤状态，大部分为出席
            status_weights = {'present': 0.8, 'absent': 0.1, 'late': 0.08, 'leave': 0.02}
            status = random.choices(
                list(status_weights.keys()),
                weights=list(status_weights.values()),
                k=1
            )[0]
            
            # 根据状态生成备注
            remark = ''
            if status == 'absent':
                remark = random.choice(['未到', '无故缺席', ''])
            elif status == 'late':
                remark = f"迟到{random.randint(5, 30)}分钟"
            elif status == 'leave':
                remark = random.choice(['病假', '事假', '请假已批准'])
            
            try:
                cursor.execute(
                    """INSERT INTO attendances 
                       (student_id, course_id, date, status, remark, created_at, updated_at) 
                       VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
                    (student_id, course_id, record_date.isoformat(), status, remark)
                )
            except sqlite3.Error as e:
                print(f"插入考勤记录 学生:{student_id} 课程:{course_id} 日期:{record_date} 时出错: {e}")
    
    conn.commit()
    print("考勤记录数据生成完成")

def main():
    """主函数"""
    try:
        # 清空现有数据
        clear_data()
        
        # 生成样例数据
        generate_users()
        generate_course_categories()
        generate_courses()
        generate_enrollments()
        generate_attendances()
        
        print("\n样例数据生成完成！")
        print("默认密码: 123456")
        print("学生账号示例: S2023000")
        print("教师账号示例: T1000")
        print("管理员账号示例: A100")
    except Exception as e:
        print(f"生成样例数据时出错: {e}")
    finally:
        # 关闭数据库连接
        conn.close()

if __name__ == "__main__":
    main()