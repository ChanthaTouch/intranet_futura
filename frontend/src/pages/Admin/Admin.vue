
<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Admin Center</h1>

    <nav class="flex flex-wrap gap-3">
      <button :class="btn('users')" @click="tab='users'">Manage Users</button>
      <button :class="btn('projects')" @click="tab='projects'">Manage Projects</button>
      <button :class="btn('clients')" @click="tab='clients'">Manage Clients</button>
      <button :class="btn('roles')" @click="tab='roles'">Manage Roles</button>
      <button :class="btn('holidays')" @click="tab='holidays'">Manage Holidays</button>
    </nav>

    <!-- PROJECTS TAB -->
    <section v-if="tab==='projects'" class="border rounded p-4 space-y-4">
      <h2 class="font-semibold">Projects</h2>
      <div class="flex gap-2 text-sm">
        <button :class="projectFilter==='active' ? 'px-2 py-1 border rounded bg-black/5 dark:bg-white/10' : 'px-2 py-1 border rounded'" @click="projectFilter='active'">Active</button>
        <button :class="projectFilter==='all' ? 'px-2 py-1 border rounded bg-black/5 dark:bg-white/10' : 'px-2 py-1 border rounded'" @click="projectFilter='all'">All</button>
      </div>
      <form @submit.prevent="createProject" class="grid md:grid-cols-7 gap-2">
        <input v-model="fPrj.code" placeholder="Code" class="border rounded p-2">
        <input v-model="fPrj.name" placeholder="Name" class="border rounded p-2 md:col-span-2">
        <select v-model="fPrj.client_type" class="border rounded p-2">
          <option value="external">external</option>
          <option value="internal">internal</option>
        </select>
        <select v-model="fPrj.status" class="border rounded p-2">
          <option value="active">active</option>
          <option value="on_hold">on_hold</option>
          <option value="to_be_liquidated">to_be_liquidated</option>
          <option value="archived">archived</option>
        </select>
        <input type="date" v-model="fPrj.start_date" class="border rounded p-2" />
        <input type="date" v-model="fPrj.end_date" class="border rounded p-2" />
        <textarea v-model="fPrj.scope_of_work" placeholder="Scope of work (Markdown supported)" class="border rounded p-2 md:col-span-7"></textarea>
        <textarea v-model="fPrj.brief" placeholder="Brief (Markdown supported)" class="border rounded p-2 md:col-span-7"></textarea>
        <button class="border rounded p-2 md:col-span-7">Create</button>
      </form>

      <div class="overflow-auto border rounded">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left">
              <th class="p-2">Code</th>
              <th>Name</th>
              <th>Client</th>
              <th>Status</th>
              <th>Start</th>
              <th>End</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in visibleProjects" :key="p && p.id" class="border-t">
              <td class="p-2">{{ p.code }}</td>
              <td>{{ p.name }}</td>
              <td>{{ p.client_type }}</td>
              <td>{{ p.status }}</td>
              <td>{{ p.start_date || '-' }}</td>
              <td>{{ p.end_date || '-' }}</td>
              <td class="space-x-2">
                <button class="text-xs underline" @click="selectProject(p)">Members</button>
                <button class="text-xs underline" @click="openEdit(p)">Edit</button>
                <button class="text-xs underline" @click="removeProject(p)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Members panel -->
      <div v-if="selected" class="border rounded p-4">
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-semibold">Members — {{ selected.name }}</h3>
          <button class="text-xs underline" @click="selected=null; members=[]">Close</button>
        </div>
        <div class="grid md:grid-cols-3 gap-2 mb-2">
          <select v-model.number="memberUserId" class="border rounded p-2">
            <option disabled value="">Select user…</option>
            <option v-for="u in candidateUsers" :key="u && u.id" :value="u.id">
              {{ u.username }} — {{ u.email }}
            </option>
          </select>
          <select v-model="memberRole" class="border rounded p-2">
            <option value="member">member</option>
            <option value="viewer">viewer</option>
            <option value="pm">pm</option>
          </select>
          <button class="border rounded p-2" @click="addMember" :disabled="!memberUserId">Add</button>
        </div>
        <div class="overflow-auto border rounded">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-left">
                <th class="p-2">User</th>
                <th>Email</th>
                <th>Role</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m && m.id" class="border-t">
                <td class="p-2">{{ m.username || m.full_name || m.id }}</td>
                <td>{{ m.email }}</td>
                <td class="capitalize"><select v-model="m.role" class="border rounded p-1" @change="updateMemberRole(m)"><option value="member">member</option><option value="viewer">viewer</option><option value="pm">pm (manager)</option></select></td>
                <td><button class="text-xs underline" @click="removeMember(m)">Remove</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Edit modal -->
      <div v-if="editOpen" class="fixed inset-0 bg-black/20 flex items-start justify-center p-6 z-10 backdrop-blur-sm">
        <div class="bg-white text-zinc-900 rounded-2xl p-6 shadow-2xl w-full max-w-2xl space-y-4 border border-black/5">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold">Edit project</h3>
            <button class="text-sm underline" @click="closeEdit">Close</button>
          </div>
          <div class="grid sm:grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-600">Code</label>
              <input v-model="editForm.code" class="border rounded p-2 w-full" disabled />
            </div>
            <div>
              <label class="text-xs text-gray-600">Name</label>
              <input v-model="editForm.name" class="border rounded p-2 w-full" />
            </div>
            <div>
              <label class="text-xs text-gray-600">Client Type</label>
              <select v-model="editForm.client_type" class="border rounded p-2 w-full">
                <option value="external">external</option>
                <option value="internal">internal</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-600">Status</label>
              <select v-model="editForm.status" class="border rounded p-2 w-full">
                <option value="active">active</option>
                <option value="on_hold">on_hold</option>
                <option value="to_be_liquidated">to_be_liquidated</option>
                <option value="archived">archived</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-600">Start</label>
              <input type="date" v-model="editForm.start_date" class="border rounded p-2 w-full" />
            </div>
            <div>
              <label class="text-xs text-gray-600">End</label>
              <input type="date" v-model="editForm.end_date" class="border rounded p-2 w-full" />
            </div>
            <div class="sm:col-span-2">
              <label class="text-xs text-gray-600">Scope of work</label>
              <textarea v-model="editForm.scope_of_work" class="border rounded p-2 w-full" rows="3"></textarea>
            </div>
            <div class="sm:col-span-2">
              <label class="text-xs text-gray-600">Brief</label>
              <textarea v-model="editForm.brief" class="border rounded p-2 w-full" rows="3"></textarea>
            </div>
          </div>
          <div class="flex gap-2 justify-end">
            <button class="border rounded px-3 py-2" @click="closeEdit">Cancel</button>
            <button class="border rounded px-3 py-2" :disabled="saving" @click="saveEdit">Save</button>
          </div>
        </div>
      </div>
    </section>
    <!-- Other tabs left as-is -->
    
    <!-- USERS TAB -->
    <section v-if="tab==='users'" class="card p-4 space-y-3">
      <h2 class="font-semibold">Users</h2>
      <form @submit.prevent="createUser" class="grid md:grid-cols-5 gap-2">
        <input v-model="fUser.username" placeholder="Username" class="input">
        <input v-model="fUser.email" placeholder="Email" class="input">
        <input v-model="fUser.password" placeholder="Password" type="password" class="input">
        <select v-model.number="fUser.role_id" class="input">
          <option disabled value="">Role…</option>
          <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
        <button class="btn btn-primary">Create</button>
      </form>
      <div class="overflow-auto">
        <table class="w-full text-sm">
          <thead>
  <tr class="text-left">
    <th class="p-2">User</th>
    <th>Email</th>
    <th>Role</th>
    <th>Line Manager</th>
    <th>Password</th>
    <th>Active</th>
    <th></th>
  </tr>
