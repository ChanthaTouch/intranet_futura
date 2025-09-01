<template>
  <!-- Main container with full screen width and height -->
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300 w-full h-full">
    <!-- Inner container to handle overflow and flexible growth -->
    <div class="w-full p-0 mx-auto flex-grow overflow-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg h-full">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h1 class="text-2xl font-bold text-gray-800 flex items-center">
            <i class="fas fa-list-alt mr-3 text-green-500"></i>Leave Records
          </h1>
        </div>

        <!-- Loading and Error States -->
        <div v-if="loading" class="text-center p-4">
          <p class="text-blue-500 font-semibold">Loading leave records...</p>
        </div>
        <div v-if="error" class="text-center p-4 text-red-500 font-semibold">
          <p>Failed to load data. Please check your network connection and API server.</p>
        </div>

        <!-- Leave Records Table -->
        <div class="mt-8" v-if="!loading && !error">
          <div class="overflow-x-auto bg-white rounded-lg shadow">
            <table class="min-w-full table-auto text-sm">
              <thead class="bg-gray-200 text-gray-600 uppercase leading-normal">
                <tr>
                  <th class="py-3 px-6 text-left font-semibold">User ID</th>
                  <th class="py-3 px-6 text-left font-semibold">Start Date</th>
                  <th class="py-3 px-6 text-left font-semibold">End Date</th>
                  <th class="py-3 px-6 text-left font-semibold">Type</th>
                  <th class="py-3 px-6 text-left font-semibold">Reason</th>
                  <th class="py-3 px-6 text-left font-semibold">Days</th>
                  <th class="py-3 px-6 text-center font-semibold">Status</th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-if="rows.length === 0">
                  <td colspan="7" class="py-4 text-center text-gray-600">No leave records found.</td>
                </tr>
                <tr v-for="row in rows" :key="row.id" class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <td class="py-3 px-6">{{ row.user_id }}</td>
                  <td class="py-3 px-6">{{ row.start_date }}</td>
                  <td class="py-3 px-6">{{ row.end_date }}</td>
                  <td class="py-3 px-6">{{ row.leave_type }}</td>
                  <td class="py-3 px-6">{{ row.reason }}</td>
                  <td class="py-3 px-6">{{ row.days }}</td>
                  <td class="py-3 px-6 text-center">
                    <span class="py-1 px-3 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-yellow-200 text-yellow-600': row.status === 'pending',
                        'bg-green-200 text-green-600': row.status === 'approved',
                        'bg-red-200 text-red-600': row.status === 'rejected'
                      }">
                      {{ row.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// --- Reactive State ---
const rows = ref([]);
const loading = ref(true);
const error = ref(false);

// --- Axios API Instance ---
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Data Fetching ---
async function fetchLeaveRecords() {
  loading.value = true;
  error.value = false;
  try {
    const response = await api.get('/leave-requests/');
    rows.value = response.data;
  } catch (err) {
    console.error("Failed to load leave records:", err);
    error.value = true;
  } finally {
    loading.value = false;
  }
}

// --- Lifecycle Hook ---
onMounted(() => {
  fetchLeaveRecords();
});
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>
