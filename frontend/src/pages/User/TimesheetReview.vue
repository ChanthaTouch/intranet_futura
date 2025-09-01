<template>
  <div class="space-y-8 p-6 md:p-10 bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen font-inter flex-1">
    <h1 class="text-3xl font-bold text-black text-shadow-sm">Team Timesheets — Review</h1>
    <div class="card bg-white rounded-2xl shadow-xl p-6">
      <div class="text-sm text-gray-600 mb-4">Pending/submitted entries from your direct reports.</div>
      <div v-if="loading" class="text-sm text-black">Loading…</div>
      <table v-else class="w-full text-sm text-black">
        <thead class="bg-gray-50 text-xs uppercase tracking-wider text-gray-600">
          <tr>
            <th class="p-4 text-left font-semibold text-shadow-xs">Date</th>
            <th class="p-4 text-left font-semibold text-shadow-xs">User</th>
            <th class="p-4 text-left font-semibold text-shadow-xs">Hours</th>
            <th class="p-4 text-left font-semibold text-shadow-xs">Project</th>
            <th class="p-4 text-left font-semibold text-shadow-xs">Description</th>
            <th class="p-4 text-left font-semibold text-shadow-xs">Status</th>
            <th class="p-4 text-left font-semibold text-shadow-xs"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id" class="border-t border-gray-200 hover:bg-gray-50 transition-colors duration-200">
            <td class="p-4">{{ r.work_date }}</td>
            <td class="p-4">{{ r.user }}</td>
            <td class="p-4">{{ r.hours_worked }}</td>
            <td class="p-4"><span v-if="r.contract_id">#{{ r.contract_id }}</span></td>
            <td class="p-4 max-w-[32rem] truncate">{{ r.description }}</td>
            <td class="p-4"><span :class="badge(r.status)">{{ r.status }}</span></td>
            <td class="p-4 space-x-3">
              <button class="btn" @click="approve(r)" v-if="r.status !== 'approved'">
                <i class="fas fa-check mr-2 text-gray-600"></i>Approve
              </button>
              <button class="btn" @click="reject(r)" v-if="r.status !== 'rejected'">
                <i class="fas fa-times mr-2 text-gray-600"></i>Reject
              </button>
            </td>
          </tr>
          <tr v-if="rows.length === 0">
            <td colspan="7" class="p-4 text-center text-gray-500">No timesheet entries found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const rows = ref([])
const loading = ref(true)

const badge = (s) => 
  'inline-block px-3 py-1 rounded-full text-xs font-medium capitalize ' +
  (s === 'approved' ? 'text-green-800 bg-green-100' :
   s === 'rejected' ? 'text-red-700 bg-red-100' :
   'text-black bg-gray-200')

async function load() {
  loading.value = true
  try {
    rows.value = (await api.get('/api/hr/team/timesheets')).data
  } finally {
    loading.value = false
  }
}

async function approve(r) {
  await api.put(`/api/hr/timesheets/${r.id}/approve`)
  await load()
}

async function reject(r) {
  await api.put(`/api/hr/timesheets/${r.id}/reject`)
  await load()
}

onMounted(load)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.font-inter {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.card {
  @apply bg-white border border-gray-200 rounded-2xl shadow-xl;
}

.btn {
  @apply inline-flex items-center justify-center px-4 py-2 text-sm text-black bg-white border border-gray-300 rounded-lg shadow-sm
         hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-200;
}

.text-shadow-sm {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.text-shadow-xs {
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
}

.fa-solid, .fa-regular {
  transition: color 0.2s ease;
}

.text-red-700 {
  color: #b91c1c;
}

.text-green-800 {
  color: #15803d;
}

.bg-green-100 {
  background-color: #dcfce7;
}

.bg-red-100 {
  background-color: #fee2e2;
}

.bg-gray-50 {
  background-color: #f9fafb;
}

.bg-gray-200 {
  background-color: #e5e7eb;
}

.text-sm {
  font-size: 0.875rem;
}

.font-semibold {
  font-weight: 600;
}

.space-y-8 > * + * {
  margin-top: 2rem;
}

.p-6 {
  padding: 1.5rem;
}

.border-t {
  border-top: 1px solid #e5e7eb;
}

.space-x-3 > * + * {
  margin-left: 0.75rem;
}
</style>