<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300">
    <div class="w-full p-4 mx-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg">
        <div class="p-6 rounded-lg bg-gray-50 shadow-inner">
          <div class="grid lg:grid-cols-3 gap-6">
            <div class="bg-white rounded-lg shadow p-6">
              <div class="text-xl font-bold text-gray-800 mb-4">Employee Information</div>
              <div class="text-sm text-gray-600"><b>Name:</b> {{ me?.full_name || me?.username }}</div>
              <div class="text-sm text-gray-600"><b>Email:</b> {{ me?.email }}</div>
              <div class="text-sm text-gray-600"><b>Manager:</b> {{ managerName }}</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
              <div class="text-xl font-bold text-gray-800 mb-4">Timesheet Information</div>
              <div class="text-sm text-gray-600"><b>Week:</b> {{ weekNumber }}</div>
              <div class="text-sm text-gray-600"><b>Period:</b> {{ fmt(start) }} - {{ fmt(end) }}</div>
              <div class="text-sm text-gray-600"><b>Status:</b> <span :class="submitted ? 'text-green-600 bg-green-200' : 'text-gray-600 bg-gray-200'">{{ submitted ? 'Submitted' : 'Draft (not submitted)' }}</span></div>
              <div class="mt-4 flex gap-3">
                <button class="px-4 py-2 bg-gray-600 text-white font-bold rounded-md hover:bg-gray-700 transition duration-300 shadow-md hover:shadow-lg" @click="shift(-7)">« Previous week</button>
                <button class="px-4 py-2 bg-gray-600 text-white font-bold rounded-md hover:bg-gray-700 transition duration-300 shadow-md hover:shadow-lg" @click="toCurrent()">Current week</button>
                <button class="px-4 py-2 bg-gray-600 text-white font-bold rounded-md hover:bg-gray-700 transition duration-300 shadow-md hover:shadow-lg" @click="shift(7)">Next week »</button>
              </div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
              <div class="text-xl font-bold text-gray-800 mb-4">Information</div>
              <div class="text-sm text-gray-600">Note: daily max 10h. Saturdays, Sundays, and public holidays are disabled.</div>
              <div v-if="holidayText" class="text-sm text-red-600 mt-2">Public Holiday: {{ holidayText }}</div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-6 mt-8 space-y-4">
            <div class="text-xl font-bold text-gray-800">Project</div>
            <div class="grid md:grid-cols-4 gap-3">
              <select v-model.number="newRow.contract_id" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                <option disabled value="">— Select Project —</option>
                <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.code }} — {{ p.name }}</option>
              </select>
              <input v-model="newRow.description" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white md:col-span-2" placeholder="Detail / Notes (optional)">
              <button class="px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg" @click="addRow">
                <i class="fas fa-plus mr-2"></i>Add row
              </button>
            </div>
            <div class="grid md:grid-cols-4 gap-3">
              <select v-model="ncType" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                <option value="">— Select Non Chargeable time —</option>
                <option>Training</option>
                <option>Meeting</option>
                <option>Admin</option>
                <option>Leave</option>
              </select>
              <input v-model="ncDetail" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white md:col-span-2" placeholder="Type detail (optional)">
              <button class="px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg" @click="addNC">
                <i class="fas fa-plus mr-2"></i>Add non-chargeable
              </button>
            </div>
          </div>

          <div class="mt-8 bg-white rounded-lg shadow p-6 overflow-auto">
            <table class="min-w-full table-auto text-sm">
              <thead class="bg-gray-200 text-gray-600 uppercase leading-normal">
                <tr>
                  <th class="py-3 px-6 text-left font-semibold">Project / Type</th>
                  <th v-for="(d,i) in days" :key="i" class="py-3 px-6 text-left font-semibold">
                    {{ weekDays[i] }}<br><span class="text-xs">{{ fmt(d) }}</span>
                  </th>
                  <th class="py-3 px-6 font-semibold">Total</th>
                  <th class="py-3 px-6"></th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-for="(r,ri) in rows" :key="ri" class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <td class="py-3 px-6">
                    <div v-if="r.contract_id">#{{ getProj(r.contract_id)?.code }} — {{ getProj(r.contract_id)?.name }}</div>
                    <div v-else class="text-orange-700">Non-Chargeable: {{ r.description }}</div>
                  </td>
                  <td v-for="(d,di) in days" :key="di" class="py-2 px-2">
                    <input :disabled="isSaturday(d) || isSunday(d) || isHoliday(d)" type="number" min="0" max="10" step="0.5" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white" v-model.number="r.hours[di]" @input="clamp(r, di)">
                  </td>
                  <td class="px-6 font-semibold">{{ rowTotal(r).toFixed(1) }}</td>
                  <td><button class="text-xs underline text-gray-600 hover:text-gray-900" @click="removeRow(ri)">Remove</button></td>
                </tr>
                <tr class="border-t bg-gray-50">
                  <td class="py-3 px-6 font-semibold">Total time</td>
                  <td v-for="(d,di) in days" :key="'t'+di" class="py-3 px-6 font-semibold" :class="dayTotal(di)>10 ? 'text-red-600' : ''">{{ dayTotal(di).toFixed(1) }}</td>
                  <td class="py-3 px-6 font-semibold">{{ grandTotal.toFixed(1) }}</td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="flex gap-3 mt-8">
            <button class="px-6 py-2 bg-gray-600 text-white font-bold rounded-md hover:bg-gray-700 transition duration-300 shadow-md hover:shadow-lg" @click="save(false)">Save</button>
            <button class="px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg" @click="save(true)">
              <i class="fas fa-paper-plane mr-2"></i>Save and Submit
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { useAuth } from '../../store'

