import { createRouter, createWebHistory } from 'vue-router'

// 路由懒加载
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')

// 学生路由
const StudentDashboard = () => import('../views/student/Dashboard.vue')
const StudentCourses = () => import('../views/student/Courses.vue')
const StudentAttendance = () => import('../views/student/Attendance.vue')
const StudentProfile = () => import('../views/student/Profile.vue')

// 教师路由
const TeacherDashboard = () => import('../views/teacher/Dashboard.vue')
const TeacherAttendance = () => import('../views/teacher/Attendance.vue')
const TeacherCourses = () => import('../views/teacher/Courses.vue')
const TeacherProfile = () => import('../views/teacher/Profile.vue')

// 管理员路由
const AdminDashboard = () => import('../views/admin/Dashboard.vue')
const AdminUsers = () => import('../views/admin/Users.vue')
const AdminCourses = () => import('../views/admin/Courses.vue')
const AdminAttendance = () => import('../views/admin/Attendance.vue')

// 通用权限验证函数
const requireAuth = (role) => (to, from, next) => {
  try {
    const userStr = localStorage.getItem('user')
    if (!userStr) {
      console.log('未找到用户信息，跳转到登录页')
      return next('/login')
    }
    
    const user = JSON.parse(userStr)
    if (user && user.role === role) {
      console.log(`用户角色验证通过: ${role}`)
      return next()
    }
    
    console.log(`用户角色不匹配，当前角色: ${user?.role || '未知'}`)
    return next('/login')
  } catch (error) {
    console.error('路由守卫错误:', error)
    return next('/login')
  }
}

// 角色路由守卫
const requireStudent = requireAuth('student')
const requireTeacher = requireAuth('teacher')
const requireAdmin = requireAuth('admin')

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  
  // 学生路由
  {
    path: '/student',
    redirect: '/student/dashboard',
    beforeEnter: requireStudent,
    children: [
      {
        path: 'dashboard',
        name: 'StudentDashboard',
        component: StudentDashboard
      },
      {
        path: 'courses',
        name: 'StudentCourses',
        component: StudentCourses
      },
      {
        path: 'attendance',
        name: 'StudentAttendance',
        component: StudentAttendance
      },
      {
        path: 'profile',
        name: 'StudentProfile',
        component: StudentProfile
      }
    ]
  },
  
  // 教师路由
  {
    path: '/teacher',
    redirect: '/teacher/dashboard',
    beforeEnter: requireTeacher,
    children: [
      {
        path: 'dashboard',
        name: 'TeacherDashboard',
        component: TeacherDashboard
      },
      {
        path: 'courses',
        name: 'TeacherCourses',
        component: TeacherCourses
      },
      {
        path: 'profile',
        name: 'TeacherProfile',
        component: TeacherProfile
      },
      {
        path: 'attendance',
        name: 'TeacherAttendance',
        component: TeacherAttendance
      },
    ]
  },
  
  // 管理员路由
  {
    path: '/admin',
    redirect: '/admin/dashboard',
    beforeEnter: requireAdmin,
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: AdminUsers
      },
      {
        path: 'courses',
        name: 'AdminCourses',
        component: AdminCourses
      },
      {
        path: 'attendance',
        name: 'AdminAttendance',
        component: AdminAttendance
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫调试
router.beforeEach((to, from, next) => {
  console.log(`路由跳转: ${from.path} -> ${to.path}`)
  next()
})

export default router