<template>
  <!-- Main container with full screen width and height -->
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300 w-full h-full">
    <!-- Inner container to handle overflow and flexible growth -->
    <div class="w-full p-0 mx-auto flex-grow overflow-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg h-full">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h1 class="text-2xl font-bold text-gray-800 flex items-center">
            <i class="fas fa-list-check mr-3 text-blue-500"></i>Request Records
          </h1>
        </div>

        <!-- Loading and Error States -->
        <div v-if="loading" class="text-center p-4">
          <p class="text-blue-500 font-semibold">Loading request records...</p>
        </div>
        <div v-if="error" class="text-center p-4 text-red-500 font-semibold">
          <p>Failed to load data. Please check your network connection and API server.</p>
        </div>

        <!-- Request Records Table -->
        <div class="mt-8" v-if="!loading && !error">
          <div class="overflow-x-auto bg-white rounded-lg shadow">
            <table class="min-w-full table-auto text-sm">
              <thead class="bg-gray-200 text-gray-600 uppercase leading-normal">
                <tr>
                  <th class="py-3 px-6 text-left font-semibold">Title</th>
                  <th class="py-3 px-6 text-left font-semibold">Description</th>
                  <th class="py-3 px-6 text-left font-semibold">Quantity</th>
                  <th class="py-3 px-6 text-left font-semibold">Deadline</th>
                  <th class="py-3 px-6 text-left font-semibold">BOQ</th>
                  <th class="py-3 px-6 text-center font-semibold">Status</th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-if="rows.length === 0">
                  <td colspan="6" class="py-4 text-center text-gray-600">No request records found.</td>
                </tr>
                <tr v-for="row in rows" :key="row.id" class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <td class="py-3 px-6">{{ row.title }}</td>
                  <td class="py-3 px-6">{{ row.description }}</td>
                  <td class="py-3 px-6">{{ row.quantity }}</td>
                  <td class="py-3 px-6">{{ row.deadline }}</td>
                  <td class="py-3 px-6">{{ row.boq ? 'Attached' : 'None' }}</td>
                  <td class="py-3 px-6 text-center">
                    <span class="py-1 px-3 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-yellow-200 text-yellow-600': row.status === 'Pending',
                        'bg-green-200 text-green-600': row.status === 'Approved',
                        'bg-red-200 text-red-600': row.status === 'Rejected'
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
async function fetchRequestRecords() {
  loading.value = true;
  error.value = false;
  try {
    const response = await api.get('/tickets/');
    rows.value = response.data.map(request => ({
      ...request,
      boq: request.boq ? request.boq : null
    }));
  } catch (err) {
    console.error("Failed to load request records:", err);
    error.value = true;
  } finally {
    loading.value = false;
  }
}

// --- Lifecycle Hook ---
onMounted(() => {
  fetchRequestRecords();
});
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>