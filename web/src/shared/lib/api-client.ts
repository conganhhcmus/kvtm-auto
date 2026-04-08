import axios from 'axios'

const apiClient = axios.create({ baseURL: '/api' })

apiClient.interceptors.response.use(
  (r) => r,
  (e) => Promise.reject(e.response?.data?.detail ?? e.message),
)

export default apiClient
