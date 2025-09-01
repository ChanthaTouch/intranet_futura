
import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from './store'

const Login = () => import('./pages/Login.vue')
const Dashboard = () => import('./pages/Dashboard.vue')
const Project = () => import('./pages/Projects/Project.vue')
const Admin = () => import('./pages/Admin/Admin.vue')
const Library = () => import('./pages/Library/Library.vue')
const Helpdesk = () => import('./pages/Helpdesk/Home.vue')
const Finance = () => import('./pages/Finance/Home.vue')
const QA = () => import('./pages/QA/Home.vue')
const Safety = () => import('./pages/Safety/Home.vue')
const ProfileEdit = () => import('./pages/User/ProfileEdit.vue')
const Leave = () => import('./pages/User/Leave.vue')
const Timesheet = () => import('./pages/User/Timesheet.vue')
const TimesheetReview = () => import('./pages/User/TimesheetReview.vue')
const TaskCard = () => import('./pages/User/TaskCard.vue')
const Mission = () => import('./pages/User/Mission.vue')
const Requests = () => import('./pages/User/Requests.vue')
const UserProfile = () => import('./pages/HRMIS/UserProfile.vue')
const LeaveRecord = () => import('./pages/HRMIS/LeaveRecord.vue')
const Recruitment = () => import('./pages/User/Recruitment.vue')
const RecruitmentRecord = () => import('./pages/HRMIS/RecruitmentRecord.vue')
const RequestRecord = () => import('./pages/HRMIS/RequestRecord.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/', component: Dashboard, meta: { requiresAuth: true } },
    { path: '/tasks', component: TaskCard, meta: { requiresAuth: true } },
    { path: '/projects/:id', component: Project, meta: { requiresAuth: true } },
    { path: '/helpdesk', component: Helpdesk, meta: { requiresAuth: true } },
    { path: '/library', component: Library, meta: { requiresAuth: true } },
    { path: '/finance', component: Finance, meta: { requiresAuth: true, adminOnly: true } },
    { path: '/qa', component: QA, meta: { requiresAuth: true, adminOnly: true } },
    { path: '/safety', component: Safety, meta: { requiresAuth: true, adminOnly: true } },
    { path: '/profile', component: ProfileEdit, meta: { requiresAuth: true } },
    { path: '/leave', component: Leave, meta: { requiresAuth: true } },
    { path: '/timesheet', component: Timesheet, meta: { requiresAuth: true } },
    { path: '/timesheet-review', component: TimesheetReview, meta: { requiresAuth: true } },
    { path: '/mission', component: Mission, meta: { requiresAuth: true } },
    { path: '/requests', component: Requests, meta: { requiresAuth: true } },
    { path: '/recruitment', component: Recruitment, meta: { requiresAuth: true } },
    { path: '/user-profile', component: UserProfile, meta: { requiresAuth: true } },
    { path: '/leave-record', component: LeaveRecord, meta:{requiresAuth:true} },
    { path: '/recruitment-record', component: RecruitmentRecord, meta:{requiresAuth:true} },
    { path: '/request-record', component:RequestRecord, meta:{requiresAuth:true} },
    { path: '/admin', component: Admin, meta: { requiresAuth: true,  } },
  ]
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuth()
  if (to.meta.requiresAuth && !auth.token) return next('/login')
  if (auth.token && !auth.user) {
    try { await auth.fetchMe() } catch(e){ auth.logout(); return next('/login') }
  }
  if (to.meta.adminOnly && auth.user?.role_id !== 1) return next('/')
  next()
})

export default router
