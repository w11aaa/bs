<template>
  <div class="login-container">
    <div class="login-form">
      <h2>互联网课堂考勤系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角色" prop="user_type">
          <el-radio-group v-model="loginForm.user_type">
            <el-radio label="student">学生</el-radio>
            <el-radio label="teacher">教师</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login" style="width: 100%">登录</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="toRegister" style="width: 100%">注册(学生)</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="fillTestCredentials" type="info" style="width: 100%">填充测试凭据</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: '',
        user_type: 'student'
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ],
        user_type: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      }
    }
  },
  methods: {
    async login() {
      try {
        // 1. 表单验证
        console.log('开始登录验证');
        await this.$refs.loginFormRef.validate();
        console.log('表单验证通过');
        
        const loginData = {
          username: this.loginForm.username,
          password: this.loginForm.password,
          user_type: this.loginForm.user_type
        }
        console.log('准备发送登录请求:', loginData);
        
        // 使用绝对URL直接访问后端API，绕过可能有问题的代理配置
        const directAxios = axios.create({
            // 确保不使用全局baseURL
            baseURL: ''
        });
        
        // 发送登录请求到后端API
        const response = await directAxios.post('http://127.0.0.1:5000/auth/login', loginData);
        console.log('登录请求返回响应:', response);
        
        // 从响应中获取数据部分（因为新创建的axios实例没有应用响应拦截器）
        const result = response.data;
        console.log('登录请求返回数据:', result);
        
        // 3. 检查返回的数据内容
        if (result && result.message === '登录成功' && result.user) {
          // 4. 存储从后端获取的干净的用户信息
          try {
            localStorage.setItem('user', JSON.stringify(result.user));
            console.log('用户信息已存储到localStorage:', result.user);
          } catch (storageError) {
            console.error('localStorage存储失败:', storageError);
          }
          
          // 添加更明显的成功提示
          const successMsg = '登录成功！用户：' + result.user.username + '，角色：' + result.user.role;
          console.log(successMsg);
          ElMessage.success(successMsg);
          
          // 5. 根据后端返回的角色进行跳转，更安全
          const targetPath = `/${result.user.role}/dashboard`;
          console.log('准备跳转到:', targetPath);
          
          // 使用setTimeout确保localStorage保存完成，并使用try-catch捕获可能的路由错误
          setTimeout(() => {
            try {
              router.push(targetPath);
              console.log('路由跳转已执行');
            } catch (routerError) {
              console.error('路由跳转失败:', routerError);
              // 备用方案：使用window.location.href
              window.location.href = targetPath;
              console.log('备用跳转方案已执行');
            }
          }, 100);

        } else {
          console.error('登录失败，返回数据格式不正确:', JSON.stringify(result));
          // 更详细地检查结果对象的属性
          console.error('Result object keys:', result ? Object.keys(result) : 'No result object');
          // 优先显示后端返回的错误信息，保持与外层错误处理一致
          const errorMsg = result?.message || '登录失败，返回数据格式不正确';
          console.error('详细错误信息:', errorMsg);
          ElMessage.error(errorMsg);
        }
      } catch (error) {
        console.error('Login Error:', error);
        console.error('Error type:', typeof error);
        console.error('Error object keys:', Object.keys(error || {}));
        console.error('Error response:', error?.response || 'No response');
        console.error('Error request:', error?.request || 'No request');
        
        // 优先显示后端返回的错误信息
        let errorMessage;
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', JSON.stringify(error.response.data));
          errorMessage = error.response.data?.message || `后端返回错误: ${error.response.status}`;
        } else if (error.request) {
          console.error('No response received from server');
          errorMessage = '服务器无响应，请检查网络连接';
        } else {
          console.error('Request setup error:', error.message);
          errorMessage = `请求错误: ${error.message}`;
        }
        
        ElMessage.error(errorMessage);
      }
    },
    toRegister() {
      router.push('/register')
    },
    fillTestCredentials() {
      // 默认管理员凭据
      this.loginForm.username = 'admin';
      this.loginForm.password = 'admin123';
      this.loginForm.user_type = 'admin';
      ElMessage.info('已填充管理员测试凭据');
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 400px;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}
</style>
