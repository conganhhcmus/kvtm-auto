import { useMutation, useQueryClient } from '@tanstack/react-query'
import { executionApi } from './api'
import type { GameOptions } from './types'

export function useStartExecution() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ deviceId, scriptId, options }: { deviceId: string; scriptId: string; options: GameOptions }) =>
      executionApi.start(deviceId, scriptId, options),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['devices'] }),
  })
}

export function useStopExecution() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (deviceId: string) => executionApi.stop(deviceId),
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ['devices'] })
      qc.refetchQueries({ queryKey: ['devices'] })
    },
  })
}

export function useStopAll() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: executionApi.stopAll,
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ['devices'] })
      qc.refetchQueries({ queryKey: ['devices'] })
    },
  })
}
