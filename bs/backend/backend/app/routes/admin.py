from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Admin, Student, Teacher, Course, CourseCategory, Enrollment, Attendance
from datetime import datetime
import os
import base64
from app.utils import face_recognizer

# 创建蓝图
admin_bp = Blueprint('admin', __name__)

# 验证管理员身份的装饰器
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    decorated_function.__doc__ = f.__doc__
    decorated_function.__module__ = f.__module__
    return decorated_function

# 创建管理员（初始化使用）
@admin_bp.route('/create_admin', methods=['POST'])
def create_admin():
    try:
        # 检查是否已有管理员
        if Admin.query.first():
            return jsonify({'message': '管理员已存在，禁止重复创建'}), 403
        
        data = request.get_json()
        
        # 创建管理员
        admin = Admin(
            username=data.get('username'),
            email=data.get('email'),
            admin_id=data.get('admin_id'),
            name=data.get('name')
        )
        admin.set_password(data.get('password'))
        
        db.session.add(admin)
        db.session.commit()
        
        return jsonify({'message': '管理员创建成功'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建失败: {str(e)}'}), 500

# 用户管理 - 获取所有学生
@admin_bp.route('/students', methods=['GET'])
@admin_required
def get_all_students():
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        # 构建查询
        query = Student.query
        
        if search:
            query = query.filter(
                (Student.student_id.contains(search)) |
                (Student.name.contains(search)) |
                (Student.username.contains(search)) |
                (Student.major.contains(search))
            )
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 格式化结果
        students = []
        for student in pagination.items:
            students.append({
                'id': student.id,
                'student_id': student.student_id,
                'username': student.username,
                'email': student.email,
                'name': student.name,
                'gender': student.gender,
                'age': student.age,
                'major': student.major,
                'class_name': student.class_name,
                'has_face_data': True if student.face_encoding else False,
                'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'students': students,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取学生列表失败: {str(e)}'}), 500

# 管理员创建学生
@admin_bp.route('/students', methods=['POST'])
@admin_required
def create_student():
    try:
        data = request.get_json()
        
        # 检查学号是否已存在
        if Student.query.filter_by(student_id=data.get('student_id')).first():
            return jsonify({'message': '学号已存在'}), 400
        
        # 检查用户名是否已存在
        if Student.query.filter_by(username=data.get('username')).first():
            return jsonify({'message': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if Student.query.filter_by(email=data.get('email')).first():
            return jsonify({'message': '邮箱已存在'}), 400
        
        # 创建学生
        student = Student(
            username=data.get('username'),
            email=data.get('email'),
            student_id=data.get('student_id'),
            name=data.get('name'),
            gender=data.get('gender'),
            age=data.get('age'),
            major=data.get('major'),
            class_name=data.get('class_name')
        )
        student.set_password(data.get('password', '123456'))  # 默认密码
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({'message': '学生创建成功', 'student_id': student.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建学生失败: {str(e)}'}), 500

# 更新学生信息
@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': '学生不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'username' in data:
            existing = Student.query.filter(Student.username == data['username'], Student.id != student_id).first()
            if existing:
                return jsonify({'message': '用户名已存在'}), 400
            student.username = data['username']
        
        if 'email' in data:
            existing = Student.query.filter(Student.email == data['email'], Student.id != student_id).first()
            if existing:
                return jsonify({'message': '邮箱已存在'}), 400
            student.email = data['email']
        
        if 'student_id' in data:
            existing = Student.query.filter(Student.student_id == data['student_id'], Student.id != student_id).first()
            if existing:
                return jsonify({'message': '学号已存在'}), 400
            student.student_id = data['student_id']
        
        if 'name' in data:
            student.name = data['name']
        
        if 'gender' in data:
            student.gender = data['gender']
        
        if 'age' in data:
            student.age = data['age']
        
        if 'major' in data:
            student.major = data['major']
        
        if 'class_name' in data:
            student.class_name = data['class_name']
        
        if 'password' in data:
            student.set_password(data['password'])
        
        db.session.commit()
        return jsonify({'message': '学生信息更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新失败: {str(e)}'}), 500

# 删除学生
@admin_bp.route('/students/<int:student_id>', methods=['DELETE'])
@admin_required
def delete_student(student_id):
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': '学生不存在'}), 404
        
        # 删除学生（会级联删除相关的考勤记录和选课记录）
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'message': '学生删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

# 教师管理 - 获取所有教师
@admin_bp.route('/teachers', methods=['GET'])
@admin_required
def get_all_teachers():
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        # 构建查询
        query = Teacher.query
        
        if search:
            query = query.filter(
                (Teacher.teacher_id.contains(search)) |
                (Teacher.name.contains(search)) |
                (Teacher.username.contains(search)) |
                (Teacher.department.contains(search))
            )
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 格式化结果
        teachers = []
        for teacher in pagination.items:
            teachers.append({
                'id': teacher.id,
                'teacher_id': teacher.teacher_id,
                'username': teacher.username,
                'email': teacher.email,
                'name': teacher.name,
                'gender': teacher.gender,
                'age': teacher.age,
                'title': teacher.title,
                'department': teacher.department,
                'created_at': teacher.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'teachers': teachers,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取教师列表失败: {str(e)}'}), 500

# 创建教师
@admin_bp.route('/teachers', methods=['POST'])
@admin_required
def create_teacher():
    try:
        data = request.get_json()
        
        # 检查教师号是否已存在
        if Teacher.query.filter_by(teacher_id=data.get('teacher_id')).first():
            return jsonify({'message': '教师号已存在'}), 400
        
        # 检查用户名是否已存在
        if Teacher.query.filter_by(username=data.get('username')).first():
            return jsonify({'message': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if Teacher.query.filter_by(email=data.get('email')).first():
            return jsonify({'message': '邮箱已存在'}), 400
        
        # 创建教师
        teacher = Teacher(
            username=data.get('username'),
            email=data.get('email'),
            teacher_id=data.get('teacher_id'),
            name=data.get('name'),
            gender=data.get('gender'),
            age=data.get('age'),
            title=data.get('title'),
            department=data.get('department')
        )
        teacher.set_password(data.get('password', '123456'))  # 默认密码
        
        db.session.add(teacher)
        db.session.commit()
        
        return jsonify({'message': '教师创建成功', 'teacher_id': teacher.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建教师失败: {str(e)}'}), 500

# 更新教师信息
@admin_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
@admin_required
def update_teacher(teacher_id):
    try:
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'message': '教师不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'username' in data:
            existing = Teacher.query.filter(Teacher.username == data['username'], Teacher.id != teacher_id).first()
            if existing:
                return jsonify({'message': '用户名已存在'}), 400
            teacher.username = data['username']
        
        if 'email' in data:
            existing = Teacher.query.filter(Teacher.email == data['email'], Teacher.id != teacher_id).first()
            if existing:
                return jsonify({'message': '邮箱已存在'}), 400
            teacher.email = data['email']
        
        if 'teacher_id' in data:
            existing = Teacher.query.filter(Teacher.teacher_id == data['teacher_id'], Teacher.id != teacher_id).first()
            if existing:
                return jsonify({'message': '教师号已存在'}), 400
            teacher.teacher_id = data['teacher_id']
        
        if 'name' in data:
            teacher.name = data['name']
        
        if 'gender' in data:
            teacher.gender = data['gender']
        
        if 'age' in data:
            teacher.age = data['age']
        
        if 'title' in data:
            teacher.title = data['title']
        
        if 'department' in data:
            teacher.department = data['department']
        
        if 'password' in data:
            teacher.set_password(data['password'])
        
        db.session.commit()
        return jsonify({'message': '教师信息更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新失败: {str(e)}'}), 500

# 删除教师
@admin_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
@admin_required
def delete_teacher(teacher_id):
    try:
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'message': '教师不存在'}), 404
        
        # 检查是否有教授的课程
        if teacher.courses:
            return jsonify({'message': '该教师还有教授的课程，无法删除'}), 400
        
        db.session.delete(teacher)
        db.session.commit()
        
        return jsonify({'message': '教师删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

# 系统统计信息
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    try:
        # 获取统计数据
        total_students = Student.query.count()
        total_teachers = Teacher.query.count()
        total_courses = Course.query.count()
        total_attendances = Attendance.query.count()
        
        # 计算今日考勤
        today = datetime.now().date()
        today_attendances = Attendance.query.filter_by(attendance_date=today).count()
        
        # 计算本月考勤
        current_month = datetime.now().month
        current_year = datetime.now().year
        month_attendances = Attendance.query.filter(
            db.extract('month', Attendance.attendance_date) == current_month,
            db.extract('year', Attendance.attendance_date) == current_year
        ).count()
        
        stats = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_courses': total_courses,
            'total_attendances': total_attendances,
            'today_attendances': today_attendances,
            'month_attendances': month_attendances
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': f'获取统计失败: {str(e)}'}), 500