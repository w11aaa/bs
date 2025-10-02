<template>
  <div class="courses-container">
    <h2>课程管理</h2>
    
    <div class="action-bar">
      <el-button type="primary" @click="openCourseDialog()">创建新课程</el-button>
    </div>
    
    <el-table :data="courses" style="width: 100%" v-loading="loading">
      <el-table-column prop="course_name" label="课程名称" />
      <el-table-column prop="course_code" label="课程代码" />
      <el-table-column prop="category" label="课程类别" />
      <el-table-column prop="credit" label="学分" width="80" />
      <el-table-column prop="capacity" label="容量" width="80" />
      <el-table-column prop="enrolled_count" label="已选人数" width="100" />
      <el-table-column prop="schedule" label="上课时间" />
      <el-table-column prop="location" label="上课地点" />
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openCourseDialog(row)">编辑</el-button>
          <el-button type="success" size="small" @click="viewStudents(row.id)">学生名单</el-button>
          <el-button type="info" size="small" @click="manageAttendance(row.id)">考勤管理</el-button>
          <el-button type="danger" size="small" @click="deleteCourse(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 课程表单对话框 -->
    <el-dialog
      v-model="courseDialogVisible"
      :title="isEdit ? '编辑课程' : '创建课程'"
      width="600px"
    >
      <el-form
        :model="courseForm"
        :rules="courseRules"
        ref="courseFormRef"
        label-width="100px"
      >
        <el-form-item label="课程名称" prop="course_name">
          <el-input v-model="courseForm.course_name" />
        </el-form-item>
        
        <el-form-item label="课程代码" prop="course_code">
          <el-input v-model="courseForm.course_code" />
        </el-form-item>
        
        <el-form-item label="课程类别" prop="category_id">
          <el-select v-model="courseForm.category_id" placeholder="选择课程类别">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="学分" prop="credit">
          <el-input-number v-model="courseForm.credit" :min="0.5" :max="10" :step="0.5" />
        </el-form-item>
        
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="courseForm.capacity" :min="1" :max="500" />
        </el-form-item>
        
        <el-form-item label="上课时间" prop="schedule">
          <el-input v-model="courseForm.schedule" placeholder="例如：周一 8:00-10:00" />
        </el-form-item>
        
        <el-form-item label="上课地点" prop="location">
          <el-input v-model="courseForm.location" />
        </el-form-item>
        
        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="courseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCourseForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 学生名单对话框 -->
    <el-dialog
      v-model="studentsDialogVisible"
      title="课程学生名单"
      width="800px"
    >
      <div class="dialog-header" v-if="selectedCourse">
        <h3>{{ selectedCourse.course_name }}</h3>
        <p>已选人数: {{ enrolledStudents.length }} / {{ selectedCourse.capacity }}</p>
      </div>
      
      <el-table :data="enrolledStudents" style="width: 100%" v-loading="studentsLoading">
        <el-table-column prop="student_id" label="学号" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="major" label="专业" />
        <el-table-column prop="class_name" label="班级" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="removeStudent(row.id)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="export-section">
        <el-button type="primary" @click="exportStudentList">导出学生名单</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'TeacherCourses',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const courses = ref([])
    const categories = ref([])
    const courseDialogVisible = ref(false)
    const studentsDialogVisible = ref(false)
    const studentsLoading = ref(false)
    const enrolledStudents = ref([])
    const selectedCourse = ref(null)
    const isEdit = ref(false)
    const courseFormRef = ref(null)
    
    // 课程表单
    const courseForm = reactive({
      id: null,
      course_name: '',
      course_code: '',
      category_id: null,
      credit: 2,
      capacity: 50,
      schedule: '',
      location: '',
      description: ''
    })
    
    // 表单验证规则
    const courseRules = {
      course_name: [
        { required: true, message: '请输入课程名称', trigger: 'blur' }
      ],
      course_code: [
        { required: true, message: '请输入课程代码', trigger: 'blur' }
      ],
      category_id: [
        { required: true, message: '请选择课程类别', trigger: 'change' }
      ],
      credit: [
        { required: true, message: '请输入学分', trigger: 'blur' }
      ],
      capacity: [
        { required: true, message: '请输入容量', trigger: 'blur' }
      ],
      schedule: [
        { required: true, message: '请输入上课时间', trigger: 'blur' }
      ],
      location: [
        { required: true, message: '请输入上课地点', trigger: 'blur' }
      ]
    }
    
    // 加载课程列表
    const loadCourses = async () => {
      loading.value = true
      try {
        const res = await axios.get('/teacher/courses')
        courses.value = res.data || []
      } catch (error) {
        console.error('加载课程失败:', error)
        ElMessage.error('加载课程失败')
      } finally {
        loading.value = false
      }
    }
    
    // 加载课程类别
    const loadCategories = async () => {
      try {
        const res = await axios.get('/course/categories')
        categories.value = res.data || []
      } catch (error) {
        console.error('加载课程类别失败:', error)
        ElMessage.error('加载课程类别失败')
      }
    }
    
    // 打开课程对话框
    const openCourseDialog = (course = null) => {
      if (course) {
        isEdit.value = true
        Object.assign(courseForm, course)
      } else {
        isEdit.value = false
        resetCourseForm()
      }
      courseDialogVisible.value = true
    }
    
    // 重置课程表单
    const resetCourseForm = () => {
      courseForm.id = null
      courseForm.course_name = ''
      courseForm.course_code = ''
      courseForm.category_id = null
      courseForm.credit = 2
      courseForm.capacity = 50
      courseForm.schedule = ''
      courseForm.location = ''
      courseForm.description = ''
    }
    
    // 提交课程表单
    const submitCourseForm = async () => {
      if (!courseFormRef.value) return
      
      await courseFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            if (isEdit.value) {
              await axios.put(`/teacher/courses/${courseForm.id}`, courseForm)
              ElMessage.success('课程更新成功')
            } else {
              await axios.post('/teacher/courses', courseForm)
              ElMessage.success('课程创建成功')
            }
            
            courseDialogVisible.value = false
            loadCourses()
          } catch (error) {
            console.error('保存课程失败:', error)
            ElMessage.error(error.response?.data?.message || '保存课程失败')
          }
        }
      })
    }
    
    // 删除课程
    const deleteCourse = async (courseId) => {
      try {
        await ElMessageBox.confirm('确定要删除该课程吗？删除后将无法恢复。', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await axios.delete(`/teacher/courses/${courseId}`)
        ElMessage.success('课程删除成功')
        loadCourses()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除课程失败:', error)
          ElMessage.error(error.response?.data?.message || '删除课程失败')
        }
      }
    }
    
    // 查看学生名单
    const viewStudents = async (courseId) => {
      studentsLoading.value = true
      studentsDialogVisible.value = true
      
      try {
        // 获取课程信息
        const courseRes = await axios.get(`/teacher/courses/${courseId}`)
        selectedCourse.value = courseRes.data
        
        // 获取已选学生名单
        const studentsRes = await axios.get(`/teacher/courses/${courseId}/students`)
        enrolledStudents.value = studentsRes.data || []
      } catch (error) {
        console.error('加载学生名单失败:', error)
        ElMessage.error('加载学生名单失败')
      } finally {
        studentsLoading.value = false
      }
    }
    
    // 移除学生
    const removeStudent = async (studentId) => {
      if (!selectedCourse.value) return
      
      try {
        await ElMessageBox.confirm('确定要将该学生从课程中移除吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await axios.post(`/teacher/courses/${selectedCourse.value.id}/remove-student`, {
          student_id: studentId
        })
        
        ElMessage.success('学生移除成功')
        // 重新加载学生名单
        viewStudents(selectedCourse.value.id)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('移除学生失败:', error)
          ElMessage.error(error.response?.data?.message || '移除学生失败')
        }
      }
    }
    
    // 导出学生名单
    const exportStudentList = async () => {
      if (!selectedCourse.value) return
      
      try {
        const res = await axios.get(`/teacher/courses/${selectedCourse.value.id}/export-students`, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${selectedCourse.value.course_name}-学生名单.xlsx`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('导出学生名单失败:', error)
        ElMessage.error('导出学生名单失败')
      }
    }
    
    // 考勤管理
    const manageAttendance = (courseId) => {
      router.push({
        path: '/teacher/attendance',
        query: { course_id: courseId }
      })
    }
    
    onMounted(() => {
      loadCourses()
      loadCategories()
    })
    
    return {
      loading,
      courses,
      categories,
      courseDialogVisible,
      studentsDialogVisible,
      studentsLoading,
      enrolledStudents,
      selectedCourse,
      isEdit,
      courseForm,
      courseRules,
      courseFormRef,
      openCourseDialog,
      submitCourseForm,
      deleteCourse,
      viewStudents,
      removeStudent,
      exportStudentList,
      manageAttendance
    }
  }
}
</script>

<style scoped>
.courses-container {
  padding: 20px;
}

.action-bar {
  margin-bottom: 20px;
}

.dialog-header {
  margin-bottom: 20px;
}

.dialog-header h3 {
  margin: 0 0 10px 0;
}

.dialog-header p {
  margin: 0;
  color: #606266;
}

.export-section {
  margin-top: 20px;
  text-align: right;
}
</style>