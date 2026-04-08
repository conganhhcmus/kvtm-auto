import { useQuery } from '@tanstack/react-query'
import { scriptApi } from './api'

export function useScripts() {
  return useQuery({
    queryKey: ['scripts'],
    queryFn: scriptApi.getScripts,
  })
}

export function useScript(id: string) {
  return useQuery({
    queryKey: ['scripts', id],
    queryFn: () => scriptApi.getScript(id),
    enabled: !!id,
  })
}
