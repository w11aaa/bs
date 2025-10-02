from app import create_app
import os

# 创建Flask应用实例
app = create_app(config_name='development')

if __name__ == '__main__':
    # 创建必要的目录
    upload_dir = os.path.join(app.root_path, 'static/uploads/face_images')
    os.makedirs(upload_dir, exist_ok=True)
    
    attendance_dir = os.path.join(app.root_path, 'static/uploads/attendance_images')
    os.makedirs(attendance_dir, exist_ok=True)
    
    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=True)