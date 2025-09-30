import { createRouter, createWebHistory } from 'vue-router'

// 路由懒加载
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')

// 学生路由
const StudentDashboard = () => import('../views/student/Dashboard.vue')

// 教师路由
const TeacherDashboard = () => import('../views/teacher/Dashboard.vue')
const TeacherAttendance = () => import('../views/teacher/Attendance.vue')

// 管理员路由
const AdminDashboard = () => import('../views/admin/Dashboard.vue')

// 权限控制
const requireAuth = (to, from, next) => {
  const user = localStorage.getItem('user')
  if (user) {
    next()
  } else {
    next('/login')
  }
}

const requireStudent = (to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user'))
  if (user && user.role === 'student') {
    next()
  } else {
    next('/login')
  }
}

const requireTeacher = (to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user'))
  if (user && user.role === 'teacher') {
    next()
  } else {
    next('/login')
  }
}

const requireAdmin = (to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user'))
  if (user && user.role === 'admin') {
    next()
  } else {
    next('/login')
  }
}

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
        path: 'attendance',
        name: 'TeacherAttendance',
        component: TeacherAttendance
      }
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
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router