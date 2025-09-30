<template>
  <div class="register-container">
    <div class="register-form">
      <h2>学生注册</h2>
      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="100px">
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="registerForm.student_id" placeholder="请输入学号" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="registerForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="registerForm.confirm_password" type="password" placeholder="请再次输入密码" />
        </el-form-item>
        <el-form-item label="人脸图片">
          <el-upload
            class="avatar-uploader"
            action=""
            :on-change="handleAvatarChange"
            :auto-upload="false"
            :show-file-list="true"
            accept="image/*"
          >
            <img v-if="registerForm.face_image_url" :src="registerForm.face_image_url" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="tip">请上传清晰的人脸照片（用于人脸识别考勤）</div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="register" style="width: 100%">注册</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="toLogin" style="width: 100%">已有账号，去登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { Plus } from '@element-plus/icons-vue'

export default {
  name: 'Register',
  components: {
    Plus
  },
  data() {
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
          student_id: '',
          name: '',
          email: '',
          username: '',
          password: '',
          confirm_password: '',
          face_image: null,
          face_image_url: ''
        },
      rules: {
        student_id: [
          { required: true, message: '请输入学号', trigger: 'blur' },
          { min: 8, max: 20, message: '学号长度在 8 到 20 个字符', trigger: 'blur' }
        ],
        name: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
        ],
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 4, max: 20, message: '用户名长度在 4 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    handleAvatarChange(file) {
      this.registerForm.face_image = file.raw
      // 创建图片预览URL
      const reader = new FileReader()
      reader.onload = (e) => {
        this.registerForm.face_image_url = e.target.result
      }
      reader.readAsDataURL(file.raw)
    },
    async register() {
      try {
        await this.$refs.registerFormRef.validate()
        
        if (!this.registerForm.face_image) {
          ElMessage.warning('请上传人脸照片')
          return
        }
        
        const formData = new FormData()
        formData.append('student_id', this.registerForm.student_id)
        formData.append('name', this.registerForm.name)
        formData.append('email', this.registerForm.email)
        formData.append('username', this.registerForm.username)
        formData.append('password', this.registerForm.password)
        formData.append('face_image', this.registerForm.face_image)
        formData.append('user_type', 'student')
        
        const response = await axios.post('http://127.0.0.1:5000/auth/register', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // 检查是否成功
        if (response.success === true || !response.message) {
          ElMessage.success('注册成功，请登录')
          router.push('/login')
        } else {
          ElMessage.error(response.message || '注册失败')
        }
      } catch (error) {
        ElMessage.error('注册失败，请重试')
        console.error('Register error:', error)
      }
    },
    toLogin() {
      router.push('/login')
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-form {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 450px;
}

.register-form h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: block;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}

.tip {
  margin-top: 10px;
  color: #909399;
  font-size: 12px;
}
</style>