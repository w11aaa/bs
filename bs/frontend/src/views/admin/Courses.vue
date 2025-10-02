<template>
  <div class="admin-courses-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>课程管理</h2>
          <div class="header-actions">
            <el-button type="primary" @click="showAddCourseDialog">添加课程</el-button>
            <el-button type="success" @click="showImportDialog">批量导入</el-button>
            <el-button type="info" @click="exportCourses">导出课程</el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索和筛选区域 -->
      <div class="filter-container">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchQuery"
              placeholder="搜索课程名称或编号"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch"></el-button>
              </template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-select v-model="filterCategory" placeholder="课程类别" clearable @change="handleSearch">
              <el-option
                v-for="item in categoryOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="filterStatus" placeholder="课程状态" clearable @change="handleSearch">
              <el-option label="进行中" value="active" />
              <el-option label="已结束" value="ended" />
              <el-option label="未开始" value="pending" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="filterTeacher" placeholder="授课教师" clearable @change="handleSearch">
              <el-option
                v-for="teacher in teacherOptions"
                :key="teacher.id"
                :label="teacher.name"
                :value="teacher.id"
              />
            </el-select>
          </el-col>
        </el-row>
      </div>
      
      <!-- 课程列表 -->
      <el-table
        v-loading="loading"
        :data="courses"
        style="width: 100%; margin-top: 20px"
        border
      >
        <el-table-column prop="courseCode" label="课程编号" width="120" />
        <el-table-column prop="name" label="课程名称" width="180" />
        <el-table-column prop="category" label="课程类别" width="120" />
        <el-table-column prop="teacherName" label="授课教师" width="120" />
        <el-table-column prop="credits" label="学分" width="80" />
        <el-table-column prop="capacity" label="容量" width="80" />
        <el-table-column prop="enrolled" label="已选人数" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button size="small" @click="showEditCourseDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="primary" @click="viewStudents(scope.row)">查看学生</el-button>
            <el-popconfirm
              title="确定要删除此课程吗？"
              @confirm="deleteCourse(scope.row.id)"
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
    
    <!-- 添加/编辑课程对话框 -->
    <el-dialog
      v-model="courseDialogVisible"
      :title="isEditing ? '编辑课程' : '添加课程'"
      width="50%"
    >
      <el-form
        ref="courseFormRef"
        :model="courseForm"
        :rules="courseRules"
        label-width="100px"
      >
        <el-form-item label="课程编号" prop="courseCode">
          <el-input v-model="courseForm.courseCode" />
        </el-form-item>
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="courseForm.name" />
        </el-form-item>
        <el-form-item label="课程类别" prop="categoryId">
          <el-select v-model="courseForm.categoryId" placeholder="选择课程类别">
            <el-option
              v-for="item in categoryOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="授课教师" prop="teacherId">
          <el-select v-model="courseForm.teacherId" placeholder="选择授课教师">
            <el-option
              v-for="teacher in teacherOptions"
              :key="teacher.id"
              :label="teacher.name"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学分" prop="credits">
          <el-input-number v-model="courseForm.credits" :min="0" :max="10" />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="courseForm.capacity" :min="1" :max="500" />
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
          <el-input v-model="courseForm.description" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="开始日期" prop="startDate">
          <el-date-picker
            v-model="courseForm.startDate"
            type="date"
            placeholder="选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="endDate">
          <el-date-picker
            v-model="courseForm.endDate"
            type="date"
            placeholder="选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="courseForm.status" placeholder="选择课程状态">
            <el-option label="进行中" value="active" />
            <el-option label="已结束" value="ended" />
            <el-option label="未开始" value="pending" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="courseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCourseForm">确认</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 查看学生对话框 -->
    <el-dialog
      v-model="studentsDialogVisible"
      title="课程学生列表"
      width="70%"
    >
      <div v-if="currentCourse" class="course-info">
        <h3>{{ currentCourse.name }} ({{ currentCourse.courseCode }})</h3>
        <p>授课教师: {{ currentCourse.teacherName }} | 已选人数: {{ currentCourse.enrolled }}/{{ currentCourse.capacity }}</p>
      </div>
      
      <div class="student-search">
        <el-input
          v-model="studentSearchQuery"
          placeholder="搜索学生姓名或学号"
          clearable
          @clear="searchStudents"
          @keyup.enter="searchStudents"
        >
          <template #append>
            <el-button :icon="Search" @click="searchStudents"></el-button>
          </template>
        </el-input>
      </div>
      
      <el-table
        v-loading="studentsLoading"
        :data="courseStudents"
        style="width: 100%; margin-top: 20px"
        border
      >
        <el-table-column prop="studentId" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="scope">
            {{ scope.row.gender === 'male' ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column prop="major" label="专业" width="150" />
        <el-table-column prop="class" label="班级" width="120" />
        <el-table-column prop="enrollDate" label="选课日期" width="120" />
        <el-table-column label="出勤率" width="100">
          <template #default="scope">
            {{ scope.row.attendanceRate || '0' }}%
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-popconfirm
              title="确定要将此学生从课程中移除吗？"
              @confirm="removeStudentFromCourse(scope.row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">移除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="student-pagination">
        <el-pagination
          v-model:current-page="studentCurrentPage"
          v-model:page-size="studentPageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          :total="studentTotal"
          @size-change="handleStudentSizeChange"
          @current-change="handleStudentCurrentChange"
        />
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportStudentList">导出学生名单</el-button>
          <el-button type="primary" @click="studentsDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入课程"
      width="50%"
    >
      <div class="import-container">
        <el-alert
          title="请使用指定格式的Excel文件进行导入"
          type="info"
          description="文件应包含以下列：课程编号、课程名称、课程类别ID、教师ID、学分、容量、描述、开始日期、结束日期、状态"
          show-icon
          :closable="false"
        />
        
        <div class="import-actions">
          <el-button type="primary" @click="downloadTemplate">下载导入模板</el-button>
          <el-upload
            class="upload-demo"
            action="/api/admin/courses/import"
            :headers="uploadHeaders"
            :on-success="handleImportSuccess"
            :on-error="handleImportError"
            :before-upload="beforeImportUpload"
            accept=".xlsx, .xls"
          >
            <el-button type="success">选择文件并上传</el-button>
          </el-upload>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 数据加载状态
const loading = ref(false)
const studentsLoading = ref(false)

// 课程列表数据
const courses = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 学生列表数据
const courseStudents = ref([])
const studentTotal = ref(0)
const studentCurrentPage = ref(1)
const studentPageSize = ref(10)
const studentSearchQuery = ref('')
const currentCourse = ref(null)

// 搜索和筛选
const searchQuery = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const filterTeacher = ref('')

// 选项数据
const categoryOptions = ref([])
const teacherOptions = ref([])

// 对话框显示状态
const courseDialogVisible = ref(false)
const studentsDialogVisible = ref(false)
const importDialogVisible = ref(false)
const isEditing = ref(false)

// 课程表单
const courseFormRef = ref(null)
const courseForm = reactive({
  id: '',
  courseCode: '',
  name: '',
  categoryId: '',
  teacherId: '',
  credits: 3,
  capacity: 50,
  description: '',
  startDate: '',
  endDate: '',
  status: 'pending'
})

// 表单验证规则
const courseRules = {
  courseCode: [
    { required: true, message: '请输入课程编号', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  categoryId: [
    { required: true, message: '请选择课程类别', trigger: 'change' }
  ],
  teacherId: [
    { required: true, message: '请选择授课教师', trigger: 'change' }
  ],
  credits: [
    { required: true, message: '请输入学分', trigger: 'blur' }
  ],
  capacity: [
    { required: true, message: '请输入容量', trigger: 'blur' }
  ],
  startDate: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  endDate: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择课程状态', trigger: 'change' }
  ]
}

// 上传文件的请求头
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

// 生命周期钩子
onMounted(() => {
  loadCourses()
  loadCategories()
  loadTeachers()
})

// 加载课程列表
const loadCourses = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value,
      search: searchQuery.value,
      category: filterCategory.value,
      status: filterStatus.value,
      teacherId: filterTeacher.value
    }
    
    const response = await axios.get('/admin/courses', { params })
    courses.value = response.data.courses
    total.value = response.data.total
  } catch (error) {
    console.error('加载课程失败:', error)
    ElMessage.error('加载课程列表失败')
  } finally {
    loading.value = false
  }
}

