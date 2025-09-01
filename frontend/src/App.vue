<template>
  <div class="h-screen w-screen flex flex-col bg-gradient-to-br from-gray-50 to-gray-100 font-inter">
    <header class="md:hidden sticky top-0 z-50 flex items-center justify-between px-6 py-4 bg-white shadow-md border-b border-gray-200">
      <div class="flex items-center gap-3">
        <i class="fa-solid fa-cubes text-blue-600 text-2xl"></i>
        <span class="font-bold text-2xl text-gray-900 tracking-tight">Futura</span>
      </div>
      <button
        @click="open = !open"
        :aria-expanded="open"
        aria-label="Toggle navigation menu"
        class="text-gray-600 hover:text-blue-600 focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 rounded-lg p-2 transition-colors duration-200"
      >
        <i class="fa-solid fa-bars text-2xl transition-transform duration-200" :class="{ 'rotate-90': open }"></i>
      </button>
    </header>

    <div class="flex flex-1 h-[calc(100vh-80px)] md:h-screen">
      <aside
        :class="[sidebarVisible ? 'block' : 'hidden md:block', open ? 'translate-x-0' : '-translate-x-full', 'fixed md:static md:translate-x-0 w-80 bg-gradient-to-b from-gray-900 to-gray-800 text-gray-100 shadow-2xl md:shadow-none border-r border-gray-700 h-full transition-transform duration-300 ease-in-out md:block z-40']"
      >
        <div
          v-if="open"
          class="fixed inset-0 bg-black bg-opacity-60 md:hidden"
          @click="open = false"
        ></div>

        <div class="p-6 flex items-center gap-4 border-b border-gray-700 bg-gray-900">
          <div class="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-2xl font-semibold transition-transform duration-200 hover:scale-105">
            {{ auth.user?.username?.charAt(0)?.toUpperCase() || '👤' }}
          </div>
          <div>
            <div class="font-bold text-white text-xl tracking-tight">Futura Intranet</div>
            <div class="text-sm text-gray-300 mt-1" v-if="auth.user">Welcome, {{ auth.user.username }}</div>
          </div>
        </div>

        <nav class="p-6 space-y-8 overflow-y-auto h-[calc(100%-96px)] no-scrollbar">
          <!-- User Menu -->
          <div v-if="auth.user">
            <button
              @click="toggleUserMenu"
              class="flex items-center justify-between w-full text-xs font-semibold uppercase text-gray-400 px-4 mb-4 tracking-wider hover:text-blue-400 transition-colors duration-200"
              aria-label="Toggle User Menu"
            >
              User Menu
              <i :class="userMenuOpen ? 'fa-solid fa-chevron-down' : 'fa-solid fa-angle-right'" class="text-sm"></i>
            </button>
            <ul v-if="userMenuOpen" class="space-y-1">
              <li>
                <router-link class="nav-link" to="/" aria-label="Dashboard">
                  <i class="fa-solid fa-gauge text-lg"></i> Dashboard
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/profile" aria-label="Edit Profile">
                  <i class="fa-solid fa-id-card text-lg"></i> Profile
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/timesheet" aria-label="Timesheet">
                  <i class="fa-regular fa-clock text-lg"></i> Timesheet
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/timesheet-review" aria-label="Timesheet Review">
                  <i class="fa-solid fa-clipboard-check text-lg"></i> Timesheet Review
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/recruitment" aria-label="Recruitment">
                  <i class="fa-solid fa-user-plus text-lg"></i> Recruitment
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/leave" aria-label="Leave">
                  <i class="fa-solid fa-plane-departure text-lg"></i> Leave
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/tasks" aria-label="Task Card">
                  <i class="fa-solid fa-table-columns text-lg"></i> Tasks
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/mission" aria-label="Mission Request">
                  <i class="fa-solid fa-route text-lg"></i> Mission
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/requests" aria-label="Other Requests">
                  <i class="fa-solid fa-list-check text-lg"></i> Requests
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/helpdesk" aria-label="Helpdesk">
                  <i class="fa-solid fa-life-ring text-lg"></i> Helpdesk
                </router-link>
              </li>
            </ul>
          </div>

        <!-- HRMIS Menu -->
