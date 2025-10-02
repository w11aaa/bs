from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Course, CourseCategory, Teacher, Enrollment
from datetime import datetime, time

# 创建蓝图
course_bp = Blueprint('course', __name__)

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

# 创建课程
@course_bp.route('/create', methods=['POST'])
@teacher_required
def create_course():
    try:
        data = request.get_json()
        
        # 检查课程代码是否已存在
        if Course.query.filter_by(course_code=data.get('course_code')).first():
            return jsonify({'message': '课程代码已存在'}), 400
        
        # 处理时间格式
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        start_time = None
        end_time = None
        
        if start_time_str:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
        
        if end_time_str:
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # 创建课程
        course = Course(
            course_code=data.get('course_code'),
            name=data.get('name'),
            description=data.get('description'),
            credits=data.get('credits'),
            semester=data.get('semester'),
            year=data.get('year'),
            start_time=start_time,
            end_time=end_time,
            day_of_week=data.get('day_of_week'),
            location=data.get('location'),
            teacher_id=current_user.id if current_user.role == 'teacher' else data.get('teacher_id'),
            category_id=data.get('category_id')
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({'message': '课程创建成功', 'course_id': course.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建课程失败: {str(e)}'}), 500

# 更新课程信息
@course_bp.route('/<int:course_id>', methods=['PUT'])
@teacher_required
def update_course(course_id):
    try:
        # 获取课程
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 验证权限（只有创建课程的教师或管理员可以修改）
        if current_user.role != 'admin' and course.teacher_id != current_user.id:
            return jsonify({'message': '无权限修改此课程'}), 403
        
        data = request.get_json()
        
        # 更新字段
        if 'course_code' in data:
            # 检查课程代码是否被其他课程使用
            existing = Course.query.filter(Course.course_code == data['course_code'], Course.id != course_id).first()
            if existing:
                return jsonify({'message': '课程代码已存在'}), 400
            course.course_code = data['course_code']
        
        if 'name' in data:
            course.name = data['name']
        
        if 'description' in data:
            course.description = data['description']
        
        if 'credits' in data:
            course.credits = data['credits']
        
        if 'semester' in data:
            course.semester = data['semester']
        
        if 'year' in data:
            course.year = data['year']
        
        if 'start_time' in data:
            course.start_time = datetime.strptime(data['start_time'], '%H:%M').time() if data['start_time'] else None
        
        if 'end_time' in data:
            course.end_time = datetime.strptime(data['end_time'], '%H:%M').time() if data['end_time'] else None
        
        if 'day_of_week' in data:
            course.day_of_week = data['day_of_week']
        
        if 'location' in data:
            course.location = data['location']
        
        if 'teacher_id' in data and current_user.role == 'admin':
            course.teacher_id = data['teacher_id']
        
        if 'category_id' in data:
            course.category_id = data['category_id']
        
        db.session.commit()
        return jsonify({'message': '课程更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新课程失败: {str(e)}'}), 500

# 删除课程
@course_bp.route('/<int:course_id>', methods=['DELETE'])
@teacher_required
def delete_course(course_id):
    try:
        # 获取课程
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 验证权限
        if current_user.role != 'admin' and course.teacher_id != current_user.id:
            return jsonify({'message': '无权限删除此课程'}), 403
        
        # 删除课程（会级联删除相关的考勤记录和选课记录）
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({'message': '课程删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除课程失败: {str(e)}'}), 500

# 获取课程详情
@course_bp.route('/<int:course_id>', methods=['GET'])
@login_required
def get_course(course_id):
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 构建课程信息
        course_info = {
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
            'teacher_id': course.teacher_id,
            'teacher_name': course.teacher.name if course.teacher else None,
            'category_id': course.category_id,
            'category_name': course.category.name if course.category else None,
            'created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(course_info), 200
        
    except Exception as e:
        return jsonify({'message': f'获取课程失败: {str(e)}'}), 500

# 获取课程分类列表
@course_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    try:
        categories = CourseCategory.query.all()
        
        result = []
        for category in categories:
            result.append({
                'id': category.id,
                'name': category.name,
                'description': category.description
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'message': f'获取课程分类失败: {str(e)}'}), 500

# 创建课程分类（仅管理员）
@course_bp.route('/categories', methods=['POST'])
@teacher_required
def create_category():
    try:
        # 只有管理员可以创建课程分类
        if current_user.role != 'admin':
            return jsonify({'message': '只有管理员可以创建课程分类'}), 403
        
        data = request.get_json()
        
        # 检查分类名称是否已存在
        if CourseCategory.query.filter_by(name=data.get('name')).first():
            return jsonify({'message': '分类名称已存在'}), 400
        
        category = CourseCategory(
            name=data.get('name'),
            description=data.get('description')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({'message': '分类创建成功', 'category_id': category.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建分类失败: {str(e)}'}), 500

# 学生选课
@course_bp.route('/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    try:
        # 只有学生可以选课
        if current_user.role != 'student':
            return jsonify({'message': '只有学生可以选课'}), 403
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 检查是否已经选过该课程
        existing = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course_id
        ).first()
        
        if existing:
            return jsonify({'message': '已经选过该课程'}), 400
        
        # 创建选课记录
        enrollment = Enrollment(
            student_id=current_user.id,
            course_id=course_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({'message': '选课成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'选课失败: {str(e)}'}), 500

# 学生退课
@course_bp.route('/<int:course_id>/drop', methods=['POST'])
@login_required
def drop_course(course_id):
    try:
        # 只有学生可以退课
        if current_user.role != 'student':
            return jsonify({'message': '只有学生可以退课'}), 403
        
        # 查找选课记录
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({'message': '未选该课程'}), 404
        
        # 删除选课记录
        db.session.delete(enrollment)
        db.session.commit()
        
        return jsonify({'message': '退课成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'退课失败: {str(e)}'}), 500