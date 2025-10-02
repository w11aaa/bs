<template>
  <div class="profile-container">
    <h2>个人资料</h2>
    
    <el-card class="profile-card">
      <el-form 
        :model="profileForm" 
        :rules="rules" 
        ref="profileFormRef" 
        label-width="100px"
        v-loading="loading"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学号" prop="student_id">
              <el-input v-model="profileForm.student_id" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="profileForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="profileForm.gender" placeholder="请选择性别">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄" prop="age">
              <el-input-number v-model="profileForm.age" :min="16" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-input v-model="profileForm.major" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="班级" prop="class_name">
              <el-input v-model="profileForm.class_name" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="人脸照片">
          <div class="face-image-container">
            <img v-if="faceImageUrl" :src="faceImageUrl" class="face-image" />
            <div v-else class="no-image">暂无人脸照片</div>
            <el-upload
              class="upload-btn"
              action="#"
              :http-request="uploadFaceImage"
              :show-file-list="false"
              accept="image/*"
            >
              <el-button type="primary">更新人脸照片</el-button>
            </el-upload>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">保存修改</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="password-card">
      <div class="card-header">
        <h3>修改密码</h3>
      </div>
      <el-form 
        :model="passwordForm" 
        :rules="passwordRules" 
        ref="passwordFormRef" 
        label-width="120px"
      >
        <el-form-item label="当前密码" prop="current_password">
          <el-input 
            v-model="passwordForm.current_password" 
            type="password" 
            show-password 
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input 
            v-model="passwordForm.new_password" 
            type="password" 
            show-password 
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input 
            v-model="passwordForm.confirm_password" 
            type="password" 
            show-password 
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword">修改密码</el-button>
          <el-button @click="resetPasswordForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ref, reactive, onMounted } from 'vue'

export default {
  name: 'StudentProfile',
  setup() {
    const profileFormRef = ref(null)
    const passwordFormRef = ref(null)
    const loading = ref(false)
    const faceImageUrl = ref('')
    
    // 个人资料表单
    const profileForm = reactive({
      student_id: '',
      username: '',
      name: '',
      email: '',
      gender: '',
      age: null,
      major: '',
      class_name: ''
    })
    
    // 密码表单
    const passwordForm = reactive({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      gender: [
        { required: true, message: '请选择性别', trigger: 'change' }
      ]
    }
    
    // 密码表单验证规则
    const passwordRules = {
      current_password: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      new_password: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
      ],
      confirm_password: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.new_password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
    
    // 加载个人资料
    const loadProfile = async () => {
      loading.value = true
      try {
        const res = await axios.get('/student/profile')
        if (res.data) {
          Object.assign(profileForm, res.data)
          
          // 加载人脸照片
          if (res.data.face_image) {
            faceImageUrl.value = `/api/static/uploads/face_images/${res.data.face_image}`
          }
        }
      } catch (error) {
        console.error('加载个人资料失败:', error)
        ElMessage.error('加载个人资料失败')
      } finally {
        loading.value = false
      }
    }
    
    // 提交个人资料表单
    const submitForm = async () => {
      if (!profileFormRef.value) return
      
      await profileFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true
          try {
            await axios.put('/student/profile', profileForm)
            ElMessage.success('个人资料更新成功')
            
            // 更新本地存储的用户信息
            const userStr = localStorage.getItem('user')
            if (userStr) {
              const user = JSON.parse(userStr)
              user.name = profileForm.name
              localStorage.setItem('user', JSON.stringify(user))
            }
          } catch (error) {
            console.error('更新个人资料失败:', error)
            ElMessage.error(error.response?.data?.message || '更新个人资料失败')
          } finally {
            loading.value = false
          }
        }
      })
    }
    
    // 重置个人资料表单
    const resetForm = () => {
      if (profileFormRef.value) {
        profileFormRef.value.resetFields()
        loadProfile()
      }
    }
    
    // 上传人脸照片
    const uploadFaceImage = async (options) => {
      const formData = new FormData()
      formData.append('face_image', options.file)
      
      loading.value = true
      try {
        const res = await axios.post('/student/profile/face', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (res.data && res.data.face_image) {
          faceImageUrl.value = `/api/static/uploads/face_images/${res.data.face_image}?t=${Date.now()}`
          ElMessage.success('人脸照片更新成功')
        }
      } catch (error) {
        console.error('上传人脸照片失败:', error)
        ElMessage.error(error.response?.data?.message || '上传人脸照片失败')
      } finally {
        loading.value = false
      }
    }
    
    // 修改密码
    const changePassword = async () => {
      if (!passwordFormRef.value) return
      
      await passwordFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            await axios.put('/auth/password', {
              current_password: passwordForm.current_password,
              new_password: passwordForm.new_password
            })
            
            ElMessage.success('密码修改成功')
            resetPasswordForm()
          } catch (error) {
            console.error('修改密码失败:', error)
            ElMessage.error(error.response?.data?.message || '修改密码失败')
          }
        }
      })
    }
    
    // 重置密码表单
    const resetPasswordForm = () => {
      if (passwordFormRef.value) {
        passwordFormRef.value.resetFields()
      }
    }
    
    onMounted(() => {
      loadProfile()
    })
    
    return {
      profileFormRef,
      passwordFormRef,
      loading,
      profileForm,
      passwordForm,
      rules,
      passwordRules,
      faceImageUrl,
      submitForm,
      resetForm,
      uploadFaceImage,
      changePassword,
      resetPasswordForm
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  margin-bottom: 30px;
}

.password-card {
  margin-top: 30px;
}

.card-header {
  margin-bottom: 20px;
}

.face-image-container {
  display: flex;
  align-items: center;
  gap: 20px;
}

.face-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
}

.no-image {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  color: #909399;
  border-radius: 4px;
}
</style>