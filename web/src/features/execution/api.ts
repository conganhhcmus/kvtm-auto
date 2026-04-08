import apiClient from '@/shared/lib/api-client'
import type { GameOptions } from './types'

export const executionApi = {
  start: (deviceId: string, scriptId: string, options: GameOptions) =>
    apiClient.post('/execute/start', { device_id: deviceId, script_id: scriptId, options }),
  stop: (deviceId: string) =>
    apiClient.post('/execute/stop', { device_id: deviceId }),
  stopAll: () =>
    apiClient.post('/execute/stop-all'),
}
