<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300">
    <div class="w-full p-4 mx-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">
            <i class="fas fa-list-check mr-2 text-blue-500"></i>
            Other Request
          </h2>
        </div>

        <div class="p-6 rounded-lg bg-gray-50 shadow-inner">
          <form @submit.prevent="submit" class="flex flex-col gap-4">
            <div class="flex flex-col md:flex-row gap-4">
              <div class="flex-1 w-full">
                <label for="title" class="block text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  id="title"
                  v-model="formData.title"
                  placeholder="Title"
                  class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  required
                />
              </div>

              <div class="flex-1 w-full">
                <label for="description" class="block text-gray-700 mb-1">Description</label>
                <textarea
                  id="description"
                  v-model="formData.description"
                  placeholder="Describe your request"
                  rows="4"
                  class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  required
                ></textarea>
              </div>
            </div>

            <div class="flex flex-col md:flex-row gap-4">
              <div class="flex-1 w-full">
                <label for="quantity" class="block text-gray-700 mb-1">Quantity</label>
                <input
                  type="number"
                  id="quantity"
                  v-model.number="formData.quantity"
                  placeholder="Quantity (e.g., 50 bags of cement)"
                  min="1"
                  class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  required
                />
              </div>

              <div class="flex-1 w-full">
                <label for="deadline" class="block text-gray-700 mb-1">Deadline</label>
                <input
                  type="date"
                  id="deadline"
                  v-model="formData.deadline"
                  class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  required
                />
              </div>

              <div class="flex-1 w-full">
                <label for="boqFile" class="block text-gray-700 mb-1">BOQ Attachment</label>
                <input
                  type="file"
                  id="boqFile"
                  ref="boqFile"
                  accept=".pdf,.doc,.docx"
                  class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                />
              </div>
            </div>

            <div class="flex justify-end gap-4">
              <button
                type="button"
                @click="clearForm"
                class="px-6 py-2 bg-gray-600 text-white font-bold rounded-md hover:bg-gray-700 transition duration-300 shadow-md hover:shadow-lg"
              >
                Clear
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg disabled:bg-blue-400 disabled:cursor-not-allowed"
              >
                Submit
              </button>
            </div>
          </form>

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
                  <th class="py-3 px-6 text-left">Quantity</th>
                  <th class="py-3 px-6 text-left">Deadline</th>
                  <th class="py-3 px-6 text-left">BOQ</th>
                  <th class="py-3 px-6 text-center">Status</th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-if="requests.length === 0">
                  <td colspan="6" class="py-4 text-center">No requests submitted yet.</td>
                </tr>
                <tr
                  v-for="request in requests"
                  :key="request.id"
                  class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200"
                >
                  <td class="py-3 px-6 text-left">{{ request.title }}</td>
                  <td class="py-3 px-6 text-left">{{ request.description }}</td>
                  <td class="py-3 px-6 text-left">{{ request.quantity }}</td>
                  <td class="py-3 px-6 text-left">{{ request.deadline }}</td>
                  <td class="py-3 px-6 text-left">{{ request.boq ? 'Attached' : 'None' }}</td>
                  <td class="py-3 px-6 text-center">
                    <span
                      class="py-1 px-3 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-green-200 text-green-600': request.status === 'Approved',
                        'bg-red-200 text-red-600': request.status === 'Rejected',
                        'bg-yellow-200 text-yellow-600': request.status === 'Pending',
                      }"
                    >
                      {{ request.status }}
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
import { reactive, ref, onMounted } from 'vue'
import axios from 'axios'

const formData = reactive({
  title: '',
  description: '',
  quantity: null,
  deadline: '',
  boq: null,
  status: 'Pending'
})

const requests = ref([])
const boqFile = ref(null)
const isSubmitting = ref(false)
const successMessage = ref('')

// Fetch requests from the API on component mount
onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/tickets/')
    requests.value = response.data.map(request => ({
      ...request,
      boq: request.boq ? request.boq : null
    }))
  } catch (error) {
    console.error('Error fetching requests:', error)
    alert('Failed to load requests. Please try again later.')
  }
})

async function submit() {
  if (!formData.title || !formData.description || !formData.quantity || !formData.deadline) {
    alert('Please fill out all required fields.')
    return
  }

  isSubmitting.value = true
  successMessage.value = ''

  try {
    const formDataToSend = new FormData()
    formDataToSend.append('title', `Other Request: ${formData.title}`)
    formDataToSend.append('description', formData.description)
    formDataToSend.append('quantity', formData.quantity)
    formDataToSend.append('deadline', formData.deadline)
    formDataToSend.append('status', formData.status)
    if (boqFile.value?.files[0]) {
      formDataToSend.append('boq', boqFile.value.files[0])
    }
    formDataToSend.append('priority', 'normal')

    const response = await axios.post('http://127.0.0.1:8000/tickets/', formDataToSend, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    requests.value.push({
      ...response.data,
      boq: boqFile.value?.files[0] ? boqFile.value.files[0].name : null
    })

    successMessage.value = 'Request submitted successfully!'
    clearForm()
  } catch (error) {
    alert('An error occurred while submitting the request. Please try again.')
    console.error(error)
  } finally {
    isSubmitting.value = false
  }
}

function clearForm() {
  formData.title = ''
  formData.description = ''
  formData.quantity = null
  formData.deadline = ''
  formData.boq = null
  if (boqFile.value) boqFile.value.value = ''
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>