<template>
  <div class="admin-attendance-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>考勤记录管理</h2>
          <div class="header-actions">
            <el-button type="primary" @click="exportAttendance">导出考勤数据</el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索和筛选区域 -->
      <div class="filter-container">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-select v-model="filterCourse" placeholder="选择课程" clearable @change="handleSearch">
              <el-option
                v-for="course in courseOptions"
                :key="course.id"
                :label="course.name"
                :value="course.id"
              />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="filterStatus" placeholder="考勤状态" clearable @change="handleSearch">
              <el-option label="出席" value="present" />
              <el-option label="缺席" value="absent" />
              <el-option label="迟到" value="late" />
              <el-option label="请假" value="leave" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleSearch"
            />
          </el-col>
          <el-col :span="4">
            <el-input
              v-model="searchQuery"
              placeholder="搜索学生姓名/学号"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch"></el-button>
              </template>
            </el-input>
          </el-col>
        </el-row>
      </div>
      
      <!-- 考勤统计卡片 -->
      <div class="stats-container" v-if="showStats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-value">{{ stats.totalRecords || 0 }}</div>
              <div class="stat-label">总记录数</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card present">
              <div class="stat-value">{{ stats.presentCount || 0 }}</div>
              <div class="stat-label">出席人次</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card absent">
              <div class="stat-value">{{ stats.absentCount || 0 }}</div>
              <div class="stat-label">缺席人次</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="stat-card late">
              <div class="stat-value">{{ stats.lateCount || 0 }}</div>
              <div class="stat-label">迟到人次</div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 考勤记录列表 -->
      <el-table
        v-loading="loading"
        :data="attendanceRecords"
        style="width: 100%; margin-top: 20px"
        border
      >
        <el-table-column prop="date" label="日期" width="120" sortable />
        <el-table-column prop="time" label="时间" width="100" />
        <el-table-column prop="courseName" label="课程" width="180" />
        <el-table-column prop="studentId" label="学号" width="120" />
        <el-table-column prop="studentName" label="学生姓名" width="120" />
        <el-table-column prop="teacherName" label="授课教师" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除此考勤记录吗？"
              @confirm="deleteRecord(scope.row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 编辑考勤记录对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑考勤记录"
      width="40%"
    >
      <el-form
        ref="recordFormRef"
        :model="recordForm"
        :rules="recordRules"
        label-width="100px"
      >
        <el-form-item label="学生" prop="studentName">
          <el-input v-model="recordForm.studentName" disabled />
        </el-form-item>
        <el-form-item label="课程" prop="courseName">
          <el-input v-model="recordForm.courseName" disabled />
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-input v-model="recordForm.date" disabled />
        </el-form-item>
        <el-form-item label="时间" prop="time">
          <el-input v-model="recordForm.time" disabled />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="recordForm.status" placeholder="选择考勤状态">
            <el-option label="出席" value="present" />
            <el-option label="缺席" value="absent" />
            <el-option label="迟到" value="late" />
            <el-option label="请假" value="leave" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="note">
          <el-input v-model="recordForm.note" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRecordForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 数据加载状态
const loading = ref(false)

// 考勤记录数据
const attendanceRecords = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 搜索和筛选
const searchQuery = ref('')
const filterCourse = ref('')
const filterStatus = ref('')
const dateRange = ref([])
const courseOptions = ref([])

// 统计数据
const stats = ref({
  totalRecords: 0,
  presentCount: 0,
  absentCount: 0,
  lateCount: 0
})

// 是否显示统计信息
const showStats = computed(() => {
  return filterCourse.value || (dateRange.value && dateRange.value.length === 2)
})

// 对话框显示状态
const editDialogVisible = ref(false)

// 考勤记录表单
const recordFormRef = ref(null)
const recordForm = reactive({
  id: '',
  studentName: '',
  courseName: '',
  date: '',
  time: '',
  status: '',
  note: ''
})

// 表单验证规则
const recordRules = {
  status: [
    { required: true, message: '请选择考勤状态', trigger: 'change' }
  ]
}

// 生命周期钩子
onMounted(() => {
  loadAttendanceRecords()
  loadCourses()
})

