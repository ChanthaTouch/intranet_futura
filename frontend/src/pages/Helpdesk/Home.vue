<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300">
    <div class="w-full p-4 mx-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h3 class="text-xl font-bold text-gray-800">
            <i class="fas fa-headset mr-2 text-blue-500"></i>Helpdesk
          </h3>
        </div>
        <div class="p-6 rounded-lg bg-gray-50 shadow-inner">
          <form @submit.prevent="create" class="grid md:grid-cols-3 gap-6">
            <div>
              <label class="block text-gray-700 mb-1">Title</label>
              <input v-model="title" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white" placeholder="Title" />
            </div>
            <div>
              <label class="block text-gray-700 mb-1">Description</label>
              <input v-model="desc" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white" placeholder="Description" />
            </div>
            <div>
              <label class="block text-gray-700 mb-1">Priority</label>
              <select v-model="priority" class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div class="md:col-span-3 flex justify-end gap-3">
              <button class="px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg" type="submit">
                <i class="fas fa-paper-plane mr-2"></i>Submit
              </button>
            </div>
          </form>
        </div>
        <div class="mt-8">
          <div class="overflow-x-auto bg-white rounded-lg shadow">
            <table class="min-w-full table-auto text-sm">
              <thead class="bg-gray-200 text-gray-600 uppercase leading-normal">
                <tr>
                  <th class="py-3 px-6 text-left font-semibold">ID</th>
                  <th class="py-3 px-6 text-left font-semibold">Title</th>
                  <th class="py-3 px-6 text-left font-semibold">Priority</th>
                  <th class="py-3 px-6 text-left font-semibold">Status</th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-if="items.length === 0">
                  <td colspan="4" class="py-4 text-center text-gray-600">No tickets found.</td>
                </tr>
                <tr v-for="t in items" :key="t.id" class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <td class="py-3 px-6">{{ t.id }}</td>
                  <td class="py-3 px-6">{{ t.title }}</td>
                  <td class="py-3 px-6">{{ t.priority }}</td>
                  <td class="py-3 px-6">{{ t.status }}</td>
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
import { ref, onMounted } from 'vue'
import api from '../../api'

const title = ref('')
const desc = ref('')
const priority = ref('normal')
const items = ref([])

async function load() {
  const { data } = await api.get('/api/helpdesk/tickets')
  items.value = data
}

async function create() {
  await api.post('/api/helpdesk/tickets', { title: title.value, description: desc.value, priority: priority.value })
  title.value = ''
  desc.value = ''
  await load()
}

onMounted(load)
</script>

<style scoped>
/*
  Font Awesome for the icon. You would need to include the library in your project.
  No other custom styles needed as Tailwind CSS handles everything.
*/
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>