<template>
  <div class="bg-white min-h-screen font-sans text-gray-900 transition-colors duration-300">
    <div class="w-full p-4 mx-auto">
      <div class="bg-white p-6 sm:p-8 rounded-lg shadow-lg">
        <h2 class="text-xl font-bold text-gray-800 mb-4">Dashboard</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-xl font-bold text-gray-800 mb-4">Quick Links</div>
            <router-link class="block text-sm text-gray-600 hover:text-gray-900 underline transition-colors duration-200" to="/e-project">E-Project</router-link>
            <router-link class="block text-sm text-gray-600 hover:text-gray-900 underline transition-colors duration-200" to="/helpdesk">Helpdesk</router-link>
            <router-link class="block text-sm text-gray-600 hover:text-gray-900 underline transition-colors duration-200" to="/library">Library</router-link>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-xl font-bold text-gray-800 mb-4">Finance</div>
            <router-link class="text-sm text-gray-600 hover:text-gray-900 underline transition-colors duration-200" to="/finance">Open finance view</router-link>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-xl font-bold text-gray-800 mb-4">Analytics</div>
            <router-link class="text-sm text-gray-600 hover:text-gray-900 underline transition-colors duration-200" to="/analytics">Analysis of Data</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
</style>