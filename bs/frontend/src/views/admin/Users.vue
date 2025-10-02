<template>
  <div class="users-container">
    <h2>用户管理</h2>
    
    <div class="filter-section">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="用户类型">
          <el-select v-model="filterForm.role" placeholder="选择用户类型" @change="loadUsers">
            <el-option label="全部" value="" />
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.keyword"
            placeholder="姓名/ID/邮箱"
            clearable
            @keyup.enter="loadUsers"
          >
            <template #append>
              <el-button @click="loadUsers">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      
      <div class="action-buttons">
        <el-button type="primary" @click="openUserDialog()">添加用户</el-button>
        <el-button type="success" @click="openImportDialog">批量导入</el-button>
      </div>
    </div>
    
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="学生" name="student">
        <el-table :data="users" style="width: 100%" v-loading="loading">
          <el-table-column prop="student_id" label="学号" />
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="gender" label="性别" width="80" />
          <el-table-column prop="age" label="年龄" width="80" />
          <el-table-column prop="major" label="专业" />
          <el-table-column prop="class_name" label="班级" />
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="openUserDialog(row)">编辑</el-button>
              <el-button
                :type="row.status === 'active' ? 'danger' : 'success'"
                size="small"
                @click="toggleUserStatus(row)"
              >
                {{ row.status === 'active' ? '禁用' : '启用' }}
              </el-button>
              <el-button type="danger" size="small" @click="deleteUser(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="教师" name="teacher">
        <el-table :data="users" style="width: 100%" v-loading="loading">
          <el-table-column prop="teacher_id" label="工号" />
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="gender" label="性别" width="80" />
          <el-table-column prop="title" label="职称" />
          <el-table-column prop="department" label="院系" />
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="openUserDialog(row)">编辑</el-button>
              <el-button
                :type="row.status === 'active' ? 'danger' : 'success'"
                size="small"
                @click="toggleUserStatus(row)"
              >
                {{ row.status === 'active' ? '禁用' : '启用' }}
              </el-button>
              <el-button type="danger" size="small" @click="deleteUser(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="管理员" name="admin">
        <el-table :data="users" style="width: 100%" v-loading="loading">
          <el-table-column prop="admin_id" label="ID" />
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="openUserDialog(row)">编辑</el-button>
              <el-button
                :type="row.status === 'active' ? 'danger' : 'success'"
                size="small"
                @click="toggleUserStatus(row)"
              >
                {{ row.status === 'active' ? '禁用' : '启用' }}
              </el-button>
              <el-button type="danger" size="small" @click="deleteUser(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 用户表单对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="600px"
    >
      <el-form
        :model="userForm"
        :rules="userRules"
        ref="userFormRef"
        label-width="100px"
      >
        <el-form-item label="用户类型" prop="role" v-if="!isEdit">
          <el-select v-model="userForm.role" placeholder="选择用户类型">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userForm.name" />
        </el-form-item>
        
        <el-form-item :label="userIdLabel" prop="user_id" v-if="userForm.role !== 'admin' || isEdit">
          <el-input v-model="userForm.user_id" :disabled="isEdit" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        
        <template v-if="userForm.role === 'student'">
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="userForm.gender">
              <el-radio label="男">男</el-radio>
              <el-radio label="女">女</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="年龄" prop="age">
            <el-input-number v-model="userForm.age" :min="16" :max="100" />
          </el-form-item>
          
          <el-form-item label="专业" prop="major">
            <el-input v-model="userForm.major" />
          </el-form-item>
          
          <el-form-item label="班级" prop="class_name">
            <el-input v-model="userForm.class_name" />
          </el-form-item>
        </template>
        
        <template v-if="userForm.role === 'teacher'">
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="userForm.gender">
              <el-radio label="男">男</el-radio>
              <el-radio label="女">女</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="职称" prop="title">
            <el-select v-model="userForm.title" placeholder="选择职称">
              <el-option label="助教" value="助教" />
              <el-option label="讲师" value="讲师" />
              <el-option label="副教授" value="副教授" />
              <el-option label="教授" value="教授" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="院系" prop="department">
            <el-input v-model="userForm.department" />
          </el-form-item>
        </template>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUserForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入用户"
      width="500px"
    >
      <el-form
        :model="importForm"
        :rules="importRules"
        ref="importFormRef"
        label-width="100px"
      >
        <el-form-item label="用户类型" prop="role">
          <el-select v-model="importForm.role" placeholder="选择用户类型">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Excel文件" prop="file">
          <el-upload
            class="upload-demo"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".xlsx,.xls"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                请上传Excel文件，格式请参考<el-button type="text" @click="downloadTemplate">模板文件</el-button>
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="importUsers">导入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'AdminUsers',
  components: {
    Search
  },
  setup() {
    const loading = ref(false)
    const users = ref([])
    const activeTab = ref('student')
    const userDialogVisible = ref(false)
    const importDialogVisible = ref(false)
    const isEdit = ref(false)
    const userFormRef = ref(null)
    const importFormRef = ref(null)
    
    // 筛选表单
    const filterForm = reactive({
      role: '',
      keyword: ''
    })
    
    // 分页
    const pagination = reactive({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })
    
    // 用户表单
    const userForm = reactive({
      id: null,
      role: 'student',
      name: '',
      user_id: '',
      email: '',
      password: '',
      gender: '男',
      age: 18,
      major: '',
      class_name: '',
      title: '',
      department: ''
    })
    
    // 导入表单
    const importForm = reactive({
      role: 'student',
      file: null
    })
    
    // 计算属性：用户ID标签
    const userIdLabel = computed(() => {
      switch (userForm.role) {
        case 'student': return '学号'
        case 'teacher': return '工号'
        case 'admin': return '管理员ID'
        default: return '用户ID'
      }
    })
    
    // 表单验证规则
    const userRules = {
      role: [
        { required: true, message: '请选择用户类型', trigger: 'change' }
      ],
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      user_id: [
        { required: true, message: '请输入用户ID', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
      ],
      gender: [
        { required: true, message: '请选择性别', trigger: 'change' }
      ],
      major: [
        { required: true, message: '请输入专业', trigger: 'blur' }
      ],
      class_name: [
        { required: true, message: '请输入班级', trigger: 'blur' }
      ],
      title: [
        { required: true, message: '请选择职称', trigger: 'change' }
      ],
      department: [
        { required: true, message: '请输入院系', trigger: 'blur' }
      ]
    }
    
    const importRules = {
      role: [
        { required: true, message: '请选择用户类型', trigger: 'change' }
      ],
      file: [
        { required: true, message: '请选择文件', trigger: 'change' }
      ]
    }
    
    // 监听标签页变化
    watch(activeTab, (newVal) => {
      filterForm.role = newVal
      loadUsers()
    })
    
    // 加载用户列表
    const loadUsers = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          limit: pagination.pageSize,
          role: filterForm.role,
          keyword: filterForm.keyword
        }
        
        const res = await axios.get('/admin/users', { params })
        users.value = res.data.users || []
        pagination.total = res.data.total || 0
      } catch (error) {
        console.error('加载用户失败:', error)
        ElMessage.error('加载用户失败')
      } finally {
        loading.value = false
      }
    }
    
    // 处理标签页点击
    const handleTabClick = () => {
      pagination.currentPage = 1
    }
    
    // 处理页码变化
    const handleCurrentChange = (page) => {
      pagination.currentPage = page
      loadUsers()
    }
    
    // 处理每页条数变化
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      pagination.currentPage = 1
      loadUsers()
    }
    
    // 打开用户对话框
    const openUserDialog = (user = null) => {
      resetUserForm()
      
      if (user) {
        isEdit.value = true
        userForm.id = user.id
        userForm.role = user.role
        userForm.name = user.name
        userForm.email = user.email
        
        if (user.role === 'student') {
          userForm.user_id = user.student_id
          userForm.gender = user.gender
          userForm.age = user.age
          userForm.major = user.major
          userForm.class_name = user.class_name
        } else if (user.role === 'teacher') {
          userForm.user_id = user.teacher_id
          userForm.gender = user.gender
          userForm.title = user.title
          userForm.department = user.department
        } else if (user.role === 'admin') {
          userForm.user_id = user.admin_id
        }
      } else {
        isEdit.value = false
      }
      
      userDialogVisible.value = true
    }
    
    // 重置用户表单
    const resetUserForm = () => {
      userForm.id = null
      userForm.role = 'student'
      userForm.name = ''
      userForm.user_id = ''
      userForm.email = ''
      userForm.password = ''
      userForm.gender = '男'
      userForm.age = 18
      userForm.major = ''
      userForm.class_name = ''
      userForm.title = ''
      userForm.department = ''
    }
    
    // 提交用户表单
    const submitUserForm = async () => {
      if (!userFormRef.value) return
      
      await userFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            const payload = {
              name: userForm.name,
              email: userForm.email
            }
            
            if (userForm.role === 'student') {
              payload.student_id = userForm.user_id
              payload.gender = userForm.gender
              payload.age = userForm.age
              payload.major = userForm.major
              payload.class_name = userForm.class_name
            } else if (userForm.role === 'teacher') {
              payload.teacher_id = userForm.user_id
              payload.gender = userForm.gender
              payload.title = userForm.title
              payload.department = userForm.department
            } else if (userForm.role === 'admin') {
              payload.admin_id = userForm.user_id
            }
            
            if (!isEdit.value) {
              payload.password = userForm.password
              await axios.post(`/admin/users/${userForm.role}`, payload)
              ElMessage.success('用户创建成功')
            } else {
              await axios.put(`/admin/users/${userForm.role}/${userForm.id}`, payload)
              ElMessage.success('用户更新成功')
            }
            
            userDialogVisible.value = false
            loadUsers()
          } catch (error) {
            console.error('保存用户失败:', error)
            ElMessage.error(error.response?.data?.message || '保存用户失败')
          }
        }
      })
    }
    
    // 切换用户状态
    const toggleUserStatus = async (user) => {
      try {
        const action = user.status === 'active' ? '禁用' : '启用'
        await ElMessageBox.confirm(`确定要${action}该用户吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const newStatus = user.status === 'active' ? 'inactive' : 'active'
        await axios.put(`/admin/users/${user.role}/${user.id}/status`, {
          status: newStatus
        })
        
        ElMessage.success(`用户${action}成功`)
        
        // 更新本地状态
        const index = users.value.findIndex(u => u.id === user.id)
        if (index !== -1) {
          users.value[index].status = newStatus
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('更新用户状态失败:', error)
          ElMessage.error(error.response?.data?.message || '更新用户状态失败')
        }
      }
    }
    
    // 删除用户
    const deleteUser = async (user) => {
      try {
        await ElMessageBox.confirm('确定要删除该用户吗？删除后将无法恢复。', '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await axios.delete(`/admin/users/${user.role}/${user.id}`)
        ElMessage.success('用户删除成功')
        loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除用户失败:', error)
          ElMessage.error(error.response?.data?.message || '删除用户失败')
        }
      }
    }
    
    // 打开导入对话框
    const openImportDialog = () => {
      importForm.role = activeTab.value
      importForm.file = null
      importDialogVisible.value = true
    }
    
    // 处理文件变更
    const handleFileChange = (file) => {
      importForm.file = file.raw
    }
    
    // 下载模板
    const downloadTemplate = async () => {
      try {
        const res = await axios.get(`/admin/users/${importForm.role}/template`, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${importForm.role === 'student' ? '学生' : '教师'}导入模板.xlsx`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('下载模板失败:', error)
        ElMessage.error('下载模板失败')
      }
    }
    
    // 导入用户
    const importUsers = async () => {
      if (!importFormRef.value) return
      
      await importFormRef.value.validate(async (valid) => {
        if (valid) {
          if (!importForm.file) {
            ElMessage.warning('请选择文件')
            return
          }
          
          try {
            const formData = new FormData()
            formData.append('file', importForm.file)
            
            await axios.post(`/admin/users/${importForm.role}/import`, formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
            
            ElMessage.success('用户导入成功')
            importDialogVisible.value = false
            loadUsers()
          } catch (error) {
            console.error('导入用户失败:', error)
            ElMessage.error(error.response?.data?.message || '导入用户失败')
          }
        }
      })
    }
    
    onMounted(() => {
      loadUsers()
    })
    
    return {
      loading,
      users,
      activeTab,
      filterForm,
      pagination,
      userDialogVisible,
      importDialogVisible,
      isEdit,
      userForm,
      importForm,
      userIdLabel,
      userRules,
      importRules,
      userFormRef,
      importFormRef,
      loadUsers,
      handleTabClick,
      handleCurrentChange,
      handleSizeChange,
      openUserDialog,
      submitUserForm,
      toggleUserStatus,
      deleteUser,
      openImportDialog,
      handleFileChange,
      downloadTemplate,
      importUsers
    }
  }
}
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>