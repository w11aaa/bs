from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Attendance, Course, Student, Enrollment
from datetime import datetime, date
import pandas as pd
import io
import base64

# 创建蓝图
attendance_bp = Blueprint('attendance', __name__)

# 验证教师或管理员身份的装饰器
def teacher_or_admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'teacher' and current_user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    decorated_function.__doc__ = f.__doc__
    decorated_function.__module__ = f.__module__
    return decorated_function

# 批量导入考勤记录
@attendance_bp.route('/import', methods=['POST'])
@teacher_or_admin_required
def import_attendances():
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        attendance_date = data.get('date')
        attendances = data.get('attendances')  # 格式: [{student_id: int, status: str, remarks: str}]
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 验证权限（教师只能导入自己课程的考勤）
        if current_user.role == 'teacher' and course.teacher_id != current_user.id:
            return jsonify({'message': '无权限导入此课程的考勤记录'}), 403
        
        # 转换日期格式
        try:
            attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': '日期格式错误'}), 400
        
        # 批量创建或更新考勤记录
        success_count = 0
        error_count = 0
        errors = []
        
        for item in attendances:
            try:
                student_id = item.get('student_id')
                status = item.get('status')
                remarks = item.get('remarks', '')
                
                # 验证学生是否选修了该课程
                enrollment = Enrollment.query.filter_by(
                    student_id=student_id,
                    course_id=course_id
                ).first()
                
                if not enrollment:
                    error_count += 1
                    errors.append(f'学生ID {student_id} 未选修该课程')
                    continue
                
                # 检查是否已存在考勤记录
                attendance = Attendance.query.filter_by(
                    student_id=student_id,
                    course_id=course_id,
                    attendance_date=attendance_date_obj
                ).first()
                
                if attendance:
                    # 更新现有记录
                    attendance.status = status
                    attendance.remarks = remarks
                else:
                    # 创建新记录
                    attendance = Attendance(
                        student_id=student_id,
                        course_id=course_id,
                        attendance_date=attendance_date_obj,
                        status=status,
                        remarks=remarks
                    )
                    db.session.add(attendance)
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f'处理学生ID {item.get("student_id")} 时出错: {str(e)}')
        
        # 提交事务
        if success_count > 0:
            db.session.commit()
        
        return jsonify({
            'message': '考勤导入完成',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'导入失败: {str(e)}'}), 500

# 导出考勤记录
@attendance_bp.route('/export', methods=['GET'])
@teacher_or_admin_required
def export_attendances():
    try:
        course_id = request.args.get('course_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 验证权限
        if current_user.role == 'teacher' and course.teacher_id != current_user.id:
            return jsonify({'message': '无权限导出此课程的考勤记录'}), 403
        
        # 构建查询
        query = Attendance.query.filter_by(course_id=course_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance_date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance_date <= end)
        
        # 执行查询
        attendances = query.all()
        
        # 准备导出数据
        export_data = []
        
        for attendance in attendances:
            student = Student.query.get(attendance.student_id)
            
            export_data.append({
                '学号': student.student_id,
                '姓名': student.name,
                '考勤日期': attendance.attendance_date.strftime('%Y-%m-%d'),
                '签到时间': attendance.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if attendance.check_in_time else '',
                '状态': attendance.status,
                '备注': attendance.remarks
            })
        
        # 创建DataFrame并导出为Excel
        df = pd.DataFrame(export_data)
        
        # 使用BytesIO作为文件对象
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='考勤记录')
        
        # 获取Excel内容
        output.seek(0)
        excel_data = output.getvalue()
        
        # 将Excel数据转换为base64
        excel_base64 = base64.b64encode(excel_data).decode('utf-8')
        
        return jsonify({
            'message': '考勤记录导出成功',
            'excel_data': excel_base64,
            'filename': f'考勤记录_{course.name}_{datetime.now().strftime("%Y%m%d")}.xlsx'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'导出失败: {str(e)}'}), 500

# 获取考勤统计
@attendance_bp.route('/stats', methods=['GET'])
@teacher_or_admin_required
def get_attendance_stats():
    try:
        course_id = request.args.get('course_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 验证权限
        if current_user.role == 'teacher' and course.teacher_id != current_user.id:
            return jsonify({'message': '无权限查看此课程的考勤统计'}), 403
        
        # 构建查询
        query = Attendance.query.filter_by(course_id=course_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance_date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.attendance_date <= end)
        
        # 获取所有考勤记录
        attendances = query.all()
        
        # 按学生分组统计
        student_stats = {}
        for attendance in attendances:
            student_id = attendance.student_id
            if student_id not in student_stats:
                student_stats[student_id] = {
                    'student_id': student_id,
                    'student_no': '',
                    'name': '',
                    'total': 0,
                    'present': 0,
                    'late': 0,
                    'absent': 0
                }
            
            stats = student_stats[student_id]
            stats['total'] += 1
            
            if attendance.status == 'present':
                stats['present'] += 1
            elif attendance.status == 'late':
                stats['late'] += 1
            elif attendance.status == 'absent':
                stats['absent'] += 1
        
        # 获取学生详细信息
        result = []
        for student_id, stats in student_stats.items():
            student = Student.query.get(student_id)
            if student:
                stats['student_no'] = student.student_id
                stats['name'] = student.name
                # 计算出勤率
                stats['attendance_rate'] = (stats['present'] / stats['total'] * 100) if stats['total'] > 0 else 0
                result.append(stats)
        
        # 按出勤率排序
        result.sort(key=lambda x: x['attendance_rate'], reverse=True)
        
        # 计算整体统计
        overall_total = len(attendances)
        overall_present = sum(1 for a in attendances if a.status == 'present')
        overall_late = sum(1 for a in attendances if a.status == 'late')
        overall_absent = sum(1 for a in attendances if a.status == 'absent')
        
        # 获取学生总数（选修该课程的学生数）
        student_count = Enrollment.query.filter_by(course_id=course_id).count()
        
        overall_stats = {
            'total_records': overall_total,
            'total_students': student_count,
            'present': overall_present,
            'late': overall_late,
            'absent': overall_absent,
            'average_attendance_rate': (overall_present / overall_total * 100) if overall_total > 0 else 0
        }
        
        return jsonify({
            'overall_stats': overall_stats,
            'student_stats': result
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取统计失败: {str(e)}'}), 500

# 手动创建考勤记录
@attendance_bp.route('/create', methods=['POST'])
@teacher_or_admin_required
def create_attendance():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        attendance_date = data.get('date')
        status = data.get('status')
        remarks = data.get('remarks', '')
        
        # 检查课程是否存在
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': '课程不存在'}), 404
        
        # 验证权限
        if current_user.role == 'teacher' and course.teacher_id != current_user.id:
            return jsonify({'message': '无权限为此课程创建考勤记录'}), 403
        
        # 检查学生是否存在
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'message': '学生不存在'}), 404
        
        # 检查学生是否选修了该课程
        enrollment = Enrollment.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({'message': '学生未选修该课程'}), 400
        
        # 转换日期格式
        try:
            attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': '日期格式错误'}), 400
        
        # 检查是否已存在考勤记录
        existing = Attendance.query.filter_by(
            student_id=student_id,
            course_id=course_id,
            attendance_date=attendance_date_obj
        ).first()
        
        if existing:
            return jsonify({'message': '该学生在此日期已有考勤记录'}), 400
        
        # 创建考勤记录
        attendance = Attendance(
            student_id=student_id,
            course_id=course_id,
            attendance_date=attendance_date_obj,
            status=status,
            remarks=remarks
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({'message': '考勤记录创建成功'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建失败: {str(e)}'}), 500