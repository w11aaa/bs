from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Teacher, Course, Student, Attendance, Enrollment
from app.utils import face_recognizer
from datetime import datetime, time
import os
import base64

# 创建蓝图
teacher_bp = Blueprint('teacher', __name__)

# 验证教师身份的装饰器
def teacher_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'teacher' and current_user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    decorated_function.__doc__ = f.__doc__
    decorated_function.__module__ = f.__module__
    return decorated_function

# 更新教师个人信息
@teacher_bp.route('/profile', methods=['PUT'])
@teacher_required
def update_profile():
    try:
        data = request.get_json()
        teacher = Teacher.query.get(current_user.id)
        
        # 更新可以修改的字段
        if 'email' in data:
            # 检查邮箱是否被其他用户使用
            existing = Teacher.query.filter(Teacher.email == data['email'], Teacher.id != current_user.id).first()
            if existing:
                return jsonify({'message': '邮箱已被使用'}), 400
            teacher.email = data['email']
        
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
        
        db.session.commit()
        return jsonify({'message': '个人信息更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新失败: {str(e)}'}), 500

# 获取教师教授的课程列表
@teacher_bp.route('/courses', methods=['GET'])
@teacher_required
def get_teacher_courses():
    try:
        # 获取当前教师的所有课程
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        
        result = []
        for course in courses:
            result.append({
                'course_id': course.id,
                'course_code': course.course_code,
                'name': course.name,
                'description': course.description,
                'credits': course.credits,
                'semester': course.semester,
                'year': course.year,
                'start_time': course.start_time.strftime('%H:%M') if course.start_time else None,
                'end_time': course.end_time.strftime('%H:%M') if course.end_time else None,
                'day_of_week': course.day_of_week,
                'location': course.location,
                'category_id': course.category_id,
                'category_name': course.category.name if course.category else None
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'获取课程失败: {str(e)}'}), 500

# 获取课程的学生列表
@teacher_bp.route('/courses/<int:course_id>/students', methods=['GET'])
@teacher_required
def get_course_students(course_id):
    try:
        # 验证课程是否属于当前教师
        course = Course.query.filter_by(id=course_id, teacher_id=current_user.id).first()
        if not course:
            return jsonify({'message': '课程不存在或无权限'}), 404
        
        # 获取课程的所有学生
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        
        students = []
        for enrollment in enrollments:
            student = enrollment.student
            students.append({
                'student_id': student.id,
                'student_no': student.student_id,
                'name': student.name,
                'gender': student.gender,
                'age': student.age,
                'major': student.major,
                'class_name': student.class_name,
                'has_face_data': True if student.face_encoding else False
            })
        
        return jsonify(students), 200
        
    except Exception as e:
        return jsonify({'message': f'获取学生列表失败: {str(e)}'}), 500

# 获取课程的考勤记录
@teacher_bp.route('/courses/<int:course_id>/attendances', methods=['GET'])
@teacher_required
def get_course_attendances(course_id):
    try:
        # 验证课程是否属于当前教师
        course = Course.query.filter_by(id=course_id, teacher_id=current_user.id).first()
        if not course:
            return jsonify({'message': '课程不存在或无权限'}), 404
        
        # 获取查询参数
        attendance_date = request.args.get('date')
        
        # 构建查询
        query = Attendance.query.filter_by(course_id=course_id)
        
        if attendance_date:
            date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
            query = query.filter_by(attendance_date=date)
        
        # 执行查询并获取结果
        attendances = query.order_by(Attendance.attendance_date.desc(), Attendance.student_id).all()
        
        # 格式化结果
        result = []
        for attendance in attendances:
            student = attendance.student
            result.append({
                'id': attendance.id,
                'student_id': student.id,
                'student_no': student.student_id,
                'student_name': student.name,
                'attendance_date': attendance.attendance_date.strftime('%Y-%m-%d'),
                'check_in_time': attendance.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_in_time else None,
                'status': attendance.status,
                'face_match_score': attendance.face_match_score,
                'remarks': attendance.remarks
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'获取考勤记录失败: {str(e)}'}), 500

