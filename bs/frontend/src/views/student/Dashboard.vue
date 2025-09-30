<template>
  <div class="dashboard-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>互联网课堂考勤系统 - 学生端</h1>
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
            <el-menu-item index="/student/dashboard">
              <el-icon><home /></el-icon>
              <span>仪表板</span>
            </el-menu-item>
            <el-menu-item index="/student/courses">
              <el-icon><document /></el-icon>
              <span>我的课程</span>
            </el-menu-item>
            <el-menu-item index="/student/attendance">
              <el-icon><timer /></el-icon>
              <span>考勤记录</span>
            </el-menu-item>
            <el-menu-item index="/student/profile">
              <el-icon><user /></el-icon>
              <span>个人资料</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main>
          <div class="main-content">
            <h2>欢迎，{{ user.name }}</h2>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon"><document /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ courseCount }}</div>
                      <div class="card-label">已选课程</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon success"><check /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ attendanceStats.present }}</div>
                      <div class="card-label">出勤次数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon warning"><warning /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ attendanceStats.absent }}</div>
                      <div class="card-label">缺勤次数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <el-card class="mt-20">
              <template #header>
                <div class="card-header">
                  <span>最近考勤记录</span>
                </div>
              </template>
              <el-table :data="recentAttendance" style="width: 100%">
                <el-table-column prop="course_name" label="课程名称" />
                <el-table-column prop="date" label="日期" />
                <el-table-column prop="time" label="签到时间" />
                <el-table-column prop="status" label="状态">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../../router'
import { Home, Document, Timer, User, ArrowDown, Check, Warning } from '@element-plus/icons-vue'

export default {
  name: 'StudentDashboard',
  components: {
    Home,
    Document,
    Timer,
    User,
    ArrowDown,
    Check,
    Warning
  },
  data() {
    return {
      user: {},
      activeMenu: '/student/dashboard',
      courseCount: 0,
      attendanceStats: {
        present: 0,
        absent: 0
      },
      recentAttendance: []
    }
  },
  created() {
    this.user = JSON.parse(localStorage.getItem('user'))
    this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        // 获取课程数量
        const coursesRes = await axios.get('/student/courses')
        if (coursesRes.success) {
          this.courseCount = coursesRes.data.length
        }
        
        // 获取考勤统计
        const statsRes = await axios.get('/student/attendance/stats')
        if (statsRes.success) {
          this.attendanceStats = statsRes.data
        }
        
        // 获取最近考勤记录
        const attendanceRes = await axios.get('/student/attendance?limit=5')
        if (attendanceRes.success) {
          this.recentAttendance = attendanceRes.data
        }
      } catch (error) {
        console.error('Load dashboard data error:', error)
        ElMessage.error('加载数据失败')
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
    toProfile() {
      router.push('/student/profile')
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
.dashboard-container {
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
}

.main-content h2 {
  margin-bottom: 20px;
  color: #303133;
}

.card-item {
  display: flex;
  align-items: center;
}

.card-icon {
  font-size: 48px;
  color: #409eff;
  margin-right: 20px;
}

.card-icon.success {
  color: #67c23a;
}

.card-icon.warning {
  color: #e6a23c;
}

.card-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.card-label {
  color: #909399;
  margin-top: 5px;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>