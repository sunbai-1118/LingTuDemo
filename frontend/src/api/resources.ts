import http, { type ApiEnvelope } from './http'

export interface ResourceInfo {
  resource: 'A' | 'B'
  message: string
}

export async function fetchResourceA(): Promise<ApiEnvelope<ResourceInfo>> {
  const resp = await http.get<ApiEnvelope<ResourceInfo>>('/resources/a')
  return resp.data
}

export async function fetchResourceB(): Promise<ApiEnvelope<ResourceInfo>> {
  const resp = await http.get<ApiEnvelope<ResourceInfo>>('/resources/b')
  return resp.data
}