# 人脸识别考勤
@teacher_bp.route('/courses/<int:course_id>/face_attendance', methods=['POST'])
@teacher_required
def face_attendance(course_id):
    try:
        # 验证课程是否属于当前教师
        course = Course.query.filter_by(id=course_id, teacher_id=current_user.id).first()
        if not course:
            return jsonify({'message': '课程不存在或无权限'}), 404
        
        data = request.get_json()
        base64_image = data.get('image')
        
        if not base64_image:
            return jsonify({'message': '请上传人脸图片'}), 400
        
        # 提取人脸特征
        encoding, message = face_recognizer.extract_face_encoding_from_base64(base64_image)
        
        if encoding is None:
            return jsonify({'message': message}), 400
        
        # 获取课程的所有学生（带有面部数据）
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        known_encodings_with_ids = []
        
        for enrollment in enrollments:
            student = enrollment.student
            if student.face_encoding:
                known_encodings_with_ids.append((student.face_encoding, student.id))
        
        if not known_encodings_with_ids:
            return jsonify({'message': '该课程的学生尚未上传人脸数据'}), 400
        
        # 识别人脸
        is_match, student_id, score = face_recognizer.recognize_faces(encoding, known_encodings_with_ids)
        
        if not is_match:
            return jsonify({'message': '未识别到匹配的学生', 'score': score}), 400
        
        # 获取当前日期
        today = datetime.now().date()
        now = datetime.now()
        
        # 检查是否已经考勤
        attendance = Attendance.query.filter_by(
            student_id=student_id,
            course_id=course_id,
            attendance_date=today
        ).first()
        
        if attendance:
            return jsonify({'message': '该学生今天已经考勤'}), 400
        
        # 确定考勤状态（迟到/准时）
        status = 'present'
        if course.start_time:
            # 计算迟到时间
            current_time = now.time()
            if current_time > course.start_time:
                # 计算迟到的分钟数
                course_start = datetime.combine(today, course.start_time)
                minutes_late = (now - course_start).total_seconds() / 60
                if minutes_late > 15:  # 超过15分钟算迟到
                    status = 'late'
        
        # 创建考勤记录
        attendance = Attendance(
            student_id=student_id,
            course_id=course_id,
            attendance_date=today,
            check_in_time=now,
            status=status,
            face_match_score=score
        )
        
        # 保存考勤图片
        if 'base64,' in base64_image:
            base64_image = base64_image.split('base64,')[1]
        
        image_bytes = base64.b64decode(base64_image)
        image_filename = f'attendance_{course_id}_{student_id}_{now.strftime("%Y%m%d%H%M%S")}.jpg'
        image_path = os.path.join('app/static/uploads/attendance_images', image_filename)
        full_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), image_path)
        
        success, save_message = face_recognizer.save_face_image(image_bytes, full_image_path)
        if success:
            attendance.image_path = image_filename
        
        db.session.add(attendance)
        db.session.commit()
        
        # 获取学生信息
        student = Student.query.get(student_id)
        
        return jsonify({
            'message': '考勤成功',
            'student': {
                'student_id': student.student_id,
                'name': student.name
            },
            'attendance': {
                'status': status,
                'check_in_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'score': score
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'考勤失败: {str(e)}'}), 500

# 手动修改考勤记录
@teacher_bp.route('/attendances/<int:attendance_id>', methods=['PUT'])
@teacher_required
def update_attendance(attendance_id):
    try:
        # 获取考勤记录
        attendance = Attendance.query.get(attendance_id)
        if not attendance:
            return jsonify({'message': '考勤记录不存在'}), 404
        
        # 验证课程是否属于当前教师
        if attendance.course.teacher_id != current_user.id:
            return jsonify({'message': '无权限修改此考勤记录'}), 403
        
        data = request.get_json()
        
        # 更新字段
        if 'status' in data:
            attendance.status = data['status']
        
        if 'remarks' in data:
            attendance.remarks = data['remarks']
        
        db.session.commit()
        return jsonify({'message': '考勤记录更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新失败: {str(e)}'}), 500