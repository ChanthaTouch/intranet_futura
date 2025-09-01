<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300 w-full h-full">
    <div class="w-full p-0 mx-auto flex-grow overflow-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg h-full">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mr-3 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
            </svg>
            Recruitment Records
          </h2>
          <router-link to="/recruitment" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-300">
            Back to Recruitment Management
          </router-link>
        </div>

        <!-- Loading & Error Messages -->
        <div v-if="loading" class="text-center p-4">
          <p class="text-blue-500 font-semibold">Loading records...</p>
        </div>
        <div v-if="error" class="text-center p-4 text-red-500 font-semibold">
          <p>Error: {{ error }}</p>
          <p>Please ensure the API is running at http://127.0.0.1:8000</p>
        </div>

        <!-- Table Section -->
        <div class="mt-8">
          <div class="overflow-x-auto bg-white rounded-lg shadow">
            <table class="min-w-full table-auto text-sm">
              <thead class="bg-gray-200 text-gray-600 uppercase leading-normal">
                <tr>
                  <th class="py-3 px-6 text-left font-semibold">Name</th>
                  <th class="py-3 px-6 text-left font-semibold">Position</th>
                  <th class="py-3 px-6 text-left font-semibold">Project</th>
                  <th class="py-3 px-6 text-left font-semibold">Hiring Manager</th>
                  <th class="py-3 px-6 text-left font-semibold">Request Date</th>
                  <th class="py-3 px-6 text-left font-semibold">Start Date</th>
                  <th class="py-3 px-6 text-center font-semibold">Status</th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-if="records.length === 0">
                  <td colspan="7" class="py-4 text-center text-gray-600">No records available.</td>
                </tr>
                <tr v-for="record in records" :key="record.id"
                  class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <td class="py-3 px-6">{{ record.name }}</td>
                  <td class="py-3 px-6">{{ record.position }}</td>
                  <td class="py-3 px-6">{{ record.project }}</td>
                  <td class="py-3 px-6">{{ record.hiring_manager }}</td>
                  <td class="py-3 px-6">{{ formatDate(record.request_date) }}</td>
                  <td class="py-3 px-6">{{ formatDate(record.start_date) }}</td>
                  <td class="py-3 px-6 text-center">
                    <span class="py-1 px-3 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-green-200 text-green-600': record.status === 'Approved',
                        'bg-red-200 text-red-600': record.status === 'Rejected',
                        'bg-yellow-200 text-yellow-600': record.status === 'Pending'
                      }">
                      {{ record.status }}
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
import { ref, onMounted } from "vue";

const API_BASE_URL = "http://127.0.0.1:8000/recruitments/";
const records = ref([]);
const loading = ref(false);
const error = ref(null);

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toISOString().split("T")[0]; // Format as YYYY-MM-DD
};

const fetchRecords = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch(API_BASE_URL);
    if (!response.ok) throw new Error("Failed to fetch records from http://127.0.0.1:8000/recruitments/");
    records.value = await response.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

onMounted(fetchRecords);
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>