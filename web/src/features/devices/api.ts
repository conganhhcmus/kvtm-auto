import apiClient from '@/shared/lib/api-client'
import type { Device } from './types'

export const deviceApi = {
  getDevices: () => apiClient.get<Device[]>('/devices').then((r) => r.data),
  getDevice: (id: string) => apiClient.get<Device>(`/devices/${id}`).then((r) => r.data),
}
