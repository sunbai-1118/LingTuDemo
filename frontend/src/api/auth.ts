import http, { type ApiEnvelope } from './http'

export interface UserInfo {
  id: number
  username: string
  role: 'USER' | 'ADMIN'
  status: string
  created_at: string
}

export interface LoginData {
  token: string
  user: UserInfo
}

export interface RegisterData {
  id: number
  username: string
  role: string
  status: string
  created_at: string
}

export async function login(username: string, password: string): Promise<ApiEnvelope<LoginData>> {
  const resp = await http.post<ApiEnvelope<LoginData>>('/auth/login', { username, password })
  return resp.data
}

export async function register(
  username: string,
  password: string,
  confirmPassword: string,
): Promise<ApiEnvelope<RegisterData>> {
  const resp = await http.post<ApiEnvelope<RegisterData>>('/auth/register', {
    username,
    password,
    confirm_password: confirmPassword,
  })
  return resp.data
}

export async function me(): Promise<ApiEnvelope<UserInfo>> {
  const resp = await http.get<ApiEnvelope<UserInfo>>('/auth/me')
  return resp.data
}