// 加载考勤记录
const loadAttendanceRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value,
      search: searchQuery.value,
      courseId: filterCourse.value,
      status: filterStatus.value,
      startDate: dateRange.value && dateRange.value.length > 0 ? dateRange.value[0] : null,
      endDate: dateRange.value && dateRange.value.length > 1 ? dateRange.value[1] : null
    }
    
    const response = await axios.get('/admin/attendance', { params })
    attendanceRecords.value = response.data.records
    total.value = response.data.total
    
    // 如果有筛选条件，加载统计数据
    if (showStats.value) {
      loadAttendanceStats()
    }
  } catch (error) {
    console.error('加载考勤记录失败:', error)
    ElMessage.error('加载考勤记录失败')
  } finally {
    loading.value = false
  }
}

// 加载考勤统计
const loadAttendanceStats = async () => {
  try {
    const params = {
      courseId: filterCourse.value,
      startDate: dateRange.value && dateRange.value.length > 0 ? dateRange.value[0] : null,
      endDate: dateRange.value && dateRange.value.length > 1 ? dateRange.value[1] : null
    }
    
    const response = await axios.get('/admin/attendance/stats', { params })
    stats.value = response.data
  } catch (error) {
    console.error('加载考勤统计失败:', error)
  }
}

// 加载课程列表
const loadCourses = async () => {
  try {
    const response = await axios.get('/admin/courses/all')
    courseOptions.value = response.data.map(course => ({
      id: course.id,
      name: course.name
    }))
  } catch (error) {
    console.error('加载课程列表失败:', error)
    ElMessage.error('加载课程列表失败')
  }
}

// 获取考勤状态类型
const getStatusType = (status) => {
  switch (status) {
    case 'present':
      return 'success'
    case 'absent':
      return 'danger'
    case 'late':
      return 'warning'
    case 'leave':
      return 'info'
    default:
      return ''
  }
}

// 获取考勤状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'present':
      return '出席'
    case 'absent':
      return '缺席'
    case 'late':
      return '迟到'
    case 'leave':
      return '请假'
    default:
      return '未知'
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  loadAttendanceRecords()
}

// 处理分页大小变化
const handleSizeChange = (val) => {
  pageSize.value = val
  loadAttendanceRecords()
}

// 处理页码变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  loadAttendanceRecords()
}

// 显示编辑对话框
const showEditDialog = (record) => {
  Object.keys(recordForm).forEach(key => {
    recordForm[key] = record[key]
  })
  editDialogVisible.value = true
}

// 提交考勤记录表单
const submitRecordForm = async () => {
  if (!recordFormRef.value) return
  
  await recordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await axios.put(`/admin/attendance/${recordForm.id}`, {
          status: recordForm.status,
          note: recordForm.note
        })
        ElMessage.success('考勤记录更新成功')
        editDialogVisible.value = false
        loadAttendanceRecords()
      } catch (error) {
        console.error('更新考勤记录失败:', error)
        ElMessage.error('更新考勤记录失败')
      }
    }
  })
}

// 删除考勤记录
const deleteRecord = async (recordId) => {
  try {
    await axios.delete(`/admin/attendance/${recordId}`)
    ElMessage.success('考勤记录删除成功')
    loadAttendanceRecords()
  } catch (error) {
    console.error('删除考勤记录失败:', error)
    ElMessage.error('删除考勤记录失败')
  }
}

// 导出考勤数据
const exportAttendance = async () => {
  try {
    const params = {
      search: searchQuery.value,
      courseId: filterCourse.value,
      status: filterStatus.value,
      startDate: dateRange.value && dateRange.value.length > 0 ? dateRange.value[0] : null,
      endDate: dateRange.value && dateRange.value.length > 1 ? dateRange.value[1] : null
    }
    
    const response = await axios.get('/admin/attendance/export', {
      params,
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '考勤记录.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('考勤数据导出成功')
  } catch (error) {
    console.error('导出考勤数据失败:', error)
    ElMessage.error('导出考勤数据失败')
  }
}
</script>

<style scoped>
.admin-attendance-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-container {
  margin-bottom: 20px;
}

.stats-container {
  margin: 20px 0;
}

.stat-card {
  text-align: center;
  padding: 15px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-label {
  margin-top: 5px;
  color: #606266;
}

.present .stat-value {
  color: #67c23a;
}

.absent .stat-value {
  color: #f56c6c;
}

.late .stat-value {
  color: #e6a23c;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>