</thead>
<tbody>
  <tr v-for="u in (users || [])" :key="u && u.id" class="border-t">
    <td class="p-2">{{ u.username }}</td>
    <td>{{ u.email }}</td>
    <td>
      <select v-model.number="u.role_id" class="input" @change="updateUser(u)">
        <option v-for="r in (roles || [])" :key="r && r.id" :value="r && r.id">{{ r && r.name }}</option>
      </select>
    </td>
    <td>
      <select v-model="u.manager_id" class="input" @change="updateUser(u)">
  <option :value="null">— None —</option>
  <option v-for="m in candidatesFor(u)" :key="m.id" :value="m.id">{{ m.username }}</option>
</select>
    </td>
    <td class="whitespace-nowrap">
      <input v-model="u._newPassword" type="password" placeholder="New…" class="input w-36 inline-block mr-1">
      <button class="text-xs underline" @click="setPassword(u)" :disabled="!u._newPassword">Set</button>
    </td>
    <td><input type="checkbox" v-model="u.is_active" @change="updateUser(u)" /></td>
    <td><button class="text-xs underline" @click="removeUser(u)">Delete</button></td>
  </tr>
</tbody>
        </table>
      </div>
    </section>

    <!-- CLIENTS TAB -->
    <section v-if="tab==='clients'" class="border rounded p-4 space-y-3">
      <h2 class="font-semibold">Clients</h2>
      <form @submit.prevent="createClient" class="grid md:grid-cols-4 gap-2">
        <input v-model="fClient.name" placeholder="Name" class="border rounded p-2">
        <input v-model="fClient.email" placeholder="Email" class="border rounded p-2">
        <input v-model="fClient.phone" placeholder="Phone" class="border rounded p-2">
        <button class="border rounded p-2">Create</button>
      </form>
      <div class="overflow-auto border rounded">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left">
              <th class="p-2">Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in safeClients" :key="c && c.id" class="border-t">
              <td class="p-2"><input v-model="c.name" class="border rounded p-2 w-full" /></td>
              <td><input v-model="c.email" class="border rounded p-2 w-full" /></td>
              <td><input v-model="c.phone" class="border rounded p-2 w-full" /></td>
              <td class="whitespace-nowrap space-x-2">
                <button class="text-xs underline" @click="updateClient(c)">Save</button>
                <button class="text-xs underline" @click="removeClient(c)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ROLES TAB -->
    <section v-if="tab==='roles'" class="border rounded p-4 space-y-3">
      <h2 class="font-semibold">Roles</h2>
      <form @submit.prevent="createRole" class="grid md:grid-cols-3 gap-2">
        <input v-model="fRole.name" placeholder="Name" class="border rounded p-2">
        <input v-model="fRole.description" placeholder="Description" class="border rounded p-2 md:col-span-2">
        <button class="border rounded p-2">Create</button>
      </form>
      <div class="overflow-auto border rounded">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left">
              <th class="p-2">Name</th>
              <th>Description</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in safeRoles" :key="r && r.id" class="border-t">
              <td class="p-2"><input v-model="r.name" class="border rounded p-2 w-full" /></td>
              <td><input v-model="r.description" class="border rounded p-2 w-full" /></td>
              <td class="whitespace-nowrap space-x-2">
                <button class="text-xs underline" @click="updateRole(r)">Save</button>
                <button class="text-xs underline" @click="removeRole(r)" :disabled="r.id===1">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  
    <!-- HOLIDAYS TAB -->
    <section v-if="tab==='holidays'" class="border rounded p-4 space-y-3">
      <h2 class="font-semibold">Public Holidays</h2>
      <form @submit.prevent="createHoliday" class="grid md:grid-cols-4 gap-2 items-center">
        <input type="date" v-model="fHoliday.date" class="border rounded p-2">
        <input v-model="fHoliday.name" placeholder="Name" class="border rounded p-2 md:col-span-2">
        <button class="border rounded p-2">Add</button>
        <div v-if="holidayError" class="text-red-600 md:col-span-4 text-sm">{{ holidayError }}</div>
      </form>

      <details class="rounded border p-3">
        <summary class="cursor-pointer font-medium">Bulk add (one "YYYY-MM-DD, Name" per line) — weekends will be skipped</summary>
        <div class="mt-2 space-y-2">
          <textarea v-model="bulkHolidayText" rows="4" class="border rounded p-2 w-full" placeholder="2025-01-01, New Year&#39;s Day
