# 互联网课堂考勤系统

## 项目简介
基于人脸识别的互联网课堂考勤系统是一种网络化的管理软件，提供了课程管理、课程分类、学生人脸识别考勤、上课考勤、学生信息，教师信息管理，学生教师注册登录退出等功能，为学校节省了大量的时间和人力成本。

## 技术栈

### 后端
- Python 3.8+
- Flask 2.3.2
- Flask-SQLAlchemy 3.0.5
- Flask-Migrate 4.0.5
- Flask-Login 0.6.2
- MySQL 8.0
- face-recognition 1.3.0 (人脸识别库)
- OpenCV 4.8.0

### 前端
- Vue.js 3.3.4
- Vue Router 4.2.4
- Element Plus 2.3.9
- Vite 4.4.9

## 功能特性

### 学生功能
- 用户注册与登录
- 个人信息管理
- 人脸照片上传
- 课程列表查看
- 考勤记录查询
- 考勤统计查看

### 教师功能
- 用户登录
- 个人信息管理
- 课程管理（创建、编辑、删除）
- 人脸识别考勤
- 考勤记录查询与修改
- 考勤数据导出

### 管理员功能
- 用户登录
- 学生信息管理（增删改查）
- 教师信息管理（增删改查）
- 管理员创建
- 课程管理
- 课程分类管理
- 系统统计信息查看

## 系统部署

### 后端部署
1. 安装Python 3.8+环境
2. 安装MySQL数据库
3. 克隆项目代码
4. 进入backend目录
5. 安装依赖：`pip install -r requirements.txt`
6. 配置数据库连接（在app/config/development.py中修改）
7. 初始化数据库：
   - `flask db init`
   - `flask db migrate`
   - `flask db upgrade`
8. 启动服务：`python app.py`

### 前端部署
1. 安装Node.js 16+
2. 进入frontend目录
3. 安装依赖：`npm install`
4. 开发模式启动：`npm run dev`
5. 生产模式构建：`npm run build`

## 注意事项
1. 首次使用时，需要先在管理员界面创建教师账号
2. 学生注册时需要上传清晰的人脸照片
3. 人脸识别考勤功能需要浏览器支持摄像头访问
4. 系统默认管理员账号：admin/admin123（需要首次登录后修改密码）

## 项目结构

```
bs/
├── backend/           # 后端代码
│   ├── app/           # 应用主目录
│   │   ├── config/    # 配置文件
│   │   ├── models/    # 数据模型
│   │   ├── routes/    # 路由定义
│   │   ├── utils/     # 工具函数
│   │   ├── static/    # 静态资源
│   │   └── templates/ # 模板文件
│   ├── app.py         # 应用入口
│   └── requirements.txt # 依赖列表
└── frontend/          # 前端代码
    ├── public/        # 公共资源
    ├── src/           # 源代码
    │   ├── assets/    # 静态资源
    │   ├── components/# 组件
    │   ├── views/     # 页面视图
    │   ├── router/    # 路由配置
    │   └── store/     # 状态管理
    ├── index.html     # 入口HTML
    ├── package.json   # 依赖配置
    └── vite.config.js # Vite配置
```