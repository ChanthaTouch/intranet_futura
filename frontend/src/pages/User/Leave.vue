<template>
  <!-- Main container with full screen width and height -->
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300 w-full h-full">
    <!-- Inner container to handle overflow and flexible growth -->
    <div class="w-full p-0 mx-auto flex-grow overflow-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg h-full">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <!-- Title with icon, similar to Recruitment.vue -->
          <h1 class="text-2xl font-bold text-gray-800 flex items-center">
            <i class="fas fa-plane-departure mr-3 text-blue-500"></i>Leave Request Form
          </h1>
        </div>
        
        <!-- Notification/Message Box -->
        <transition name="fade">
          <div v-if="message" :class="['p-4 rounded-lg shadow-md mb-6 transition-all duration-300 ease-in-out', messageType === 'success' ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-red-100 text-red-700 border border-red-300']" role="alert">
            <div class="flex items-start">
              <i :class="['fas mr-3 mt-1 text-lg', messageType === 'success' ? 'fa-check-circle text-green-500' : 'fa-exclamation-circle text-red-500']"></i>
              <div class="flex-grow">
                <p class="font-semibold">{{ message }}</p>
              </div>
            </div>
          </div>
        </transition>

        <!-- Leave Request Form -->
        <div class="p-6 rounded-lg bg-gray-50 shadow-inner w-full">
          <form @submit.prevent="create" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <label for="start_date" class="block text-gray-700 font-medium mb-2">Start Date</label>
              <input type="date" id="start_date" v-model="f.start_date" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required/>
            </div>
            <div>
              <label for="end_date" class="block text-gray-700 font-medium mb-2">End Date</label>
              <input type="date" id="end_date" v-model="f.end_date" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required/>
            </div>
            <div>
              <label for="leave_type" class="block text-gray-700 font-medium mb-2">Leave Type</label>
              <select id="leave_type" v-model="f.leave_type" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white">
                <option value="annual">Annual</option>
                <option value="sick">Sick</option>
                <option value="unpaid">Unpaid</option>
                <option value="maternity">Maternity</option>
              </select>
            </div>
            <div>
              <label for="days" class="block text-gray-700 font-medium mb-2">Days</label>
              <input type="number" id="days" v-model="f.days" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required/>
            </div>
            <div class="col-span-full">
              <label for="reason" class="block text-gray-700 font-medium mb-2">Reason</label>
              <textarea id="reason" v-model="f.reason" rows="3" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required></textarea>
            </div>
            
            <div class="col-span-full mt-4 flex justify-end">
              <button type="submit" class="w-full md:w-auto px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg">
                <i class="fas fa-paper-plane mr-2"></i>Submit Request
              </button>
            </div>
          </form>
        </div>

        <!-- Leave Requests Table -->
        <div class="mt-8">
          <div class="overflow-x-auto bg-white rounded-lg shadow">
            <table class="min-w-full table-auto text-sm">
              <thead class="bg-gray-200 text-gray-600 uppercase leading-normal">
                <tr>
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
                  <td colspan="6" class="py-4 text-center text-gray-600">No leave requests found.</td>
                </tr>
                <tr v-for="row in rows" :key="row.id" class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
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

// --- Axios API Instance ---
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Reactive State ---
const rows = ref([]);
const f = ref({
  user_id: 1,
  start_date: '',
  end_date: '',
  leave_type: 'annual',
  reason: '',
  days: null // Use null for initial value to allow validation
});
const message = ref('');
const messageType = ref('success');

// --- Helper Functions ---
function badge(s) {
  return {
    'bg-yellow-200 text-yellow-600': s === 'pending',
    'bg-green-200 text-green-600': s === 'approved',
    'bg-red-200 text-red-600': s === 'rejected',
  };
}

function showNotification(msg, type = 'success', duration = 3000) {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, duration);
}

// --- Data Fetching and Submission ---
async function load() {
  try {
    const response = await api.get('/leave-requests/');
    rows.value = response.data;
  } catch (error) {
    console.error("Failed to load leave requests:", error);
    showNotification('Failed to load leave requests. Please check the backend server.', 'error');
  }
}

async function create() {
  try {
    // Frontend validation
    if (!f.value.start_date || !f.value.end_date || !f.value.reason || f.value.days === null) {
      showNotification('Please fill in all required fields.', 'error');
      return;
    }
    if (new Date(f.value.start_date) > new Date(f.value.end_date)) {
      showNotification('Start date must be before or the same as the end date.', 'error');
      return;
    }
    
    // The payload now correctly uses snake_case keys and includes the days field
    const payload = {
      user_id: f.value.user_id,
      start_date: f.value.start_date,
      end_date: f.value.end_date,
      leave_type: f.value.leave_type,
      reason: f.value.reason,
      days: f.value.days,
    };

    console.log("Sending payload:", payload);

    await api.post('/leave-requests/', payload);
    
    // Clear form and show success message
    f.value = { start_date: '', end_date: '', leave_type: 'annual', reason: '', days: null };
    showNotification('Leave request submitted successfully!', 'success');
    
    // Reload the data from the backend to update the table
    await load();
  } catch (error) {
    console.error("Failed to create leave request:", error);
    showNotification('Failed to submit leave request. Please check the backend server.', 'error');
  }
}

// --- Lifecycle Hook ---
onMounted(() => {
  load();
});

</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

/* Optional: Adds a nice fade-in/fade-out transition for the notification box */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
