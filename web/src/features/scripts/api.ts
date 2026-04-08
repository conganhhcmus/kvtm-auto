import apiClient from '@/shared/lib/api-client'
import type { Script } from './types'

export const scriptApi = {
  getScripts: () => apiClient.get<Script[]>('/scripts').then((r) => r.data),
  getScript: (id: string) => apiClient.get<Script>(`/scripts/${id}`).then((r) => r.data),
}