// 加载课程类别
const loadCategories = async () => {
  try {
    const response = await axios.get('/course/categories')
    categoryOptions.value = response.data.map(category => ({
      value: category.id,
      label: category.name
    }))
  } catch (error) {
    console.error('加载课程类别失败:', error)
    ElMessage.error('加载课程类别失败')
  }
}

// 加载教师列表
const loadTeachers = async () => {
  try {
    const response = await axios.get('/admin/teachers')
    teacherOptions.value = response.data.map(teacher => ({
      id: teacher.id,
      name: teacher.name
    }))
  } catch (error) {
    console.error('加载教师列表失败:', error)
    ElMessage.error('加载教师列表失败')
  }
}

// 获取课程状态类型
const getStatusType = (status) => {
  switch (status) {
    case 'active':
      return 'success'
    case 'ended':
      return 'info'
    case 'pending':
      return 'warning'
    default:
      return ''
  }
}

// 获取课程状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'active':
      return '进行中'
    case 'ended':
      return '已结束'
    case 'pending':
      return '未开始'
    default:
      return '未知'
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  loadCourses()
}

// 处理分页大小变化
const handleSizeChange = (val) => {
  pageSize.value = val
  loadCourses()
}

// 处理页码变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  loadCourses()
}

// 显示添加课程对话框
const showAddCourseDialog = () => {
  isEditing.value = false
  Object.keys(courseForm).forEach(key => {
    if (key !== 'credits' && key !== 'capacity' && key !== 'status') {
      courseForm[key] = ''
    }
  })
  courseForm.credits = 3
  courseForm.capacity = 50
  courseForm.status = 'pending'
  courseDialogVisible.value = true
}