<div v-if="auth.user">
  <button
    @click="toggleHRMISMenu"
    class="flex items-center justify-between w-full text-xs font-semibold uppercase text-gray-400 px-4 mb-4 tracking-wider hover:text-blue-400 transition-colors duration-200"
            aria-label="Toggle HRMIS Menu"
          >
            HRMIS
            <i :class="hrmisMenuOpen ? 'fa-solid fa-chevron-down' : 'fa-solid fa-angle-right'" class="text-sm"></i>
          </button>

          <ul v-if="hrmisMenuOpen" class="space-y-1">
            <li>
              <router-link class="nav-link" to="/recruitment-record" aria-label="Recruitment Record">
                <i class="fa-solid fa-user-plus text-lg"></i> Recruitment Record
              </router-link>
            </li>
            <li>
              <router-link class="nav-link" to="/user-profile" aria-label="User Profile">
                <i class="fa-solid fa-user text-lg"></i> User Profile
              </router-link>
            </li>
            <li>
              <router-link class="nav-link" to="/leave-record" aria-label="Leave Record">
                <i class="fa-solid fa-plane-departure text-lg"></i> Leave Record
              </router-link>
            </li>
            <li>
              <router-link class="nav-link" to="/request-record" aria-label="Request Record">
                <i class="fa-solid fa-notes-medical text-lg"></i> Request Record
              </router-link>
            </li>
          </ul>
        </div>


          <!-- Projects Menu -->
          <div v-if="auth.user">
            <button
              @click="toggleProjectsMenu"
              class="flex items-center justify-between w-full text-xs font-semibold uppercase text-gray-400 px-4 mb-4 tracking-wider hover:text-blue-400 transition-colors duration-200"
              aria-label="Toggle Projects Menu"
            >
              Projects
              <i :class="projectsMenuOpen ? 'fa-solid fa-chevron-down' : 'fa-solid fa-angle-right'" class="text-sm"></i>
            </button>
            <ul v-if="projectsMenuOpen && projects.length" class="space-y-1">
              <li v-for="p in projects" :key="p.id">
                <router-link class="nav-link" :to="`/projects/${p.id}`" :aria-label="`Project ${p.name}`">
                  <i class="fa-solid fa-diagram-project text-lg"></i> {{ p.code }} — {{ p.name }}
                </router-link>
              </li>
            </ul>
            <div v-else-if="projectsMenuOpen && loadingProjects" class="px-4 text-gray-300 text-sm">
              Loading projects...
            </div>
          </div>

          <!-- Admin Menu -->
          <div v-if="auth.user?.role_id === 1">
            <div class="text-xs font-semibold uppercase text-gray-400 px-4 mb-4 tracking-wider">Admin</div>
            <ul class="space-y-1">
              <li>
                <router-link class="nav-link" to="/admin" aria-label="Admin Center">
                  <i class="fa-solid fa-shield-halved text-lg"></i> Admin Center
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/library" aria-label="Library">
                  <i class="fa-solid fa-book text-lg"></i> Library
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/finance" aria-label="Finance">
                  <i class="fa-solid fa-coins text-lg"></i> Finance
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/qa" aria-label="Quality">
                  <i class="fa-solid fa-clipboard-check text-lg"></i> Quality
                </router-link>
              </li>
              <li>
                <router-link class="nav-link" to="/safety" aria-label="Safety">
                  <i class="fa-solid fa-helmet-safety text-lg"></i> Safety
                </router-link>
              </li>
            </ul>
          </div>

          <button
            class="mt-8 text-sm text-blue-400 hover:text-blue-300 px-4 transition-colors duration-200 underline font-medium"
            v-if="auth.user"
            @click="logout"
            aria-label="Logout"
          >
            <i class="fa-solid fa-sign-out-alt mr-2"></i> Logout
          </button>
        </nav>
      </aside>

      <main class="flex-1 h-full overflow-y-auto bg-gray-50 no-scrollbar">
        <header class="bg-white p-6 md:p-8 lg:p-10 border-b border-gray-200 sticky top-0 z-10 flex items-center justify-between h-20 shadow-sm">
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900 tracking-tight">
            <img src="./assets/logo.jpg" class="w-52 h-20 object-contain" alt="Futura Logo">
          </h1>
          <div class="flex items-center gap-4">
            <button
              class="hidden md:flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors duration-200"
              aria-label="Notifications"
            >
              <i class="fa-solid fa-bell text-xl"></i>
              <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-red-500 -top-2 -left-1"></span>
            </button>
            <div class="relative group">
              <button
                class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
                aria-label="User menu"
              >
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white text-lg font-semibold transition-transform duration-200 hover:scale-105">
                  {{ auth.user?.username?.charAt(0)?.toUpperCase() || '👤' }}
                </div>
                <span class="text-sm font-semibold text-gray-700 hidden lg:block">Hi, {{ auth.user?.username || 'User' }}</span>
                <i class="fa-solid fa-angle-down text-sm text-gray-500 hidden lg:block transition-transform duration-200 group-hover:rotate-180"></i>
              </button>
              <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 hidden group-hover:block transition-all duration-300 z-50">
                <a href="/profile" class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2">
                  <i class="fa-solid fa-user text-sm"></i> Profile
                </a>
                <a href="#" @click="logout" class="px-4 py-2 text-sm text-red-600 hover:bg-gray-100 flex items-center gap-2">
                  <i class="fa-solid fa-sign-out-alt text-sm"></i> Logout
                </a>
              </div>
            </div>
            <button
              @click="toggleSidebar"
              class="md:hidden flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors duration-200"
              aria-label="Toggle Sidebar"
            >
              <i class="fa-solid fa-bars text-xl"></i>
            </button>
          </div>
        </header>

        <div class="p-6 md:p-8 lg:p-10 h-auto overflow-y-auto no-scrollbar">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from './store'
