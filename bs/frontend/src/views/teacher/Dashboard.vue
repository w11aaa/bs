<template>
  <div class="dashboard-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>互联网课堂考勤系统 - 教师端</h1>
          <el-dropdown>
            <span class="user-info">
              {{ user.name }} <el-icon><ArrowDown /></el-icon>
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
              <el-icon><Home /></el-icon>
              <span>仪表板</span>
            </el-menu-item>
            <el-menu-item index="/teacher/courses">
              <el-icon><Document /></el-icon>
              <span>我的课程</span>
            </el-menu-item>
            <el-menu-item index="/teacher/attendance">
              <el-icon><Timer /></el-icon>
              <span>考勤管理</span>
            </el-menu-item>
            <el-menu-item index="/teacher/profile">
              <el-icon><User /></el-icon>
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
                      <div class="card-label">教授课程</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon primary"><users /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ studentCount }}</div>
                      <div class="card-label">学生总数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon info"><timer /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ attendanceRecordCount }}</div>
                      <div class="card-label">考勤记录</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <el-card class="mt-20">
              <template #header>
                <div class="card-header">
                  <span>今日考勤统计</span>
                </div>
              </template>
              <div class="stats-container">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="stat-item">
                      <div class="stat-number">{{ todayStats.total }}</div>
                      <div class="stat-label">应出勤</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item success">
                      <div class="stat-number">{{ todayStats.present }}</div>
                      <div class="stat-label">已出勤</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item warning">
                      <div class="stat-number">{{ todayStats.late }}</div>
                      <div class="stat-label">迟到</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item danger">
                      <div class="stat-number">{{ todayStats.absent }}</div>
                      <div class="stat-label">缺勤</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-card>
            
            <el-card class="mt-20">
              <template #header>
                <div class="card-header">
                  <span>近期课程</span>
                </div>
              </template>
              <el-table :data="recentCourses" style="width: 100%">
                <el-table-column prop="course_name" label="课程名称" />
                <el-table-column prop="course_code" label="课程代码" />
                <el-table-column prop="student_count" label="学生人数" />
                <el-table-column prop="total_hours" label="总课时" />
                <el-table-column prop="action" label="操作">
                  <template #default="{ row }">
                    <el-button type="primary" size="small" @click="viewCourse(row.id)">
                      查看
                    </el-button>
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
// Element Plus 2.0+ 中图标已集成，不需要单独导入

export default {
  name: 'TeacherDashboard',
  components: {
    // 图标不需要在这里注册，Element Plus 2.0+ 直接使用 <el-icon><组件名 /></el-icon>
  },
  data() {
    return {
      user: {},
      activeMenu: '/teacher/dashboard',
      courseCount: 0,
      studentCount: 0,
      attendanceRecordCount: 0,
      todayStats: {
        total: 0,
        present: 0,
        late: 0,
        absent: 0
      },
      recentCourses: []
    }
  },
  created() {
    this.user = JSON.parse(localStorage.getItem('user'))
    this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        // 获取课程信息
        const coursesRes = await axios.get('/teacher/courses')
        if (coursesRes.success) {
          this.courseCount = coursesRes.data.length
          this.recentCourses = coursesRes.data.slice(0, 5)
          
          // 计算学生总数
          this.studentCount = coursesRes.data.reduce((sum, course) => sum + (course.student_count || 0), 0)
        }
        
        // 获取考勤统计
        const statsRes = await axios.get('/teacher/attendance/stats')
        if (statsRes.success) {
          this.attendanceRecordCount = statsRes.data.total_records
          this.todayStats = statsRes.data.today_stats
        }
      } catch (error) {
        console.error('Load dashboard data error:', error)
        ElMessage.error('加载数据失败')
      }
    },
    viewCourse(courseId) {
      this.$router.push(`/teacher/courses/${courseId}`)
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

.card-icon.primary {
  color: #67c23a;
}

.card-icon.info {
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

.stats-container {
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background-color: #f5f7fa;
}

.stat-item.success {
  background-color: #f0f9ff;
  color: #67c23a;
}

.stat-item.warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.stat-item.danger {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
}
</style>