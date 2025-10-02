from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Student, Course, Enrollment, Attendance
from app.utils import face_recognizer
import os
import base64
from datetime import datetime

# 创建蓝图
student_bp = Blueprint('student', __name__)

# 验证学生身份的装饰器
def student_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'student':
            return jsonify({'message': '权限不足'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    decorated_function.__doc__ = f.__doc__
    decorated_function.__module__ = f.__module__
    return decorated_function

# 更新学生个人信息
@student_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    try:
        data = request.get_json()
        student = Student.query.get(current_user.id)
        
        # 更新可以修改的字段
        if 'email' in data:
            # 检查邮箱是否被其他用户使用
            existing = Student.query.filter(Student.email == data['email'], Student.id != current_user.id).first()
            if existing:
                return jsonify({'message': '邮箱已被使用'}), 400
            student.email = data['email']
        
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
        
        db.session.commit()
        return jsonify({'message': '个人信息更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新失败: {str(e)}'}), 500

# 上传人脸图片
@student_bp.route('/upload_face', methods=['POST'])
@student_required
def upload_face():
    try:
        data = request.get_json()
        base64_image = data.get('image')
        
        if not base64_image:
            return jsonify({'message': '请上传人脸图片'}), 400
        
        # 提取人脸特征
        encoding, message = face_recognizer.extract_face_encoding_from_base64(base64_image)
        
        if encoding is None:
            return jsonify({'message': message}), 400
        
        # 保存人脸特征和图片
        student = Student.query.get(current_user.id)
        student.face_encoding = encoding.tobytes()  # 转换为二进制存储
        
        # 保存图片到服务器
        if 'base64,' in base64_image:
            base64_image = base64_image.split('base64,')[1]
        
        image_bytes = base64.b64decode(base64_image)
        image_filename = f'student_{student.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.jpg'
        image_path = os.path.join('app/static/uploads/face_images', image_filename)
        full_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), image_path)
        
        success, save_message = face_recognizer.save_face_image(image_bytes, full_image_path)
        if not success:
            return jsonify({'message': save_message}), 500
        
        student.face_image_path = image_filename
        db.session.commit()
        
        return jsonify({'message': '人脸信息上传成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'上传失败: {str(e)}'}), 500

# 获取学生的选课列表
@student_bp.route('/courses', methods=['GET'])
@student_required
def get_student_courses():
    try:
        # 获取当前学生的所有选课
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        
        courses = []
        for enrollment in enrollments:
            course = enrollment.course
            teacher = course.teacher
            
            courses.append({
                'course_id': course.id,
                'course_code': course.course_code,
                'name': course.name,
                'teacher': teacher.name,
                'teacher_id': teacher.id,
                'credits': course.credits,
                'semester': course.semester,
                'year': course.year,
                'start_time': course.start_time.strftime('%H:%M') if course.start_time else None,
                'end_time': course.end_time.strftime('%H:%M') if course.end_time else None,
                'day_of_week': course.day_of_week,
                'location': course.location
            })
        
        return jsonify(courses), 200
        
    except Exception as e:
        return jsonify({'message': f'获取课程失败: {str(e)}'}), 500

# 获取学生的考勤记录
@student_bp.route('/attendances', methods=['GET'])
@student_required
def get_student_attendances():
    try:
        # 获取查询参数
        course_id = request.args.get('course_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = Attendance.query.filter_by(student_id=current_user.id)
        
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance_date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance_date <= end)
        
        # 执行查询并获取结果
        attendances = query.order_by(Attendance.attendance_date.desc()).all()
        
        # 格式化结果
        result = []
        for attendance in attendances:
            result.append({
                'id': attendance.id,
                'course_id': attendance.course_id,
                'course_name': attendance.course.name,
                'attendance_date': attendance.attendance_date.strftime('%Y-%m-%d'),
                'check_in_time': attendance.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_in_time else None,
                'status': attendance.status,
                'remarks': attendance.remarks
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'获取考勤记录失败: {str(e)}'}), 500

# 获取学生考勤统计
@student_bp.route('/attendance_stats', methods=['GET'])
@student_required
def get_attendance_stats():
    try:
        course_id = request.args.get('course_id')
        
        # 构建查询
        query = Attendance.query.filter_by(student_id=current_user.id)
        
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        # 获取所有考勤记录
        attendances = query.all()
        
        # 统计
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == 'present')
        late = sum(1 for a in attendances if a.status == 'late')
        absent = sum(1 for a in attendances if a.status == 'absent')
        
        # 计算出勤率
        attendance_rate = (present / total * 100) if total > 0 else 0
        
        stats = {
            'total_classes': total,
            'present': present,
            'late': late,
            'absent': absent,
            'attendance_rate': round(attendance_rate, 2)
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': f'获取考勤统计失败: {str(e)}'}), 500