import api from './api'

const auth = useAuth()
const open = ref(false) // Navigation menu hidden by default
const projects = ref([])
const loadingProjects = ref(false)
const userMenuOpen = ref(true) // Default to open for user menu
const projectsMenuOpen = ref(true) // Default to open for projects menu
const hrmisMenuOpen = ref(true) // Default to open for HRMIS menu
const sidebarVisible = ref(true) // Sidebar visibility state

function logout() {
  auth.logout()
  open.value = false
}

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

function toggleProjectsMenu() {
  projectsMenuOpen.value = !projectsMenuOpen.value
}

function toggleHRMISMenu() {
  hrmisMenuOpen.value = !hrmisMenuOpen.value
}

function toggleSidebar() {
  sidebarVisible.value = !sidebarVisible.value
}

async function loadProjects() {
  if (!auth.token) return
  loadingProjects.value = true
  try {
    const { data } = await api.get('/api/projects/active')
    projects.value = data
  } catch (e) {
    console.error('Failed to load projects:', e)
  } finally {
    loadingProjects.value = false
  }
}

onMounted(loadProjects)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.font-inter {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  color: #e5e7eb;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: #1f2937;
  color: #60a5fa;
  transform: translateX(4px);
}

.nav-link.router-link-active {
  background-color: #1f2937;
  color: #60a5fa;
  font-weight: 600;
  box-shadow: inset 3px 0 0 #60a5fa;
}

.nav-link:focus {
  outline: none;
  box-shadow: 0 0 0 2px #60a5fa;
}

.fa-solid, .fa-regular {
  width: 1.25rem;
  text-align: center;
}

@media (max-width: 767px) {
  aside {
    width: 80%;
    max-width: 320px;
  }
}

@media (min-width: 768px) {
  .nav-link {
    padding: 0.75rem 1.25rem;
  }
}

.group-hover\:block {
  transition: opacity 0.3s ease-in-out;
}

/* Hide scrollbar but keep scrolling functionality */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
</style>