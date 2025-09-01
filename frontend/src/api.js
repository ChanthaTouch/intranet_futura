
import axios from 'axios'
import router from './router'
import { useAuth } from './store'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'https://intranet-dev-01.futura-dnc.com/',
  withCredentials: false,
})

api.interceptors.request.use((config) => {
  try{
    const auth = useAuth()
    if (auth?.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${auth.token}`
    }
  }catch{}
  return config
})

api.interceptors.response.use(
  (resp) => resp,
  (err) => {
    const status = err?.response?.status
    if (status === 401) {
      try{
        const auth = useAuth()
        auth?.logout()
      }catch{}
      // hard redirect to ensure clean state
      if (router.currentRoute.value.path !== '/login') router.push('/login').catch(()=>{})
    }
    return Promise.reject(err)
  }
)

export default api