2025-04-14, Khmer New Year — Day 1"></textarea>
          <button class="border rounded px-3 py-2" @click="bulkAddHolidays">Add All</button>
        </div>
      </details>

      <div class="overflow-auto border rounded">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left">
              <th class="p-2">Date</th>
              <th>Name</th>
              <th>Country</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in safeHolidays" :key="h && h.id" class="border-t">
              <td class="p-2">{{ h.date }}</td>
              <td><input v-model="h.name" class="border rounded p-2 w-full" /></td>
              <td>{{ h.country || '-' }}</td>
              <td class="whitespace-nowrap space-x-2">
                <button class="text-xs underline" @click="updateHoliday(h)">Save</button>
                <button class="text-xs underline" @click="removeHoliday(h)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const tab = ref('projects')

// data stores
const users = ref([])
const roles = ref([])
const projects = ref([])
const clients = ref([])
const holidays = ref([])
const members = ref([])
const projectFilter = ref('active')


// safe lists
const safeUsers = computed(() => (users.value || []).filter(u => u && typeof u.id !== 'undefined'))
const safeRoles = computed(() => (roles.value || []).filter(r => r && typeof r.id !== 'undefined'))
const safeProjects = computed(() => (projects.value || []).filter(p => p && typeof p.id !== 'undefined'))
const visibleProjects = computed(() => projectFilter.value==='active' ? safeProjects.value.filter(p => (p.status||'')==='active') : safeProjects.value)
const safeClients = computed(() => (clients.value || []).filter(c => c && typeof c.id !== 'undefined'))
const safeHolidays = computed(() => (holidays.value || []).filter(h => h && typeof h.id !== 'undefined'))
// forms
const fUser = ref({ username:'', email:'', password:'', role_id:3, manager_id:null })
const fPrj = ref({ code:'', name:'', client_type:'external', status:'active', start_date:null, end_date:null, scope_of_work:'', description:'', brief:'' })
const fClient = ref({ name:'', email:'', phone:'' })
const fRole = ref({ name:'', description:'' })
const fHoliday = ref({ date:'', name:'' })

