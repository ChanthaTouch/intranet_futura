<template>
 
  <div class="min-h-screen w-full bg-gray-200 flex items-center justify-center p-4 sm:p-6 md:p-8">
    <div class="bg-white rounded-lg shadow-lg p-6 sm:p-8 md:p-10 w-full max-w-lg sm:max-w-xl md:max-w-2xl font-sans">
      <div class="logo-futura mb-6 flex justify-center">
        <img :src="logoSrc" alt="Futura Logo" class="max-w-[150px] sm:max-w-[200px] md:max-w-[250px] h-auto">
      </div>
      <h2 class="text-xl sm:text-2xl md:text-3xl font-bold text-gray-700 mb-6 text-center">Welcome to Futura</h2>
      <div class="space-y-6">
        <div>
          <label for="username" class="block text-sm sm:text-base font-medium text-gray-500 mb-1">Email or Username</label>
          <input 
            v-model="username" 
            id="username"
            placeholder="Enter your email or username" 
            class="w-full px-4 py-3 border border-gray-400 rounded-md focus:ring-2 focus:ring-gray-500 focus:border-gray-500 outline-none transition-colors text-sm sm:text-base bg-white text-black"
            autocomplete="username"
          />
        </div>
        <div>
          <label for="password" class="block text-sm sm:text-base font-medium text-gray-500 mb-1">Password</label>
          <div class="relative">
            <input 
              v-model="password" 
              id="password"
              :type="showPwd ? 'text' : 'password'"
              placeholder="Enter your password"
              class="w-full px-4 py-3 border border-gray-400 rounded-md focus:ring-2 focus:ring-gray-500 focus:border-gray-500 outline-none transition-colors pr-12 sm:pr-14 text-sm sm:text-base bg-white text-black"
              autocomplete="current-password"
            />
            <button 
              type="button" 
              class="absolute right-3 sm:right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
              @click="showPwd = !showPwd" 
              aria-label="Toggle password visibility"
            >
              <svg v-if="showPwd" class="w-5 sm:w-6 h-5 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7 1.275-4.057 5.065-7 9.543-7 4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-1.668 3.825M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18" />
              </svg>
              <svg v-else class="w-5 sm:w-6 h-5 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
          </div>
        </div>
        <button 
          @click="submit"
          class="w-full bg-black text-white py-3 rounded-md hover:bg-gray-800 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors font-medium text-sm sm:text-base"
        >
          Sign In
        </button>
       
        <p v-if="error" class="text-red-500 text-sm sm:text-base text-center">{{ error }}</p>
        <div class="text-center text-sm sm:text-base text-gray-500">
          <a href="/forgot-password" class="hover:text-gray-700 transition-colors">Forgot password?</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../store';

// Import the logo image as a module
import logo from '../assets/logo.jpg';

const router = useRouter();
const auth = useAuth();
const username = ref('');
const password = ref('');
const showPwd = ref(false);
const error = ref('');
const logoSrc = ref(logo || 'https://via.placeholder.com/200x50?text=Futura+Logo');

async function submit() {
  if (!username.value || !password.value) {
    error.value = 'Please fill in all fields';
    return;
  }
  try {
    await auth.login(username.value, password.value);
    router.push('/');
  } catch (e) {
    error.value = 'Invalid credentials';
  }
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>