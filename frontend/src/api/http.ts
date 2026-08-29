import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

export interface ApiEnvelope<T = unknown> {
  code: number
  message: string
  data: T
}

const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const auth = useAuthStore()
    // Token 过期 / 无效：清除本地状态并跳转登录页
    if (status === 401 && auth.isLoggedIn) {
      auth.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  },
)

/** 从统一响应中提取用户可读的错误信息 */
export function extractErrorMessage(error: unknown): string {
  const envelope = (error as { response?: { data?: ApiEnvelope } }).response?.data
  if (envelope?.message) return envelope.message
  if ((error as { code?: string }).code === 'ECONNABORTED') return '请求超时，请稍后重试'
  return '网络异常，请稍后重试'
}

export default http