// project form
// selection & members
const selected = ref(null)
const memberUserId = ref('')
const memberRole = ref('member')

const candidateUsers = computed(() => {
  const ids = new Set(members.value.map(m=>m.id))
  return users.value.filter(u => !ids.has(u.id))
})

function btn(name){ return ['px-3','py-1','border','rounded', tab.value===name?'bg-gray-100':''].join(' ') }

// loaders
async function loadAll(){ await Promise.all([loadUsers(), loadRoles(), loadProjects(), loadClients(), loadHolidays()]) }
async function loadUsers(){ try{ const { data } = await api.get('/api/admin/users'); users.value = data }catch{} }

async function loadHolidays(){ try{ const { data } = await api.get('/api/admin/holidays'); holidays.value=data }catch{} }
async function loadRoles(){ try{ const { data } = await api.get('/api/admin/roles'); roles.value = data }catch{} }
async function loadProjects(){ try{ const { data } = await api.get('/api/admin/projects'); projects.value = data }catch{} }
async function loadClients(){ try{ const { data } = await api.get('/api/admin/clients'); clients.value = data }catch{} }

async function createUser(){
  await api.post('/api/admin/users', fUser.value)
  fUser.value={ username:'', email:'', password:'', role_id:3 }
  await loadUsers()
}
async function updateUser(u){
  const mid = (u.manager_id === null || u.manager_id === undefined || u.manager_id === '') ? null : Number(u.manager_id)
  const payload = { role_id: u.role_id, is_active: u.is_active, manager_id: mid }
  await api.put(`/api/admin/users/${u.id}`, payload)
}

async function removeUser(u){
  if(!confirm('Delete user?')) return
  await api.delete(`/api/admin/users/${u.id}`)
  await loadUsers()
}

async function createClient(){ await api.post('/api/admin/clients', fClient.value); fClient.value={ name:'', email:'', phone:'' }; await loadClients() }
async function updateClient(c){ await api.put(`/api/admin/clients/${c.id}`, { name:c.name, email:c.email, phone:c.phone }) }
async function removeClient(c){ if(!confirm('Delete client?')) return; await api.delete(`/api/admin/clients/${c.id}`); await loadClients() }

async function createRole(){ await api.post('/api/admin/roles', fRole.value); fRole.value={ name:'', description:'' }; await loadRoles(); await loadHolidays() }
async function updateRole(r){ await api.put(`/api/admin/roles/${r.id}`, { name:r.name, description:r.description }) }
async function removeRole(r){ if(!confirm('Delete role?')) return; await api.delete(`/api/admin/roles/${r.id}`); await loadRoles(); await loadHolidays() }
async function loadMembers(){ if(!selected.value) return; const { data } = await api.get(`/api/admin/projects/${selected.value.id}/members`); members.value = data; memberUserId.value=''; memberRole.value='member' }

