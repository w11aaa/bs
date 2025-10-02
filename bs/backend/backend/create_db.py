import pymysql
import os

# 数据库连接信息
DB_USER = 'root'
DB_PASSWORD = '123456'  # 使用123456密码
DB_HOST = '127.0.0.1'  # 使用IP地址避免解析问题
DB_PORT = 3306

# 需要创建的数据库列表
DATABASES = ['attendance_system_dev', 'attendance_system_test', 'attendance_system']

try:
    # 连接到MySQL服务器（不需要指定数据库）
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 创建每个数据库
    for db_name in DATABASES:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {db_name} 创建成功！")
    
    # 关闭连接
    cursor.close()
    conn.close()
    
    print("所有数据库创建完成！")
    
except Exception as e:
    print(f"创建数据库时出错: {e}")