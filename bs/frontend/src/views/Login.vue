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
      console.log('Login method called')
      try {
        // 表单验证
        console.log('Attempting form validation')
        await this.$refs.loginFormRef.validate()
        console.log('Form validation passed')
        
        console.log('Login form data:', this.loginForm)
        
        // 创建一个新对象，确保只发送必要的字段
        const loginData = {
          username: this.loginForm.username,
          password: this.loginForm.password,
          user_type: this.loginForm.user_type
        }
        
        console.log('Sending login request to:', 'http://127.0.0.1:5000/auth/login')
        console.log('Login request data:', loginData)
        
        const response = await axios.post('http://127.0.0.1:5000/auth/login', loginData, {
          headers: {
            'Content-Type': 'application/json'
          },
          withCredentials: true // 确保跨域请求携带凭证
        })
        
        console.log('Login response received:', response)
        console.log('Response status:', response.status)
        console.log('Response data:', response.data)
        
        // 无论响应结构如何，只要状态码是200就认为登录成功
        if (response.status === 200) {
          // 保存用户信息，确保包含role字段以匹配权限控制要求
          const userData = {
            ...(response.data || {}),
            ...(response.data.user || {}), // 兼容后端可能返回的嵌套user对象
            role: this.loginForm.user_type
          }
          console.log('Prepared user data for storage:', userData)
          
          try {
            localStorage.setItem('user', JSON.stringify(userData))
            console.log('User data saved to localStorage successfully')
            console.log('Current localStorage user:', localStorage.getItem('user'))
          } catch (storageError) {
            console.error('Error saving to localStorage:', storageError)
          }
          
          ElMessage.success('登录成功')
          
          // 延迟一点再跳转，确保localStorage保存完成
          setTimeout(() => {
            // 根据角色跳转到不同页面
            const targetPath = '/' + this.loginForm.user_type + '/dashboard'
            console.log('Attempting to navigate to:', targetPath)
            try {
              // 尝试使用绝对路径跳转
              router.push({ path: targetPath })
              console.log('Navigation command executed')
            } catch (navError) {
              console.error('Navigation error:', navError)
              // 如果路由跳转失败，直接修改location
              console.log('Falling back to window.location.href')
              window.location.href = targetPath
            }
          }, 100)
        } else {
          console.warn('Login response status not 200:', response.status)
          ElMessage.error(response.data?.message || '登录失败')
        }
      } catch (error) {
        console.error('=== Login Error Started ===')
        console.error('Error object type:', typeof error)
        console.error('Error object:', error)
        if (error.response) {
          console.error('Error response status:', error.response.status)
          console.error('Error response data:', error.response.data)
          console.error('Error response headers:', error.response.headers)
        } else if (error.request) {
          console.error('No response received:', error.request)
        } else {
          console.error('Error message:', error.message)
        }
        console.error('Error config:', error.config)
        console.error('=== Login Error Ended ===')
        
        const errorMessage = error.response?.data?.message || '登录失败，请重试'
        console.error('Displaying error message:', errorMessage)
        ElMessage.error(errorMessage)
      }
    },
    toRegister() {
      router.push('/register')
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