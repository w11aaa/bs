<template>
  <div class="attendance-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>互联网课堂考勤系统 - 教师端</h1>
          <el-dropdown>
            <span class="user-info">
              {{ user.name }} <el-icon><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="toProfile">个人资料</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="200px">
          <el-menu
            :default-active="activeMenu"
            class="sidebar-menu"
            router
            :unique-opened="true"
          >
            <el-menu-item index="/teacher/dashboard">
              <el-icon><home /></el-icon>
              <span>仪表板</span>
            </el-menu-item>
            <el-menu-item index="/teacher/courses">
              <el-icon><document /></el-icon>
              <span>我的课程</span>
            </el-menu-item>
            <el-menu-item index="/teacher/attendance">
              <el-icon><timer /></el-icon>
              <span>考勤管理</span>
            </el-menu-item>
            <el-menu-item index="/teacher/profile">
              <el-icon><user /></el-icon>
              <span>个人资料</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main>
          <div class="main-content">
            <h2>人脸识别考勤</h2>
            
            <el-card shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>选择课程</span>
                </div>
              </template>
              <el-form :model="formData" label-width="80px">
                <el-form-item label="课程">
                  <el-select v-model="formData.course_id" placeholder="请选择课程">
                    <el-option
                      v-for="course in courses"
                      :key="course.id"
                      :label="course.course_name"
                      :value="course.id"
                    >
                      {{ course.course_name }} ({{ course.course_code }})
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="考勤日期">
                  <el-date-picker
                    v-model="formData.attendance_date"
                    type="date"
                    placeholder="选择日期"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="startAttendance" :disabled="!formData.course_id || !formData.attendance_date">
                    开始考勤
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
            
            <el-card shadow="hover" class="mt-20" v-if="showAttendance">
              <template #header>
                <div class="card-header">
                  <span>人脸识别</span>
                  <el-button type="danger" @click="stopAttendance">停止考勤</el-button>
                </div>
              </template>
              
              <div class="camera-container">
                <video ref="videoElement" autoplay></video>
                <canvas ref="canvasElement" style="display: none;"></canvas>
                
                <div class="attendance-info" v-if="recognizedInfo">
                  <el-alert
                    :title="recognizedInfo.message"
                    :type="recognizedInfo.type"
                    show-icon
                  >
                    <template #desc>
                      <div v-if="recognizedInfo.student">
                        学生: {{ recognizedInfo.student.name }}<br>
                        学号: {{ recognizedInfo.student.student_id }}<br>
                        匹配度: {{ recognizedInfo.score }}%
                      </div>
                    </template>
                  </el-alert>
                </div>
              </div>
            </el-card>
            
            <el-card shadow="hover" class="mt-20">
              <template #header>
                <div class="card-header">
                  <span>今日考勤记录</span>
                  <el-button type="primary" @click="exportAttendance">导出Excel</el-button>
                </div>
              </template>
              <el-table :data="todayAttendance" style="width: 100%">
                <el-table-column prop="student_name" label="学生姓名" />
                <el-table-column prop="student_id" label="学号" />
                <el-table-column prop="time" label="签到时间" />
                <el-table-column prop="status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="match_score" label="匹配度" />
                <el-table-column prop="action" label="操作">
                  <template #default="{ row }">
                    <el-button type="primary" size="small" @click="editAttendance(row)">
                      编辑
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 编辑考勤对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑考勤记录"
      width="500px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="学生姓名">
          <el-input v-model="editForm.student_name" disabled />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option label="出勤" value="出勤" />
            <el-option label="迟到" value="迟到" />
            <el-option label="缺勤" value="缺勤" />
          </el-select>
        </el-form-item>
        <el-form-item label="签到时间">
          <el-time-picker
            v-model="editForm.time"
            placeholder="选择时间"
            format="HH:mm:ss"
            value-format="HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAttendance">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../../router'
