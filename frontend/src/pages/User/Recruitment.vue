<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300 w-full h-full">
    <div class="w-full p-0 mx-auto flex-grow overflow-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg h-full">
        <div class="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mr-3 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
            </svg>
            Recruitment Management
          </h2>
        </div>

        <!-- Loading & Error Messages -->
        <div v-if="loading" class="text-center p-4">
          <p class="text-blue-500 font-semibold">Loading data...</p>
        </div>
        <div v-if="error" class="text-center p-4 text-red-500 font-semibold">
          <p>Error: {{ error }}</p>
          <p>Please ensure the API is running at http://127.0.0.1:8000</p>
        </div>
        
        <!-- Form Section -->
        <div class="p-6 rounded-lg bg-gray-50 shadow-inner w-full">
          <form @submit.prevent="handleSubmit" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <label for="name" class="block text-gray-700 font-medium mb-2">Full Name</label>
              <input type="text" id="name" v-model="formData.name" placeholder="Name"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required />
            </div>
            <div>
              <label for="position" class="block text-gray-700 font-medium mb-2">Position</label>
              <input type="text" id="position" v-model="formData.position" placeholder="Position"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required />
            </div>
            <div>
              <label for="startDate" class="block text-gray-700 font-medium mb-2">Start Date</label>
              <input type="date" id="startDate" v-model="formData.startDate"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required />
            </div>
            <div>
              <label for="project" class="block text-gray-700 font-medium mb-2">Project</label>
              <input type="text" id="project" v-model="formData.project" placeholder="Project Name"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required />
            </div>
            <div>
              <label for="hiringManager" class="block text-gray-700 font-medium mb-2">Hiring Manager</label>
              <input type="text" id="hiringManager" v-model="formData.hiringManager" placeholder="Manager's Name"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required />
            </div>
            <div>
              <label for="requestDate" class="block text-gray-700 font-medium mb-2">Date of Request</label>
              <input type="date" id="requestDate" v-model="formData.requestDate"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200 bg-white" required />
            </div>
            
            <div class="col-span-full mt-4 flex justify-end space-x-4">
              <button type="submit"
                class="px-6 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 transition duration-300 shadow-md hover:shadow-lg w-full md:w-auto">
                {{ isEditing ? 'Update Request' : 'Submit Request' }}
              </button>
              <button v-if="isEditing" @click="cancelEdit" type="button"
                class="px-6 py-2 bg-gray-400 text-white font-bold rounded-md hover:bg-gray-500 transition duration-300 shadow-md w-full md:w-auto">
                Cancel
              </button>
            </div>
          </form>
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
                  <th class="py-3 px-6 text-center font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody class="text-gray-600 font-light">
                <tr v-if="applications.length === 0">
                  <td colspan="8" class="py-4 text-center text-gray-600">No applications submitted yet.</td>
                </tr>
                <tr v-for="app in applications" :key="app.id"
                  class="border-b border-gray-200 hover:bg-gray-100 transition-colors duration-200">
                  <td class="py-3 px-6">{{ app.name }}</td>
                  <td class="py-3 px-6">{{ app.position }}</td>
                  <td class="py-3 px-6">{{ app.project }}</td>
                  <td class="py-3 px-6">{{ app.hiring_manager }}</td>
                  <td class="py-3 px-6">{{ formatDate(app.request_date) }}</td>
                  <td class="py-3 px-6">{{ formatDate(app.start_date) }}</td>
                  <td class="py-3 px-6 text-center">
                    <span class="py-1 px-3 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-green-200 text-green-600': app.status === 'Approved',
                        'bg-red-200 text-red-600': app.status === 'Rejected',
                        'bg-yellow-200 text-yellow-600': app.status === 'Pending'
                      }">
                      {{ app.status }}
                    </span>
                  </td>
                  <td class="py-3 px-6 text-center flex justify-center space-x-2">
                    <button @click="editApplication(app)" class="text-blue-500 hover:text-blue-700">
                      <i class="fas fa-pen-to-square"></i>
                    </button>
                    <button @click="confirmDelete(app.id)" class="text-red-500 hover:text-red-700">
                      <i class="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 py-6 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
        <div class="inline-block align-bottom bg-white rounded-lg shadow-xl sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="px-4 py-5">
            <h3 class="text-lg font-medium text-gray-900">Delete Request</h3>
            <p class="mt-2 text-sm text-gray-500">
              Are you sure you want to delete this recruitment request? This action cannot be undone.
            </p>
          </div>
          <div class="bg-gray-50 px-4 py-3 flex justify-end space-x-2">
            <button @click="deleteConfirmed" type="button"
              class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700">
              Delete
            </button>
            <button @click="showModal = false" type="button"
              class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";

const API_BASE_URL = "http://127.0.0.1:8000/recruitments/";

const applications = ref([]);
const isEditing = ref(false);
const editId = ref(null);
const loading = ref(false);
const error = ref(null);
const showModal = ref(false);
const deleteId = ref(null);

const formData = reactive({
  id: null,
  name: "",
  position: "",
  project: "",
  hiringManager: "",
  requestDate: "",
  startDate: "",
  status: "Pending",
});

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toISOString().split("T")[0]; // ✅ force YYYY-MM-DD
};

const fetchApplications = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch(API_BASE_URL);
    if (!response.ok) throw new Error("Failed to fetch");
    applications.value = await response.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    name: "",
    position: "",
    project: "",
    hiringManager: "",
    requestDate: "",
    startDate: "",
    status: "Pending",
  });
  isEditing.value = false;
  editId.value = null;
};

const createApplication = async () => {
  const payload = {
    name: formData.name,
    position: formData.position,
    project: formData.project,
    hiring_manager: formData.hiringManager,
    request_date: formData.requestDate,
    start_date: formData.startDate,
    status: formData.status,
  };
  try {
    const res = await fetch(API_BASE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to create");
    await fetchApplications();
    resetForm();
  } catch (err) {
    error.value = err.message;
  }
};

const updateApplication = async () => {
  const payload = {
    name: formData.name,
    position: formData.position,
    project: formData.project,
    hiring_manager: formData.hiringManager,
    request_date: formData.requestDate,
    start_date: formData.startDate,
    status: formData.status,
  };
  try {
    const res = await fetch(`${API_BASE_URL}${editId.value}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to update");
    await fetchApplications();
    resetForm();
  } catch (err) {
    error.value = err.message;
  }
};

const confirmDelete = (id) => {
  deleteId.value = id;
  showModal.value = true;
};

const deleteConfirmed = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}${deleteId.value}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete");
    await fetchApplications();
  } catch (err) {
    error.value = err.message;
  } finally {
    showModal.value = false;
    deleteId.value = null;
  }
};

const editApplication = (app) => {
  formData.id = app.id;
  formData.name = app.name;
  formData.position = app.position;
  formData.project = app.project;
  formData.hiringManager = app.hiring_manager;
  formData.requestDate = formatDate(app.request_date);
  formData.startDate = formatDate(app.start_date);
  formData.status = app.status;
  isEditing.value = true;
  editId.value = app.id;
};

const handleSubmit = () => {
  isEditing.value ? updateApplication() : createApplication();
};

const cancelEdit = () => {
  resetForm();
};

onMounted(fetchApplications);
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>