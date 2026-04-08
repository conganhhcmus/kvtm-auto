export type DeviceStatus = 'online' | 'offline' | 'busy'

export interface Device {
  id: string
  name: string
  status: DeviceStatus
  current_script_id: string | null
  last_seen: string | null
}
