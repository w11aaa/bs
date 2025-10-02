<template>
  <div class="profile-container">
    <h2>个人资料</h2>
    
    <el-card shadow="hover" class="profile-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form
            :model="profileForm"
            :rules="profileRules"
            ref="profileFormRef"
            label-width="100px"
            class="profile-form"
          >
            <el-form-item label="姓名" prop="name">
              <el-input v-model="profileForm.name" />
            </el-form-item>
            
            <el-form-item label="工号" prop="teacher_id">
              <el-input v-model="profileForm.teacher_id" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="profileForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="年龄" prop="age">
              <el-input-number v-model="profileForm.age" :min="18" :max="100" />
            </el-form-item>
            
            <el-form-item label="职称" prop="title">
              <el-select v-model="profileForm.title" placeholder="请选择职称">
                <el-option label="助教" value="助教" />
                <el-option label="讲师" value="讲师" />
                <el-option label="副教授" value="副教授" />
                <el-option label="教授" value="教授" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="所属院系" prop="department">
              <el-input v-model="profileForm.department" />
            </el-form-item>
            
            <el-form-item label="研究方向" prop="research_area">
              <el-input v-model="profileForm.research_area" type="textarea" :rows="3" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="人脸信息" name="face">
          <div class="face-container">
            <div class="current-face" v-if="faceImageUrl">
              <h3>当前人脸照片</h3>
              <img :src="faceImageUrl" alt="人脸照片" class="face-image" />
            </div>
            
            <div class="face-upload">
              <h3>{{ faceImageUrl ? '更新人脸照片' : '上传人脸照片' }}</h3>
              <el-upload
                class="avatar-uploader"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleFaceChange"
              >
                <img v-if="facePreview" :src="facePreview" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">
                请上传清晰的正面照片，确保光线充足，面部特征清晰可见
              </div>
              <el-button type="primary" @click="uploadFace" :disabled="!faceFile">
                {{ faceImageUrl ? '更新照片' : '上传照片' }}
              </el-button>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="修改密码" name="password">
          <el-form
            :model="passwordForm"
            :rules="passwordRules"
            ref="passwordFormRef"
            label-width="100px"
            class="password-form"
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
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'

export default {
  name: 'TeacherProfile',
  components: {
    Plus
  },
  setup() {
    const activeTab = ref('basic')
    const profileFormRef = ref(null)
    const passwordFormRef = ref(null)
    const faceImageUrl = ref('')
    const facePreview = ref('')
    const faceFile = ref(null)
    
    // 个人资料表单
    const profileForm = reactive({
      name: '',
      teacher_id: '',
      email: '',
      gender: '',
      age: 30,
      title: '',
      department: '',
      research_area: ''
    })
    
    // 密码表单
    const passwordForm = reactive({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })
    
    // 表单验证规则
    const profileRules = {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      gender: [
        { required: true, message: '请选择性别', trigger: 'change' }
      ],
      age: [
        { required: true, message: '请输入年龄', trigger: 'blur' }
      ],
      title: [
        { required: true, message: '请选择职称', trigger: 'change' }
      ],
      department: [
        { required: true, message: '请输入所属院系', trigger: 'blur' }
      ]
    }
    
    const passwordRules = {
      current_password: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      new_password: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
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
      try {
        const res = await axios.get('/teacher/profile')
        const data = res.data
        
        if (data) {
          profileForm.name = data.name || ''
          profileForm.teacher_id = data.teacher_id || ''
          profileForm.email = data.email || ''
          profileForm.gender = data.gender || ''
          profileForm.age = data.age || 30
          profileForm.title = data.title || ''
          profileForm.department = data.department || ''
          profileForm.research_area = data.research_area || ''
          
          // 加载人脸图片
          loadFaceImage()
        }
      } catch (error) {
        console.error('加载个人资料失败:', error)
        ElMessage.error('加载个人资料失败')
      }
    }
    
    // 加载人脸图片
    const loadFaceImage = async () => {
      try {
        const res = await axios.get('/teacher/profile/face', {
          responseType: 'blob'
        })
        
        if (res.data.size > 0) {
          const url = URL.createObjectURL(res.data)
          faceImageUrl.value = url
        }
      } catch (error) {
        console.error('加载人脸图片失败:', error)
        // 不显示错误消息，因为可能没有上传过人脸图片
      }
    }
    
    // 更新个人资料
    const updateProfile = async () => {
      if (!profileFormRef.value) return
      
      await profileFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            await axios.put('/teacher/profile', profileForm)
            ElMessage.success('个人资料更新成功')
          } catch (error) {
            console.error('更新个人资料失败:', error)
            ElMessage.error(error.response?.data?.message || '更新个人资料失败')
          }
        }
      })
    }
    
    // 处理人脸图片变更
    const handleFaceChange = (file) => {
      faceFile.value = file.raw
      
      if (file.raw) {
        // 预览图片
        facePreview.value = URL.createObjectURL(file.raw)
      } else {
        facePreview.value = ''
      }
    }
    
    // 上传人脸图片
    const uploadFace = async () => {
      if (!faceFile.value) {
        ElMessage.warning('请先选择图片')
        return
      }
      
      try {
        const formData = new FormData()
        formData.append('face', faceFile.value)
        
        await axios.post('/teacher/profile/face', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        ElMessage.success('人脸图片上传成功')
        
        // 更新显示的人脸图片
        faceImageUrl.value = facePreview.value
        facePreview.value = ''
        faceFile.value = null
      } catch (error) {
        console.error('上传人脸图片失败:', error)
        ElMessage.error(error.response?.data?.message || '上传人脸图片失败')
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
            
            // 清空表单
            passwordForm.current_password = ''
            passwordForm.new_password = ''
            passwordForm.confirm_password = ''
          } catch (error) {
            console.error('修改密码失败:', error)
            ElMessage.error(error.response?.data?.message || '修改密码失败')
          }
        }
      })
    }
    
    onMounted(() => {
      loadProfile()
    })
    
    return {
      activeTab,
      profileForm,
      passwordForm,
      profileRules,
      passwordRules,
      profileFormRef,
      passwordFormRef,
      faceImageUrl,
      facePreview,
      faceFile,
      updateProfile,
      handleFaceChange,
      uploadFace,
      changePassword
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  margin-top: 20px;
}

.profile-form,
.password-form {
  max-width: 500px;
  margin: 0 auto;
}

.face-container {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
  align-items: flex-start;
}

.current-face,
.face-upload {
  flex: 1;
  min-width: 250px;
}

.face-image {
  width: 200px;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.avatar-uploader {
  width: 200px;
  height: 200px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-tip {
  font-size: 12px;
  color: #606266;
  margin: 10px 0;
}
</style>