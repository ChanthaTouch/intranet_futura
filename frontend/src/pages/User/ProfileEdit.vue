<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300">
    <div class="w-full p-4 mx-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">
            <i class="fas fa-id-card mr-2 text-blue-500"></i>
            Edit Profile
          </h2>
        </div>

        <div class="p-6 rounded-lg bg-gray-50 shadow-inner">
          <form @submit.prevent="save" class="space-y-6">
            <!-- Personal Information Section -->
            <div>
              <h3 class="text-lg font-semibold text-gray-800 mb-4">Personal Information</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label for="full_name_kh" class="block text-gray-700 mb-1">Full Name (Khmer)</label>
                  <input
                    type="text"
                    id="full_name_kh"
                    v-model="formData.full_name_kh"
                    placeholder="Full Name (Khmer)"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="full_name" class="block text-gray-700 mb-1">Full Name (English)</label>
                  <input
                    type="text"
                    id="full_name"
                    v-model="formData.full_name"
                    placeholder="Full Name (English)"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    required
                  />
                </div>
                <div>
                  <label for="gender" class="block text-gray-700 mb-1">Gender</label>
                  <select
                    id="gender"
                    v-model="formData.gender"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  >
                    <option value="" disabled>Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label for="phone" class="block text-gray-700 mb-1">Phone</label>
                  <input
                    type="text"
                    id="phone"
                    v-model="formData.phone"
                    placeholder="Phone Number"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    required
                  />
                </div>
                <div>
                  <label for="email" class="block text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    id="email"
                    v-model="formData.email"
                    placeholder="Email Address"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="date_of_birth" class="block text-gray-700 mb-1">Date of Birth</label>
                  <input
                    type="date"
                    id="date_of_birth"
                    v-model="formData.date_of_birth"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
              </div>
            </div>

            <!-- Professional Information Section -->
            <div>
              <h3 class="text-lg font-semibold text-gray-800 mb-4">Professional Information</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label for="position" class="block text-gray-700 mb-1">Position</label>
                  <input
                    type="text"
                    id="position"
                    v-model="formData.position"
                    placeholder="Job Position"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="skills" class="block text-gray-700 mb-1">Skills (comma separated)</label>
                  <input
                    type="text"
                    id="skills"
                    v-model="formData.skills"
                    placeholder="e.g., JavaScript, Python, Project Management"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="department" class="block text-gray-700 mb-1">Department</label>
                  <input
                    type="text"
                    id="department"
                    v-model="formData.department"
                    placeholder="Department"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
              </div>
            </div>

            <!-- Address Information Section -->
            <div>
              <h3 class="text-lg font-semibold text-gray-800 mb-4">Address Information</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label for="address_line" class="block text-gray-700 mb-1">Address Line</label>
                  <input
                    type="text"
                    id="address_line"
                    v-model="formData.address_line"
                    placeholder="Address Line"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="city" class="block text-gray-700 mb-1">City</label>
                  <input
                    type="text"
                    id="city"
                    v-model="formData.city"
                    placeholder="City"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="country" class="block text-gray-700 mb-1">Country</label>
                  <input
                    type="text"
                    id="country"
                    v-model="formData.country"
                    placeholder="Country"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
              </div>
            </div>

            <!-- Additional Information Section -->
            <div>
              <h3 class="text-lg font-semibold text-gray-800 mb-4">Additional Information</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label for="marital_status" class="block text-gray-700 mb-1">Marital Status</label>
                  <select
                    id="marital_status"
                    v-model="formData.marital_status"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  >
                    <option value="" disabled>Select Marital Status</option>
                    <option value="single">Single</option>
                    <option value="married">Married</option>
                    <option value="divorced">Divorced</option>
                    <option value="widowed">Widowed</option>
                  </select>
                </div>
                <div>
                  <label for="emergency_contact_name" class="block text-gray-700 mb-1">Emergency Contact Name</label>
                  <input
                    type="text"
                    id="emergency_contact_name"
                    v-model="formData.emergency_contact_name"
                    placeholder="Emergency Contact Name"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="emergency_contact_phone" class="block text-gray-700 mb-1">Emergency Contact Phone</label>
                  <input
                    type="text"
                    id="emergency_contact_phone"
                    v-model="formData.emergency_contact_phone"
                    placeholder="Emergency Contact Phone"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="aba_bank_account" class="block text-gray-700 mb-1">ABA Bank Account</label>
                  <input
                    type="text"
                    id="aba_bank_account"
                    v-model="formData.aba_bank_account"
                    placeholder="ABA Bank Account Number"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="id_card" class="block text-gray-700 mb-1">ID Card Number</label>
                  <input
                    type="text"
                    id="id_card"
                    v-model="formData.id_card"
                    placeholder="ID Card Number"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
                <div>
                  <label for="nssf_card" class="block text-gray-700 mb-1">NSSF Card Number</label>
                  <input
                    type="text"
                    id="nssf_card"
                    v-model="formData.nssf_card"
                    placeholder="NSSF Card Number"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end gap-4 mt-6">
              <button
                type="button"
                @click="confirmReset"
                class="px-6 py-2 bg-gray-600 text-white font-bold rounded-md hover:bg-gray-700 transition duration-300 shadow-md hover:shadow-lg"
              >
                Reset
              </button>
              <button
                type="submit"
                :disabled="isSaving || isCreating || isDeleting"
                class="px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg disabled:bg-blue-400 disabled:cursor-not-allowed"
              >
                <i class="fas fa-save mr-2"></i>{{ isSaving ? 'Saving...' : 'Save Changes' }}
              </button>
              <button
                type="button"
                @click="createProfile"
                :disabled="isSaving || isCreating || isDeleting || !isCreateProfileSupported"
                :title="isCreateProfileSupported ? '' : 'Profile creation is not supported on this server. Please contact support.'"
                class="px-6 py-2 bg-green-600 text-white font-bold rounded-md hover:bg-green-700 transition duration-300 shadow-md hover:shadow-lg disabled:bg-green-400 disabled:cursor-not-allowed"
              >
                <i class="fas fa-plus mr-2"></i>{{ isCreating ? 'Creating...' : 'Create Profile' }}
              </button>
              <button
                v-if="userId"
                type="button"
                @click="confirmDelete"
                :disabled="isSaving || isCreating || isDeleting"
                class="px-6 py-2 bg-red-600 text-white font-bold rounded-md hover:bg-red-700 transition duration-300 shadow-md hover:shadow-lg disabled:bg-red-400 disabled:cursor-not-allowed"
              >
                <i class="fas fa-trash mr-2"></i>{{ isDeleting ? 'Deleting...' : 'Delete Profile' }}
              </button>
            </div>

            <div v-if="successMessage" class="mt-4 p-4 bg-green-100 text-green-700 rounded-md">
              {{ successMessage }}
            </div>
            <div v-if="errorMessage" class="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
              {{ errorMessage }}
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import api from '../../api'

