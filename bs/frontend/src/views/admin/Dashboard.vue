<template>
  <div class="dashboard-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>互联网课堂考勤系统 - 管理员端</h1>
          <el-dropdown>
            <span class="user-info">
              {{ user.name }} <el-icon><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
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
            <el-menu-item index="/admin/dashboard">
              <el-icon><home /></el-icon>
              <span>仪表板</span>
            </el-menu-item>
            <el-menu-item index="/admin/students">
              <el-icon><user /></el-icon>
              <span>学生管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/teachers">
              <el-icon><avatar /></el-icon>
              <span>教师管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/courses">
              <el-icon><document /></el-icon>
              <span>课程管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/attendance">
              <el-icon><timer /></el-icon>
              <span>考勤统计</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main>
          <div class="main-content">
            <h2>系统概览</h2>
            
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon"><user /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ stats.student_count }}</div>
                      <div class="card-label">学生总数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon"><avatar /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ stats.teacher_count }}</div>
                      <div class="card-label">教师总数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon"><document /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ stats.course_count }}</div>
                      <div class="card-label">课程总数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="card-item">
                    <el-icon class="card-icon"><timer /></el-icon>
                    <div class="card-content">
                      <div class="card-number">{{ stats.attendance_count }}</div>
                      <div class="card-label">考勤记录</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <el-row :gutter="20" class="mt-20">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <span>考勤状态分布</span>
                    </div>
                  </template>
                  <div class="chart-container">
                    <el-progress :percentage="attendanceDistribution.present_rate" type="line" :stroke-width="24" status="success" />
                    <div class="chart-legend">
                      <div class="legend-item">
                        <span class="legend-color success"></span>
                        <span>出勤: {{ attendanceDistribution.present }} ({{ attendanceDistribution.present_rate }}%)</span>
                      </div>
                      <div class="legend-item">
                        <span class="legend-color warning"></span>
                        <span>迟到: {{ attendanceDistribution.late }} ({{ attendanceDistribution.late_rate }}%)</span>
                      </div>
                      <div class="legend-item">
                        <span class="legend-color danger"></span>
                        <span>缺勤: {{ attendanceDistribution.absent }} ({{ attendanceDistribution.absent_rate }}%)</span>
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <span>课程分类统计</span>
                    </div>
                  </template>
                  <div class="category-stats">
                    <div v-for="category in categoryStats" :key="category.id" class="category-item">
                      <div class="category-name">{{ category.name }}</div>
                      <div class="category-count">{{ category.count }} 门</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
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
import { Home, User, Avatar, Document, Timer, ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'AdminDashboard',
  components: {
    Home,
    User,
    Avatar,
    Document,
    Timer,
    ArrowDown
  },
  data() {
    return {
      user: {},
      activeMenu: '/admin/dashboard',
      stats: {
        student_count: 0,
        teacher_count: 0,
        course_count: 0,
        attendance_count: 0
      },
      attendanceDistribution: {
        present: 0,
        late: 0,
        absent: 0,
        present_rate: 0,
        late_rate: 0,
        absent_rate: 0
      },
      categoryStats: []
    }
  },
  created() {
    this.user = JSON.parse(localStorage.getItem('user'))
    this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        // 获取系统统计信息
        const statsRes = await axios.get('/admin/system/stats')
        if (statsRes.success) {
          this.stats = statsRes.data
        }
        
        // 获取考勤分布
        const attendanceRes = await axios.get('/admin/attendance/distribution')
        if (attendanceRes.success) {
          this.attendanceDistribution = attendanceRes.data
        }
        
        // 获取课程分类统计
        const categoryRes = await axios.get('/admin/courses/categories/stats')
        if (categoryRes.success) {
          this.categoryStats = categoryRes.data.slice(0, 5)
        }
      } catch (error) {
        console.error('Load dashboard data error:', error)
        ElMessage.error('加载数据失败')
      }
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

.chart-container {
  padding: 20px 0;
}

.chart-legend {
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 8px;
}

.legend-color.success {
  background-color: #67c23a;
}

.legend-color.warning {
  background-color: #e6a23c;
}

.legend-color.danger {
  background-color: #f56c6c;
}

.category-stats {
  padding: 20px 0;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
}

.category-item:last-child {
  border-bottom: none;
}

.category-name {
  font-size: 16px;
  color: #303133;
}

.category-count {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}
</style>