const auth = useAuth()

const start = ref(weekStart(new Date()))
const end = computed(() => addDays(start.value, 6))
const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const days = computed(() => Array.from({ length: 7 }, (_, i) => addDays(start.value, i)))

const me = ref(null)
const managerName = computed(() => me.value?.manager?.username || '—')
const projects = ref([])
const holidays = ref([])
const holidayText = computed(() => holidays.value.filter(h => between(parseISO(h.date), start.value, end.value)).map(h => h.name).join(', '))

const submitted = ref(false)
const rows = ref([])
const newRow = ref({ contract_id: '', description: '' })
const ncType = ref('')
const ncDetail = ref('')

function addRow() {
  if (!newRow.value.contract_id) return
  rows.value.push({ contract_id: Number(newRow.value.contract_id), description: newRow.value.description, hours: Array(7).fill(0) })
  newRow.value = { contract_id: '', description: '' }
}
function addNC() {
  if (!ncType.value) return
  rows.value.push({ contract_id: null, description: `${ncType.value}${ncDetail.value ? ' - ' + ncDetail.value : ''}`, hours: Array(7).fill(0) })
  ncType.value = ''
  ncDetail.value = ''
}
function removeRow(i) { rows.value.splice(i, 1) }
function getProj(id) { return projects.value.find(p => p.id === id) }
function fmt(d) { return d.toISOString().slice(0, 10) }
function isSaturday(d) { return d.getUTCDay() === 6 }
function isSunday(d) { return d.getUTCDay() === 0 }
function isHoliday(d) { return holidays.value.some(h => h.date === fmt(d)) }
function clamp(r, di) {
  let v = Number(r.hours[di] || 0)
  v = Math.max(0, Math.min(10, Math.round(v * 2) / 2))
  r.hours[di] = v
}
function rowTotal(r) { return r.hours.reduce((s, x) => s + Number(x || 0), 0) }
function dayTotal(di) { return rows.value.reduce((s, r) => s + Number(r.hours[di] || 0), 0) }
const grandTotal = computed(() => rows.value.reduce((s, r) => s + rowTotal(r), 0))

function addDays(d, n) {
  const x = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + n))
  return x
}
function parseISO(s) {
  const [y, m, dd] = s.split('-').map(Number)
  return new Date(Date.UTC(y, m - 1, dd))
}
function between(d, a, b) { return d >= a && d <= b }
function weekStart(d0) {
  const d = new Date(Date.UTC(d0.getUTCFullYear(), d0.getUTCMonth(), d0.getUTCDate()))
  const day = (d.getUTCDay() + 6) % 7
  d.setUTCDate(d.getUTCDate() - day)
  return d
}
function shift(n) { start.value = addDays(start.value, n); loadWeek() }
function toCurrent() { start.value = weekStart(new Date()); loadWeek() }
const weekNumber = computed(() => {
  const d = new Date(Date.UTC(start.value.getUTCFullYear(), start.value.getUTCMonth(), start.value.getUTCDate() + 3))
  const first = new Date(Date.UTC(d.getUTCFullYear(), 0, 4))
  const week = 1 + Math.round(((d - first) / 86400000 - 3 + ((first.getUTCDay() + 6) % 7)) / 7)
  return String(week).padStart(2, '0')
})

async function loadWeek() {
  rows.value = []
  submitted.value = false
  const { data } = await api.get('/api/hr/my/timesheets/week', { params: { start: fmt(start.value) } })
  if (Array.isArray(data)) {
    const key = (e) => `${e.contract_id || 'NC'}|${e.description || ''}`
    const map = new Map()
    for (const e of data) {
      const idx = Math.round((new Date(e.work_date + 'T00:00:00Z') - start.value) / 86400000)
      if (idx < 0 || idx > 6) continue
      const k = key(e)
      if (!map.has(k)) map.set(k, { contract_id: e.contract_id, description: e.description || '', hours: Array(7).fill(0) })
      map.get(k).hours[idx] += Number(e.hours_worked)
      if (e.submitted) submitted.value = true
    }
    rows.value = Array.from(map.values())
  }
}

async function save(andSubmit) {
  for (let di = 0; di < 7; di++) {
    const d = days.value[di]
    if (isSunday(d) && dayTotal(di) > 0) { alert('Sunday not allowed'); return }
    if (isHoliday(d) && dayTotal(di) > 0) { alert('Public holiday not allowed'); return }
    if (dayTotal(di) > 10) { alert('Daily total cannot exceed 10h'); return }
  }
  const items = []
  for (const r of rows.value) {
    for (let di = 0; di < 7; di++) {
      const v = Number(r.hours[di] || 0)
      if (v <= 0) continue
      items.push({ work_date: fmt(days.value[di]), hours_worked: v, contract_id: r.contract_id, description: r.description })
    }
  }
  if (items.length === 0) { alert('Nothing to save'); return }
  await api.post('/api/hr/my/timesheets/bulk', items, { params: { submitted: andSubmit ? 'true' : 'false' } })
  if (andSubmit) {
    await api.put('/api/hr/my/timesheets/submit-week', null, { params: { start: fmt(start.value) } })
  }
  await loadWeek()
}

onMounted(async () => {
  try { me.value = (await api.get('/api/users/me')).data } catch {}
  try { projects.value = (await api.get('/api/projects/active')).data } catch {}
  try { holidays.value = (await api.get('/api/admin/holidays')).data } catch {}
  await loadWeek()
})
</script>

<style scoped>
/*
  Font Awesome for the icon. You would need to include the library in your project.
  No other custom styles needed as Tailwind CSS handles everything.
*/
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>