const isCreateProfileSupported = ref(false) // Will be set based on OPTIONS check
const formData = reactive({
  full_name_kh: '',
  full_name: '',
  gender: '',
  phone: '',
  email: '',
  position: '',
  skills: '',
  department: '',
  address_line: '',
  city: '',
  country: '',
  marital_status: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
  aba_bank_account: '',
  id_card: '',
  nssf_card: '',
  date_of_birth: ''
})
const isSaving = ref(false)
const isCreating = ref(false)
const isDeleting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const userId = ref(null) // Store userId for deletion

async function load() {
  try {
    const me = await api.get('/api/users/me')
    formData.full_name = me.data.full_name || ''
    formData.phone = me.data.phone || ''
    userId.value = me.data.id || null
    const { data } = await api.get('/api/users/me/profile')
    Object.assign(formData, {
      full_name_kh: data.full_name_kh || '',
      gender: data.gender || '',
      email: data.email || '',
      position: data.position || '',
      skills: data.skills || '',
      department: data.department || '',
      address_line: data.address_line || '',
      city: data.city || '',
      country: data.country || '',
      marital_status: data.marital_status || '',
      emergency_contact_name: data.emergency_contact_name || '',
      emergency_contact_phone: data.emergency_contact_phone || '',
      aba_bank_account: data.aba_bank_account || '',
      id_card: data.id_card || '',
      nssf_card: data.nssf_card || '',
      date_of_birth: data.date_of_birth || ''
    })
    successMessage.value = 'Profile loaded successfully!'
  } catch (e) {
    errorMessage.value = 'Failed to load profile data. Please try again.'
    console.error('Load error:', e.response?.data || e)
  }
}

