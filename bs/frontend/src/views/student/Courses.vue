<template>
  <div class="courses-container">
    <h2>我的课程</h2>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane label="已选课程" name="enrolled">
        <el-table :data="enrolledCourses" style="width: 100%" v-loading="loading">
          <el-table-column prop="course_name" label="课程名称" />
          <el-table-column prop="teacher_name" label="授课教师" />
          <el-table-column prop="schedule" label="上课时间" />
          <el-table-column prop="location" label="上课地点" />
          <el-table-column prop="credit" label="学分" width="80" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="danger" size="small" @click="dropCourse(row.id)">退选</el-button>
              <el-button type="primary" size="small" @click="viewAttendance(row.id)">考勤记录</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="empty-block" v-if="enrolledCourses.length === 0 && !loading">
          <el-empty description="暂无已选课程" />
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="可选课程" name="available">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索课程名称或教师"
          prefix-icon="Search"
          clearable
          class="search-input"
        />
        
        <el-table :data="filteredAvailableCourses" style="width: 100%" v-loading="loading">
          <el-table-column prop="course_name" label="课程名称" />
          <el-table-column prop="teacher_name" label="授课教师" />
          <el-table-column prop="schedule" label="上课时间" />
          <el-table-column prop="location" label="上课地点" />
          <el-table-column prop="credit" label="学分" width="80" />
          <el-table-column prop="capacity" label="剩余名额" width="100">
            <template #default="{ row }">
              {{ row.capacity - row.enrolled_count }}/{{ row.capacity }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small" 
                @click="enrollCourse(row.id)"
                :disabled="row.capacity <= row.enrolled_count"
              >
                选课
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="empty-block" v-if="availableCourses.length === 0 && !loading">
          <el-empty description="暂无可选课程" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'StudentCourses',
  setup() {
    const router = useRouter()
    const activeTab = ref('enrolled')
    const enrolledCourses = ref([])
    const availableCourses = ref([])
    const loading = ref(false)
    const searchKeyword = ref('')
    
    // 过滤可选课程
    const filteredAvailableCourses = computed(() => {
      if (!searchKeyword.value) return availableCourses.value
      
      const keyword = searchKeyword.value.toLowerCase()
      return availableCourses.value.filter(course => 
        course.course_name.toLowerCase().includes(keyword) || 
        course.teacher_name.toLowerCase().includes(keyword)
      )
    })
    
    // 加载已选课程
    const loadEnrolledCourses = async () => {
      loading.value = true
      try {
        const res = await axios.get('/student/courses')
        enrolledCourses.value = res.data || []
      } catch (error) {
        console.error('加载已选课程失败:', error)
        ElMessage.error('加载已选课程失败')
      } finally {
        loading.value = false
      }
    }
    
    // 加载可选课程
    const loadAvailableCourses = async () => {
      loading.value = true
      try {
        const res = await axios.get('/student/courses/available')
        availableCourses.value = res.data || []
      } catch (error) {
        console.error('加载可选课程失败:', error)
        ElMessage.error('加载可选课程失败')
      } finally {
        loading.value = false
      }
    }
    
    // 选课
    const enrollCourse = async (courseId) => {
      try {
        await axios.post('/student/courses/enroll', { course_id: courseId })
        ElMessage.success('选课成功')
        // 重新加载课程列表
        loadEnrolledCourses()
        loadAvailableCourses()
      } catch (error) {
        console.error('选课失败:', error)
        ElMessage.error(error.response?.data?.message || '选课失败')
      }
    }
    
    // 退选课程
    const dropCourse = async (courseId) => {
      try {
        await ElMessageBox.confirm('确定要退选该课程吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await axios.post('/student/courses/drop', { course_id: courseId })
        ElMessage.success('退选成功')
        // 重新加载课程列表
        loadEnrolledCourses()
        loadAvailableCourses()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('退选失败:', error)
          ElMessage.error(error.response?.data?.message || '退选失败')
        }
      }
    }
    
    // 查看考勤记录
    const viewAttendance = (courseId) => {
      router.push({
        path: '/student/attendance',
        query: { course_id: courseId }
      })
    }
    
    onMounted(() => {
      loadEnrolledCourses()
      loadAvailableCourses()
    })
    
    return {
      activeTab,
      enrolledCourses,
      availableCourses,
      filteredAvailableCourses,
      loading,
      searchKeyword,
      enrollCourse,
      dropCourse,
      viewAttendance
    }
  }
}
</script>

<style scoped>
.courses-container {
  padding: 20px;
}

.search-input {
  margin-bottom: 20px;
  max-width: 400px;
}

.empty-block {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}
</style>