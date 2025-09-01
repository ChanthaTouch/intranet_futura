<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300">
    <div class="w-full p-4 mx-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">
            <i class="fas fa-list-check mr-2 text-blue-500"></i>
            Mission Request
          </h2>
        </div>

        <div class="p-6 rounded-lg bg-gray-50 shadow-inner">
          <form @submit.prevent="submit" class="flex flex-col md:flex-row items-end gap-4">
            <div class="flex-1 w-full">
              <label for="title" class="block text-gray-700 mb-1">Title</label>
              <input
                type="text"
                id="title"
                v-model="formData.title"
                placeholder="e.g., Prepare Monthly Report"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                required
              />
            </div>

            <div class="flex-1 w-full">
              <label for="description" class="block text-gray-700 mb-1">Description</label>
              <textarea
                id="description"
                v-model="formData.description"
                placeholder="e.g., Prepare financial report for August"
                rows="4"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                required
              ></textarea>
            </div>

            <div class="flex-1 w-full">
              <label for="startDate" class="block text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                id="startDate"
                v-model="formData.startDate"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                required
              />
            </div>

          
          </form>

          <form @submit.prevent="submit" class="flex flex-col md:flex-row items-end gap-4 mt-4">
            <div class="flex-1 w-full">
              <label for="endDate" class="block text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                id="endDate"
                v-model="formData.endDate"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                required
              />
            </div>

            <div class="flex-1 w-full">
              <label for="priority" class="block text-gray-700 mb-1">Priority</label>
              <select
                id="priority"
                v-model="formData.priority"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                required
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div class="flex-1 w-full">
              <label for="status" class="block text-gray-700 mb-1">Status</label>
              <select
                id="status"
                v-model="formData.status"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                required
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </form>

          <div class="flex justify-end gap-4 mt-4">
            <button
              type="button"
              @click="clearForm"
              class="px-6 py-2 bg-gray-600 text-white font-bold rounded-md hover:bg-gray-700 transition duration-300 shadow-md hover:shadow-lg"
            >
              Clear
            </button>
              <div class="w-full md:w-auto">
              <button
                type="submit"
                :disabled="isSubmitting"
                class="w-full md:w-auto px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg disabled:bg-blue-400 disabled:cursor-not-allowed"
              >
                Submit
              </button>
            </div>
          </div>

          <div v-if="successMessage" class="mt-4 p-4 bg-green-100 text-green-700 rounded-md">
            {{ successMessage }}
          </div>
        </div>

        <div class="mt-8">
          <div class="overflow-x-auto bg-white rounded-lg shadow">
            <table class="min-w-full table-auto text-sm">
              <thead class="bg-gray-200 text-gray-600 uppercase leading-normal">
                <tr>
                  <th class="py-3 px-6 text-left">Title</th>
                  <th class="py-3 px-6 text-left">Description</th>
                  <th class="py-3 px-6 text-left">Start Date</th>
                  <th class="py-3 px-6 text-left">End Date</th>
                  <th class="py-3 px-6 text-left">Priority</th>
                  <th class="py-3 px-6 text-center">Status</th>
                  <th class="py-3 px-6 text-center">HR Status</th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-if="missions.length === 0">
                  <td colspan="7" class="py-4 text-center">No missions submitted yet.</td>
                </tr>
                <tr
                  v-for="mission in missions"
                  :key="mission.id"
                  class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200"
                >
                  <td class="py-3 px-6 text-left">{{ mission.title }}</td>
                  <td class="py-3 px-6 text-left">{{ mission.description }}</td>
                  <td class="py-3 px-6 text-left">{{ mission.startDate }}</td>
                  <td class="py-3 px-6 text-left">{{ mission.endDate }}</td>
                  <td class="py-3 px-6 text-left">{{ mission.priority }}</td>
                  <td class="py-3 px-6 text-center">
                    <span
                      class="py-1 px-3 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-green-200 text-green-600': mission.status === 'completed',
                        'bg-red-200 text-red-600': mission.status === 'pending',
                        'bg-yellow-200 text-yellow-600': mission.status === 'in_progress',
                      }"
                    >
                      {{ mission.status }}
                    </span>
                  </td>
                  <td class="py-3 px-6 text-center">
                    <span
                      class="py-1 px-3 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-green-200 text-green-600': mission.hrStatus === 'Approved',
                        'bg-red-200 text-red-600': mission.hrStatus === 'Rejected',
                        'bg-yellow-200 text-yellow-600': mission.hrStatus === 'Pending',
                      }"
                    >
                      {{ mission.hrStatus }}
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
import { reactive, ref } from 'vue'
import api from '../../api'

const formData = reactive({
  title: '',
  description: '',
  startDate: '',
  endDate: '',
  priority: 'low',
  status: 'pending',
  hrStatus: 'Pending'
})

const missions = ref([])
const isSubmitting = ref(false)
const successMessage = ref('')

async function submit() {
  if (!formData.title || !formData.description || !formData.startDate || !formData.endDate || !formData.priority || !formData.status) {
    alert('Please fill out all required fields.')
    return
  }

  isSubmitting.value = true
  successMessage.value = ''

  try {
    await api.post('/api/helpdesk/tickets', {
      title: `Other Request: ${formData.title}`,
      description: formData.description,
      startDate: formData.startDate,
      endDate: formData.endDate,
      priority: formData.priority,
      status: formData.status,
      hrStatus: formData.hrStatus
    })

    missions.value.push({
      ...formData,
      id: Date.now()
    })

    successMessage.value = 'Mission submitted to HR successfully!'
    clearForm()
  } catch (error) {
    alert('An error occurred while submitting the mission to HR. Please try again.')
    console.error(error)
  } finally {
    isSubmitting.value = false
  }
}

function clearForm() {
  formData.title = ''
  formData.description = ''
  formData.startDate = ''
  formData.endDate = ''
  formData.priority = 'low'
  formData.status = 'pending'
  formData.hrStatus = 'Pending'
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>