async function save() {
  if (!formData.full_name || !formData.phone) {
    errorMessage.value = 'Please fill out all required fields (Full Name (English) and Phone).'
    return
  }

  isSaving.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    await api.put('/api/users/me/profile', formData)
    successMessage.value = 'Profile updated successfully!'
  } catch (e) {
    const status = e.response?.status
    errorMessage.value =
      status === 405
        ? 'Profile update is not allowed on this server. Please contact support.'
        : e.response?.data?.message || 'An error occurred while saving the profile. Please try again.'
    console.error('Save error:', e.response?.data || e)
  } finally {
    isSaving.value = false
  }
}

async function createProfile() {
  if (!formData.full_name || !formData.phone) {
    errorMessage.value = 'Please fill out all required fields (Full Name (English) and Phone).'
    return
  }

  isCreating.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    const response = await api.post('http://127.0.0.1:8000/api/users/', {
      ...formData,
      is_staff: true
    })
    userId.value = response.data.id || null
    successMessage.value = 'Staff profile created successfully!'
    resetForm()
  } catch (e) {
    const status = e.response?.status
    errorMessage.value =
      status === 405
        ? 'Profile creation is not supported on this server. Please contact support or check backend configuration.'
        : e.response?.data?.message || 'An error occurred while creating the staff profile. Please try again.'
    console.error('Create error:', e.response?.data || e)
  } finally {
    isCreating.value = false
  }
}

async function deleteProfile() {
  isDeleting.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    await api.delete(`/api/users/${userId.value}`)
    successMessage.value = 'Profile deleted successfully!'
    resetForm()
    userId.value = null
  } catch (e) {
    const status = e.response?.status
    errorMessage.value =
      status === 405
        ? 'Profile deletion is not allowed on this server. Please contact support.'
        : e.response?.data?.message || 'An error occurred while deleting the profile. Please try again.'
    console.error('Delete error:', e.response?.data || e)
  } finally {
    isDeleting.value = false
  }
}

function confirmReset() {
  if (confirm('Are you sure you want to reset all fields? This cannot be undone.')) {
    resetForm()
    successMessage.value = 'Form reset successfully!'
  }
}

function confirmDelete() {
  if (confirm('Are you sure you want to delete your profile? This action cannot be undone.')) {
    deleteProfile()
  }
}

function resetForm() {
  Object.assign(formData, {
    full_name_kh: '',
    full_name: '',
    gender: '',
    phone: '',
    email: '',
    position: '',
    skills: '',
    department: '',
    address_line: '',
    city: '',
    country: '',
    marital_status: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    aba_bank_account: '',
    id_card: '',
    nssf_card: '',
    date_of_birth: ''
  })
  successMessage.value = ''
  errorMessage.value = ''
}

async function checkCreateSupport() {
  try {
    const response = await api.options('http://127.0.0.1:8000/api/users/')
    const allowedMethods = response.headers['allow']?.split(',').map(method => method.trim()) || []
    isCreateProfileSupported.value = allowedMethods.includes('POST')
  } catch (e) {
    console.warn('Skipping OPTIONS check. Assuming POST is supported.')
    isCreateProfileSupported.value = true   // fallback to true
  }
}

onMounted(async () => {
  await load()
  await checkCreateSupport()
})

</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>