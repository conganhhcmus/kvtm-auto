import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export interface GameOptions {
    open_game?: boolean
    open_chest?: boolean
    sell_items?: boolean
    max_loops?: number
    loop_delay?: number
}

export interface ScriptResponse {
    id: string
    name: string
    description?: string
    order: number
    recommend: boolean
}

export interface ScriptListResponse {
    scripts: ScriptResponse[]
    total: number
}

export interface ScriptDetailResponse {
    id: string
    name: string
    description?: string
    order: number
    recommend: boolean
    path?: string
    last_modified?: string
}

export interface DeviceDetail {
    id: string
    device_name: string
    device_status: string
    screen_size?: number[]
    last_seen?: string
    current_script?: string
    script_name?: string
    game_options?: GameOptions
    model?: string
    android_version?: string
    api_level?: string
    architecture?: string
    connection_type?: string
    ip_address?: string
    battery_level?: number
    screen_on?: boolean
    cpu_usage?: number
    total_storage?: string
    available_storage?: string
    ram?: string
    current_auto?: string
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
    getDevices: () => api.get('/devices'),
    getDevice: (deviceId: string) => api.get(`/devices/${deviceId}`),
    getDeviceLogs: (deviceId: string, limit?: number) => api.get(`/devices/${deviceId}/logs`, { params: { limit } }),
    connectDevice: (deviceId: string) => api.post(`/devices/${deviceId}/connect`),
    disconnectDevice: (deviceId: string) => api.post(`/devices/${deviceId}/disconnect`),
    refreshDevices: () => api.post('/devices/refresh'),
}

// Script API
export const scriptApi = {
    getScripts: () => api.get('/scripts'),
    getScript: (scriptId: string) => api.get(`/scripts/${scriptId}`),
    runScript: (scriptId: string, deviceId: string, gameOptions?: GameOptions) =>
        api.post('/execute/start', {
            device_id: deviceId,
            script_id: scriptId,
            game_options: gameOptions || {}
        }),
    stopScript: (executionId: string) => api.post('/execute/stop', { execution_id: executionId }),
    stopAllDevices: () => api.post('/execute/stop-all'),
}

