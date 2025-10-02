<template>
  <div class="attendance-container">
    <h2>考勤记录</h2>
    
    <div class="filter-section">
      <el-select v-model="selectedCourse" placeholder="选择课程" clearable @change="loadAttendanceRecords">
        <el-option
          v-for="course in courses"
          :key="course.id"
          :label="course.course_name"
          :value="course.id"
        />
      </el-select>
      
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        @change="loadAttendanceRecords"
      />
    </div>
    
    <el-table :data="attendanceRecords" style="width: 100%" v-loading="loading">
      <el-table-column prop="course_name" label="课程名称" />
      <el-table-column prop="date" label="日期" sortable />
      <el-table-column prop="time" label="签到时间" sortable />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remarks" label="备注" />
    </el-table>
    
    <div class="empty-block" v-if="attendanceRecords.length === 0 && !loading">
      <el-empty description="暂无考勤记录" />
    </div>
    
    <div class="statistics-section" v-if="attendanceRecords.length > 0">
      <h3>考勤统计</h3>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="stat-label">出勤率</div>
              <div class="stat-value">{{ statistics.presentRate }}%</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="stat-label">缺勤次数</div>
              <div class="stat-value">{{ statistics.absentCount }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <div class="stat-item">
              <div class="stat-label">迟到次数</div>
              <div class="stat-value">{{ statistics.lateCount }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'StudentAttendance',
  setup() {
    const route = useRoute()
    const loading = ref(false)
    const courses = ref([])
    const selectedCourse = ref('')
    const dateRange = ref(null)
    const attendanceRecords = ref([])
    
    // 从路由参数中获取课程ID
    if (route.query.course_id) {
      selectedCourse.value = route.query.course_id
    }
    
    // 考勤统计
    const statistics = computed(() => {
      const total = attendanceRecords.value.length
      if (total === 0) return { presentRate: 0, absentCount: 0, lateCount: 0 }
      
      const absentCount = attendanceRecords.value.filter(record => record.status === '缺勤').length
      const lateCount = attendanceRecords.value.filter(record => record.status === '迟到').length
      const presentCount = total - absentCount - lateCount
      
      return {
        presentRate: Math.round((presentCount / total) * 100),
        absentCount,
        lateCount
      }
    })
    
    // 加载学生已选课程
    const loadCourses = async () => {
      try {
        const res = await axios.get('/student/courses')
        courses.value = res.data || []
      } catch (error) {
        console.error('加载课程失败:', error)
        ElMessage.error('加载课程失败')
      }
    }
    
    // 加载考勤记录
    const loadAttendanceRecords = async () => {
      loading.value = true
      try {
        let url = '/student/attendance'
        const params = {}
        
        if (selectedCourse.value) {
          params.course_id = selectedCourse.value
        }
        
        if (dateRange.value && dateRange.value.length === 2) {
          params.start_date = dateRange.value[0]
          params.end_date = dateRange.value[1]
        }
        
        const res = await axios.get(url, { params })
        attendanceRecords.value = res.data || []
      } catch (error) {
        console.error('加载考勤记录失败:', error)
        ElMessage.error('加载考勤记录失败')
      } finally {
        loading.value = false
      }
    }
    
    // 获取状态对应的标签类型
    const getStatusType = (status) => {
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
    }
    
    onMounted(() => {
      loadCourses()
      loadAttendanceRecords()
    })
    
    return {
      loading,
      courses,
      selectedCourse,
      dateRange,
      attendanceRecords,
      statistics,
      loadAttendanceRecords,
      getStatusType
    }
  }
}
</script>

<style scoped>
.attendance-container {
  padding: 20px;
}

.filter-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.empty-block {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}

.statistics-section {
  margin-top: 30px;
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-label {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}
</style>