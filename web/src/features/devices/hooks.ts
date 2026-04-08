import { useQuery } from '@tanstack/react-query'
import { deviceApi } from './api'

export function useDevices() {
  return useQuery({
    queryKey: ['devices'],
    queryFn: deviceApi.getDevices,
    refetchInterval: 5000,
    refetchIntervalInBackground: true,
  })
}

export function useDevice(id: string) {
  return useQuery({
    queryKey: ['devices', id],
    queryFn: () => deviceApi.getDevice(id),
    enabled: !!id,
  })
}