import { Home, Document, Timer, User, ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'TeacherAttendance',
  components: {
    Home,
    Document,
    Timer,
    User,
    ArrowDown
  },
  data() {
    return {
      user: {},
      activeMenu: '/teacher/attendance',
      courses: [],
      formData: {
        course_id: '',
        attendance_date: ''
      },
      showAttendance: false,
      recognizedInfo: null,
      todayAttendance: [],
      dialogVisible: false,
      editForm: {
        id: '',
        student_name: '',
        status: '',
        time: '',
        remark: ''
      },
      recognitionInterval: null,
      mediaStream: null
    }
  },
  created() {
    this.user = JSON.parse(localStorage.getItem('user'))
    this.loadCourses()
    this.loadTodayAttendance()
    // 默认设置为今天
    const today = new Date()
    this.formData.attendance_date = today.toISOString().split('T')[0]
  },
  beforeUnmount() {
    this.stopAttendance()
  },
  methods: {
    async loadCourses() {
      try {
        const response = await axios.get('/teacher/courses')
        if (response.success) {
          this.courses = response.data
        }
      } catch (error) {
        console.error('Load courses error:', error)
        ElMessage.error('加载课程失败')
      }
    },
    
    async loadTodayAttendance() {
      try {
        const response = await axios.get('/teacher/attendance/today')
        if (response.success) {
          this.todayAttendance = response.data
        }
      } catch (error) {
        console.error('Load today attendance error:', error)
        ElMessage.error('加载考勤记录失败')
      }
    },
    
    async startAttendance() {
      try {
        // 获取摄像头权限
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
        const videoElement = this.$refs.videoElement
        videoElement.srcObject = this.mediaStream
        
        this.showAttendance = true
        ElMessage.success('考勤开始，请学生依次进行人脸识别')
        
        // 开始定期进行人脸识别
        this.recognitionInterval = setInterval(() => {
          this.recognizeFace()
        }, 5000) // 每5秒识别一次
      } catch (error) {
        console.error('Start attendance error:', error)
        ElMessage.error('无法访问摄像头，请确保已授权')
      }
    },
    
    stopAttendance() {
      if (this.recognitionInterval) {
        clearInterval(this.recognitionInterval)
        this.recognitionInterval = null
      }
      
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop())
        this.mediaStream = null
      }
      
      this.showAttendance = false
      this.recognizedInfo = null
      ElMessage.success('考勤已停止')
    },
    
    async recognizeFace() {
      try {
        const videoElement = this.$refs.videoElement
        const canvasElement = this.$refs.canvasElement
        const context = canvasElement.getContext('2d')
        
        // 设置canvas尺寸与video相同
        canvasElement.width = videoElement.videoWidth
        canvasElement.height = videoElement.videoHeight
        
        // 绘制当前视频帧到canvas
        context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height)
        
        // 将canvas转换为Blob
        canvasElement.toBlob(async (blob) => {
          const formData = new FormData()
          formData.append('face_image', blob, 'face.jpg')
          formData.append('course_id', this.formData.course_id)
          formData.append('date', this.formData.attendance_date)
          
          try {
            const response = await axios.post('/teacher/attendance/face-recognize', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
            
            if (response.success) {
              this.recognizedInfo = {
                message: response.message,
                type: 'success',
                student: response.data,
                score: response.data.match_score
              }
              this.loadTodayAttendance() // 刷新考勤记录
            } else {
              this.recognizedInfo = {
                message: response.message,
                type: 'warning'
              }
            }
            
            // 3秒后清除提示
            setTimeout(() => {
              this.recognizedInfo = null
            }, 3000)
          } catch (error) {
            console.error('Face recognition error:', error)
          }
        }, 'image/jpeg')
      } catch (error) {
        console.error('Capture image error:', error)
      }
    },
    
    getStatusType(status) {
      switch (status) {
        case '出勤':
          return 'success'
        case '缺勤':
          return 'danger'
        case '迟到':
          return 'warning'
        default:
          return 'info'
      }
    },
    
    editAttendance(row) {
      this.editForm = {
        id: row.id,
        student_name: row.student_name,
        status: row.status,
        time: row.time,
        remark: row.remark || ''
      }
      this.dialogVisible = true
    },
    
    async saveAttendance() {
      try {
        const response = await axios.put('/teacher/attendance/update', {
          id: this.editForm.id,
          status: this.editForm.status,
          time: this.editForm.time,
          remark: this.editForm.remark
        })
        
        if (response.success) {
          ElMessage.success('修改成功')
          this.dialogVisible = false
          this.loadTodayAttendance()
        } else {
          ElMessage.error(response.message || '修改失败')
        }
      } catch (error) {
        console.error('Update attendance error:', error)
        ElMessage.error('修改失败')
      }
    },
    
    async exportAttendance() {
      try {
        const response = await axios.get('/teacher/attendance/export', {
          params: {
            course_id: this.formData.course_id,
            date: this.formData.attendance_date
          },
          responseType: 'blob'
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `考勤记录_${this.formData.attendance_date}.xlsx`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        ElMessage.success('导出成功')
      } catch (error) {
        console.error('Export attendance error:', error)
        ElMessage.error('导出失败')
      }
    },
    
    toProfile() {
      router.push('/teacher/profile')
    },
    
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      ElMessage.success('退出登录成功')
    }
  }
}
</script>

<style scoped>
.attendance-container {
  height: 100vh;
  overflow: hidden;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  color: white;
  margin: 0;
  font-size: 24px;
}

.user-info {
  color: white;
  cursor: pointer;
  font-size: 16px;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

.main-content h2 {
  margin-bottom: 20px;
  color: #303133;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.camera-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

video {
  width: 100%;
  max-width: 600px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.attendance-info {
  width: 100%;
  max-width: 600px;
  margin-top: 20px;
}
</style>