// actions
async function createProject(){ await api.post('/api/admin/projects', fPrj.value); fPrj.value={ code:'', name:'', client_type:'external', status:'active', office_id:null, start_date:null, end_date:null, scope_of_work:'', brief:'' }; await loadProjects() }
function selectProject(p){ selected.value = { ...p }; loadMembers() }
async function saveProjectMeta(p){ await api.put(`/api/admin/projects/${p.id}`, { name: p.name, start_date: p.start_date, end_date: p.end_date }); await loadProjects() }
async function addMember(){ if(!selected.value || !memberUserId.value) return; await api.post(`/api/admin/projects/${selected.value.id}/access/${memberUserId.value}`); await loadMembers() }
async function removeMember(m){ await api.delete(`/api/admin/projects/${selected.value.id}/access/${m.id}`); await loadMembers() }
async function updateMemberRole(m){ await api.put(`/api/admin/projects/${selected.value.id}/access/${m.id}`, { role: m.role }); await loadMembers() }

// modal editor
const editOpen = ref(false)
const saving = ref(false)
const editForm = ref({ id:null, code:'', name:'', client_type:'external', status:'active', start_date:null, end_date:null, scope_of_work:'', description:'', brief:'' })

function openEdit(p){
  editForm.value = { description:'', ...p }
  editForm.value.scope_of_work = editForm.value.scope_of_work || ''
  editForm.value.brief = editForm.value.brief || ''
  editOpen.value = true
}
function closeEdit(){ editOpen.value = false }
async function saveEdit(){
  if(!editForm.value.id) return
  saving.value = true
  try{
    const body = { name: editForm.value.name, client_type: editForm.value.client_type, status: editForm.value.status, start_date: editForm.value.start_date, end_date: editForm.value.end_date, scope_of_work: editForm.value.scope_of_work, brief: editForm.value.brief, description: editForm.value.description }
    await api.put(`/api/admin/projects/${editForm.value.id}`, body)
    await loadProjects()
    if(selected.value && selected.value.id===editForm.value.id){
      selected.value = { ...selected.value, ...body }
    }
    editOpen.value=false
  } finally {
    saving.value=false
  }
}

async function setPassword(u){ if(!u || !u._newPassword) return; await api.put(`/api/admin/users/${u.id}`, { password: u._newPassword }); u._newPassword=''; }

// holidays actions
async function createHoliday(){
  holidayError.value = ''
  if(!fHoliday.value.date) return
  const dt = new Date(fHoliday.value.date + 'T00:00:00')
  const day = dt.getDay()
  if(day === 0 || day === 6){ holidayError.value = 'Public holidays cannot fall on Saturday or Sunday.'; return }
  await api.post('/api/admin/holidays', { date: fHoliday.value.date, name: fHoliday.value.name || 'Holiday' })
  fHoliday.value = { date:'', name:'' }
  await loadHolidays()
}
async function updateHoliday(h){ await api.put(`/api/admin/holidays/${h.id}`, { name: h.name }) }
async function removeHoliday(h){ if(!confirm('Delete holiday?')) return; await api.delete(`/api/admin/holidays/${h.id}`); await loadHolidays() }
async function bulkAddHolidays(){
  holidayError.value = ''
  const lines = (bulkHolidayText.value || '').split('\n').map(s => s.trim()).filter(Boolean)
  for(const line of lines){
    // Accept formats: "YYYY-MM-DD, Name" or "YYYY-MM-DD Name"
    const m = line.match(/^(\d{4}-\d{2}-\d{2})[\s,]+(.+)$/)
    if(!m) continue
    const [_, date, name] = m
    const dt = new Date(date + 'T00:00:00')
    const day = dt.getDay()
    if(day === 0 || day === 6) continue
    try{ await api.post('/api/admin/holidays', { date, name }) }catch(e){ console.error(e) }
  }
  bulkHolidayText.value = ''
  await loadHolidays()
}



function candidatesFor(u){
  // return all users except self; could also add more rules here (e.g., only active)
  return (users.value || []).filter(m => m && m.id !== undefined && m.id !== u.id)
}
onMounted(loadAll)
</script>

// helpers
function candidatesFor(u){
  // return all users except self; could also add more rules here (e.g., only active)
  return (users.value || []).filter(m => m && m.id !== undefined && m.id !== u.id)
}
