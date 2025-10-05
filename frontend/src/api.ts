import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export interface GameOptions {
    open_game?: boolean
    open_chest?: boolean
    sell_items?: boolean
}

export interface Script {
    id: string
    name: string
    created: string
    path: string
}

export interface ScriptListResponse {
    scripts: Script[]
    total: number
}

export interface DeviceDetail {
    id: string
    name: string
    status: string
    last_seen: string
    current_script: string | null
    current_script_name?: string | null
    current_execution_id: string | null
    device_name?: string
    game_options?: GameOptions
}

export interface ExecutionStartResponse {
    execution_id: string
    status: 'started'
    device: DeviceDetail
    script: Script
}

export interface ExecutionStopResponse {
    status: 'stopped'
}

export interface ExecutionStopAllResponse {
    stopped_count: number
    errors: string[]
}

export const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor
api.interceptors.request.use(
    (config) => {
    // Add auth token if available
        const token = localStorage.getItem('auth_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized access
            localStorage.removeItem('auth_token')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

// Device API
export const deviceApi = {
    getDevices: () => api.get<DeviceDetail[]>('/devices'),
    getDevice: (deviceId: string) => api.get<DeviceDetail>(`/devices/${deviceId}`),
    getDeviceLogs: (deviceId: string, limit?: number) =>
        api.get<string[]>(`/devices/${deviceId}/logs`, { params: { limit } }),
}

// Script API
export const scriptApi = {
    getScripts: () => api.get<ScriptListResponse>('/scripts'),
    getScript: (scriptId: string) => api.get<Script>(`/scripts/${scriptId}`),
}

// Execute API
export const executeApi = {
    runScript: (scriptId: string, deviceId: string, gameOptions?: GameOptions) =>
        api.post<ExecutionStartResponse>('/execute/start', {
            device_id: deviceId,
            script_id: scriptId,
            game_options: gameOptions || {}
        }),
    stopScript: (executionId: string) =>
        api.post<ExecutionStopResponse>('/execute/stop', { execution_id: executionId }),
    stopAllDevices: () =>
        api.post<ExecutionStopAllResponse>('/execute/stop-all'),
}

