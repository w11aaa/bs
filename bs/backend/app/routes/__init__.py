from app.routes.auth import auth_bp
from app.routes.student import student_bp
from app.routes.teacher import teacher_bp
from app.routes.course import course_bp
from app.routes.attendance import attendance_bp
from app.routes.admin import admin_bp

__all__ = ['auth_bp', 'student_bp', 'teacher_bp', 'course_bp', 'attendance_bp', 'admin_bp']