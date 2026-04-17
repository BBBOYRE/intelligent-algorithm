import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// 请求拦截器：注入 token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理 401
http.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      // 只在非登录页时跳转，避免循环
      if (!window.location.hash.includes('/login')) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.hash = '#/login'
      }
    }
    return Promise.reject(err)
  }
)

export default http
