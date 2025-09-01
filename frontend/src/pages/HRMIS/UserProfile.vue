<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300">
    <div class="w-full p-4 mx-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">
            <i class="fas fa-user mr-2 text-blue-500"></i>
            User Profiles
          </h2>
        </div>

        <div class="mt-8">
          <div class="overflow-x-auto bg-white rounded-lg shadow">
            <table class="min-w-full table-auto text-sm">
              <thead class="bg-gray-200 text-gray-600 uppercase leading-normal">
                <tr>
                  <th class="py-3 px-6 text-left">Full Name</th>
                  <th class="py-3 px-6 text-left">Phone</th>
                  <th class="py-3 px-6 text-left">Full Name (KH)</th>
                  <th class="py-3 px-6 text-left">Gender</th>
                  <th class="py-3 px-6 text-left">Email</th>
                  <th class="py-3 px-6 text-left">Position</th>
                  <th class="py-3 px-6 text-left">Skills</th>
                  <th class="py-3 px-6 text-left">Department</th>
                  <th class="py-3 px-6 text-left">Profile</th>
                  <th class="py-3 px-6 text-left">Address</th>
                  <th class="py-3 px-6 text-left">City</th>
                  <th class="py-3 px-6 text-left">Country</th>
                  <th class="py-3 px-6 text-left">Marital Status</th>
                  <th class="py-3 px-6 text-left">Emergency Contact</th>
                  <th class="py-3 px-6 text-left">Emergency Phone</th>
                  <th class="py-3 px-6 text-left">ABA Bank Account</th>
                  <th class="py-3 px-6 text-left">ID Card</th>
                  <th class="py-3 px-6 text-left">NSSF Card</th>
                  <th class="py-3 px-6 text-left">Date of Birth</th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-if="!users || users.length === 0" class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <td colspan="19" class="py-4 text-center">No users found.</td>
                </tr>
                <tr v-for="user in users" :key="user.id" class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <td class="py-3 px-6 text-left">{{ user.full_name }}</td>
                  <td class="py-3 px-6 text-left">{{ user.phone || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.full_name_kh || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">
                    <span
                      class="py-1 px-3 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-blue-200 text-blue-600': user.gender === 'male',
                        'bg-pink-200 text-pink-600': user.gender === 'female',
                        'bg-gray-200 text-gray-600': user.gender === 'other' || !user.gender,
                      }"
                    >
                      {{ user.gender || 'N/A' }}
                    </span>
                  </td>
                  <td class="py-3 px-6 text-left">{{ user.email }}</td>
                  <td class="py-3 px-6 text-left">{{ user.position || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.skills || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.department || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.profile || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.address_line || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.city || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.country || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.marital_status || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.emergency_contact_name || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.emergency_contact_phone || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.aba_bank_account || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.id_card || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.nssf_card || 'N/A' }}</td>
                  <td class="py-3 px-6 text-left">{{ user.date_of_birth || 'N/A' }}</td>
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

const users = ref(null)

// Fetch all users from MySQL via API on component mount
onMounted(async () => {
  try {
    const response = await api.get('http://127.0.0.1:8000/api/users/')
    users.value = response.data
  } catch (error) {
    alert('An error occurred while fetching user profiles. Please try again.')
    console.error(error)
  }
})
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>