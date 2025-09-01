
import { defineStore } from 'pinia'
import api from './api'

export const useAuth = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || '',
    loading: false,
    error: ''
  }),
  actions: {
    async login(username, password){
      this.loading = true; this.error=''
      try{
        const { data } = await api.post('/api/auth/login', { username, password })
        this.token = data.access_token
        localStorage.setItem('token', this.token)
        await this.fetchMe()
      }catch(e){
        this.error = 'Login failed'
        throw e
      }finally{ this.loading=false }
    },
    async fetchMe(){
      const { data } = await api.get('/api/users/me')
      this.user = data
    },
    logout(){
      this.user = null; this.token=''
      localStorage.removeItem('token')
    }
  }
})