// 显示编辑课程对话框
const showEditCourseDialog = (course) => {
  isEditing.value = true
  Object.keys(courseForm).forEach(key => {
    courseForm[key] = course[key]
  })
  courseDialogVisible.value = true
}

// 提交课程表单
const submitCourseForm = async () => {
  if (!courseFormRef.value) return
  
  await courseFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditing.value) {
          await axios.put(`/admin/courses/${courseForm.id}`, courseForm)
          ElMessage.success('课程更新成功')
        } else {
          await axios.post('/admin/courses', courseForm)
          ElMessage.success('课程添加成功')
        }
        courseDialogVisible.value = false
        loadCourses()
      } catch (error) {
        console.error('保存课程失败:', error)
        ElMessage.error('保存课程失败')
      }
    }
  })
}

// 删除课程
const deleteCourse = async (courseId) => {
  try {
    await axios.delete(`/admin/courses/${courseId}`)
    ElMessage.success('课程删除成功')
    loadCourses()
  } catch (error) {
    console.error('删除课程失败:', error)
    ElMessage.error('删除课程失败')
  }
}

// 查看课程学生
const viewStudents = async (course) => {
  currentCourse.value = course
  studentCurrentPage.value = 1
  studentSearchQuery.value = ''
  studentsDialogVisible.value = true
  loadCourseStudents()
}

// 加载课程学生
const loadCourseStudents = async () => {
  if (!currentCourse.value) return
  
  studentsLoading.value = true
  try {
    const params = {
      page: studentCurrentPage.value,
      limit: studentPageSize.value,
      search: studentSearchQuery.value
    }
    
    const response = await axios.get(`/admin/courses/${currentCourse.value.id}/students`, { params })
    courseStudents.value = response.data.students
    studentTotal.value = response.data.total
  } catch (error) {
    console.error('加载课程学生失败:', error)
    ElMessage.error('加载课程学生列表失败')
  } finally {
    studentsLoading.value = false
  }
}

// 搜索学生
const searchStudents = () => {
  studentCurrentPage.value = 1
  loadCourseStudents()
}

// 处理学生分页大小变化
const handleStudentSizeChange = (val) => {
  studentPageSize.value = val
  loadCourseStudents()
}

// 处理学生页码变化
const handleStudentCurrentChange = (val) => {
  studentCurrentPage.value = val
  loadCourseStudents()
}

// 从课程中移除学生
const removeStudentFromCourse = async (studentId) => {
  try {
    await axios.delete(`/admin/courses/${currentCourse.value.id}/students/${studentId}`)
    ElMessage.success('学生已从课程中移除')
    loadCourseStudents()
    // 刷新课程列表以更新已选人数
    loadCourses()
  } catch (error) {
    console.error('移除学生失败:', error)
    ElMessage.error('移除学生失败')
  }
}

// 导出学生名单
const exportStudentList = async () => {
  try {
    const response = await axios.get(`/admin/courses/${currentCourse.value.id}/students/export`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${currentCourse.value.name}-学生名单.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('学生名单导出成功')
  } catch (error) {
    console.error('导出学生名单失败:', error)
    ElMessage.error('导出学生名单失败')
  }
}

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true
}

// 下载导入模板
const downloadTemplate = async () => {
  try {
    const response = await axios.get('/admin/courses/import/template', {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '课程导入模板.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('下载导入模板失败:', error)
    ElMessage.error('下载导入模板失败')
  }
}

// 导入前验证
const beforeImportUpload = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                  file.type === 'application/vnd.ms-excel'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isExcel) {
    ElMessage.error('只能上传Excel文件!')
  }
  if (!isLt2M) {
    ElMessage.error('文件大小不能超过2MB!')
  }
  return isExcel && isLt2M
}

// 导入成功处理
const handleImportSuccess = (response) => {
  ElMessage.success(`成功导入${response.imported}条课程数据`)
  importDialogVisible.value = false
  loadCourses()
}

// 导入失败处理
const handleImportError = (error) => {
  console.error('导入失败:', error)
  ElMessage.error('导入课程数据失败')
}

// 导出课程
const exportCourses = async () => {
  try {
    const params = {
      search: searchQuery.value,
      category: filterCategory.value,
      status: filterStatus.value,
      teacherId: filterTeacher.value
    }
    
    const response = await axios.get('/admin/courses/export', {
      params,
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '课程列表.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('课程列表导出成功')
  } catch (error) {
    console.error('导出课程列表失败:', error)
    ElMessage.error('导出课程列表失败')
  }
}
</script>

<style scoped>
.admin-courses-container {
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.course-info {
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.student-search {
  margin-bottom: 20px;
  max-width: 300px;
}

.student-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.import-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.import-actions {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}
</style>