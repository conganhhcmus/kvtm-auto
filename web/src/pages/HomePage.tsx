import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Play, Square, ChevronDown, ChevronUp, MonitorOff, ScrollText, Info, Monitor } from 'lucide-react'
import { useDevices } from '@/features/devices/hooks'
import { useScripts } from '@/features/scripts/hooks'
import { useStopAll, useStopExecution } from '@/features/execution/hooks'
import { executionApi } from '@/features/execution/api'
import type { GameOptions } from '@/features/execution/types'
import type { Device } from '@/features/devices/types'
import type { Script } from '@/features/scripts/types'
import DeviceDetailModal from '@/features/devices/components/DeviceDetailModal'
import DeviceLogModal from '@/features/devices/components/DeviceLogModal'
import LiveScreenModal from '@/features/stream/components/LiveScreenModal'
import MultiSelect from '@/shared/components/MultiSelect'
import SearchableSelect from '@/shared/components/SearchableSelect'
import { useLocalStorage } from '@/shared/hooks/useLocalStorage'

export default function HomePage() {
  const [selectedDevices, setSelectedDevices] = useState<string[]>([])
  const [selectedScript, setSelectedScript] = useState('')
  const [openGame, setOpenGame] = useState(true)
  const [openChests, setOpenChests] = useState(true)
  const [sellItems, setSellItems] = useState(true)

  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedDeviceDetail, setSelectedDeviceDetail] = useState('')
  const [showLogModal, setShowLogModal] = useState(false)
  const [selectedDeviceForLogs, setSelectedDeviceForLogs] = useState('')
  const [showLiveScreenModal, setShowLiveScreenModal] = useState(false)
  const [selectedDeviceForStream, setSelectedDeviceForStream] = useState({ id: '-1', name: '' })
  const [isControlPanelExpanded, setIsControlPanelExpanded] = useLocalStorage('controlPanelExpanded', true)
  const [stoppingDevices, setStoppingDevices] = useState<Set<string>>(new Set())

  const qc = useQueryClient()
  const { data: devices = [] } = useDevices()
  const { data: scripts = [] } = useScripts()
  const stopAllMutation = useStopAll()
  const stopDeviceMutation = useStopExecution()

  const runMutation = useMutation({
    mutationFn: async () => {
      if (selectedDevices.length === 0) throw new Error('No devices selected')
      if (!selectedScript) throw new Error('No script selected')
      const options: GameOptions = { open_game: openGame, open_chests: openChests, sell_items: sellItems }
      for (const deviceId of selectedDevices) {
        await executionApi.start(deviceId, selectedScript, options).catch(() => {})
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ['devices'] })
      qc.refetchQueries({ queryKey: ['devices'] })
    },
  })

  const deviceOptions = devices.map((device: Device) => {
    const isRunning = device.status === 'busy'
    const isOffline = device.status === 'offline'
    let statusSuffix = ''
    if (isRunning) statusSuffix = ' (Running - Cannot select)'
    else if (isOffline) statusSuffix = ' (Offline - Cannot select)'
    return {
      value: device.id,
      label: device.name,
      description: `Status: ${device.status}${statusSuffix}`,
      disabled: isRunning || isOffline,
    }
  })

  const scriptOptions = scripts.map((script: Script) => ({
    value: script.id,
    label: script.name,
  }))

  const getScriptDisplayName = (scriptId: string | null | undefined): string => {
    if (!scriptId) return 'No script'
    const script = scripts.find((s: Script) => s.id === scriptId)
    return script ? script.name : scriptId
  }

  const handleStopDevice = (deviceId: string) => {
    setStoppingDevices((prev) => new Set([...prev, deviceId]))
    stopDeviceMutation.mutate(deviceId, {
      onSettled: () => {
        setStoppingDevices((prev) => {
          const next = new Set(prev)
          next.delete(deviceId)
          return next
        })
      },
    })
  }

  const runningDevices = devices.filter((d: Device) => d.status === 'busy')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700">
      <div className="container mx-auto px-4 py-4 sm:py-8 max-w-7xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white mb-3 tracking-tight">
            <span className="bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent drop-shadow-lg">
              KVTM Auto Tools
            </span>
          </h1>
        </div>

        {/* Control Panel */}
        <div className="relative z-10 bg-white rounded-xl shadow-2xl p-6 sm:p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900">Control Panel</h2>
            <button
              onClick={() => setIsControlPanelExpanded(!isControlPanelExpanded)}
              className="lg:hidden inline-flex items-center px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              {isControlPanelExpanded ? (
                <><span className="text-sm font-medium text-gray-700 mr-2">Hide</span><ChevronUp className="w-4 h-4 text-gray-600" /></>
              ) : (
                <><span className="text-sm font-medium text-gray-700 mr-2">Show</span><ChevronDown className="w-4 h-4 text-gray-600" /></>
              )}
            </button>
          </div>

          <div className={isControlPanelExpanded ? 'block' : 'hidden lg:block'}>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
              <MultiSelect options={deviceOptions} values={selectedDevices} onChange={setSelectedDevices} placeholder="Select devices..." label="Devices" />
              <SearchableSelect options={scriptOptions} value={selectedScript} onChange={setSelectedScript} placeholder="Select script..." label="Script" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-end">
              <div className="lg:col-span-3">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Game Options</h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    { label: 'Open Game', value: openGame, onChange: setOpenGame },
                    { label: 'Open Chests', value: openChests, onChange: setOpenChests },
                    { label: 'Sell Items', value: sellItems, onChange: setSellItems },
                  ].map(({ label, value, onChange }) => (
                    <label key={label} className="flex items-center px-3 h-12 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200">
                      <input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500" />
                      <span className="ml-3 text-sm text-gray-700 font-medium">{label}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="lg:col-span-1 flex justify-center lg:justify-end">
                <button
                  onClick={() => runMutation.mutate()}
                  disabled={selectedDevices.length === 0 || !selectedScript || runMutation.isPending}
                  className="inline-flex items-center justify-center px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg transition-all duration-200 transform hover:scale-105 min-w-[140px] h-12"
                >
                  <Play className="w-5 h-5 mr-2" />
                  Run Now!
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Running Devices */}
        <div className="relative z-0 bg-white rounded-xl shadow-2xl p-6 sm:p-8">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-3">
            <div>
              <h2 className="text-lg sm:text-xl font-bold text-gray-900">Running Devices</h2>
              <p className="text-sm text-gray-500 mt-1">
                {runningDevices.length} device{runningDevices.length !== 1 ? 's' : ''} currently running
              </p>
            </div>
            <button
              onClick={() => stopAllMutation.mutate()}
              disabled={runningDevices.length === 0 || stopAllMutation.isPending}
              className="inline-flex items-center px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-md transition-colors text-sm min-w-[90px]"
            >
              {stopAllMutation.isPending ? (
                <><div className="w-4 h-4 mr-2 animate-spin border-2 border-white border-t-transparent rounded-full" />Stopping...</>
              ) : (
                <><Square className="w-4 h-4 mr-2" />Stop All</>
              )}
            </button>
          </div>

          {runningDevices.length > 0 ? (
            <div className="space-y-4">
              {runningDevices.map((device: Device) => (
                <div key={device.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-lg">{device.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Script: <span className="font-medium">{getScriptDisplayName(device.current_script_id)}</span>
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Last seen: {device.last_seen ? new Date(device.last_seen).toLocaleString() : '—'}
                      </p>
                      <div className="flex items-center mt-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2" />
                        <span className="text-sm text-green-700 font-medium">Running</span>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 sm:grid sm:grid-cols-3 sm:gap-2 lg:flex lg:flex-row lg:space-x-2">
                      <button
                        onClick={() => handleStopDevice(device.id)}
                        disabled={stoppingDevices.has(device.id)}
                        className="inline-flex items-center justify-center px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors min-w-[80px]"
                      >
                        {stoppingDevices.has(device.id) ? (
                          <><div className="w-4 h-4 mr-1 animate-spin border-2 border-white border-t-transparent rounded-full" />Stop...</>
                        ) : (
                          <><Square className="w-4 h-4 mr-1" />Stop</>
                        )}
                      </button>
                      <button
                        onClick={() => { setSelectedDeviceForStream({ id: device.id, name: device.name }); setShowLiveScreenModal(true) }}
                        className="inline-flex items-center justify-center px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm font-medium transition-colors min-w-[80px]"
                      >
                        <Monitor className="w-4 h-4 mr-1" />View
                      </button>
                      <button
                        onClick={() => { setSelectedDeviceForLogs(device.id); setShowLogModal(true) }}
                        className="inline-flex items-center justify-center px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm font-medium transition-colors min-w-[80px]"
                      >
                        <ScrollText className="w-4 h-4 mr-1" />Logs
                      </button>
                      <button
                        onClick={() => { setSelectedDeviceDetail(device.id); setShowDetailModal(true) }}
                        className="inline-flex items-center justify-center px-3 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 text-sm font-medium transition-colors min-w-[80px]"
                      >
                        <Info className="w-4 h-4 mr-1" />Detail
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                <MonitorOff className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Running Devices</h3>
              <p className="text-gray-500">Select devices and a script above to get started</p>
            </div>
          )}
        </div>

        <div className="text-center mt-12">
          <div className="border-t border-white border-opacity-20 pt-6">
            <p className="text-white text-sm opacity-80">© 2025 Design by conganhhcmus | KVTM Auto Tools</p>
          </div>
        </div>
      </div>

      <DeviceDetailModal isOpen={showDetailModal} onClose={() => setShowDetailModal(false)} deviceId={selectedDeviceDetail} />
      <DeviceLogModal isOpen={showLogModal} onClose={() => setShowLogModal(false)} deviceId={selectedDeviceForLogs} />
      <LiveScreenModal isOpen={showLiveScreenModal} onClose={() => setShowLiveScreenModal(false)} deviceId={selectedDeviceForStream.id} deviceName={selectedDeviceForStream.name} />
    </div>
  )
}
