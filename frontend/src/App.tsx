import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { deviceApi, scriptApi, executeApi, GameOptions, Script } from '@/api'
import { Play, Square, ChevronDown, ChevronUp, MonitorOff, ScrollText, Info, Monitor } from 'lucide-react'
import DeviceDetailModal from '@/components/DeviceDetailModal'
import DeviceLogModal from '@/components/DeviceLogModal'
import SearchableSelect from '@/components/SearchableSelect'
import MultiSelect from '@/components/MultiSelect'

interface Device {
    id: string
    name: string
    status: string
    last_seen: string
    current_script: string | null
    current_execution_id: string | null
}

function App() {
    const queryClient = useQueryClient()
    const [selectedDevices, setSelectedDevices] = useState<string[]>([])
    const [selectedScript, setSelectedScript] = useState('')
    const [openGame, setOpenGame] = useState(true)
    const [openChests, setOpenChests] = useState(true)
    const [sellItems, setSellItems] = useState(true)
    
    const [showDetailModal, setShowDetailModal] = useState(false)
    const [selectedDeviceDetail, setSelectedDeviceDetail] = useState('')
    const [showLogModal, setShowLogModal] = useState(false)
    const [selectedDeviceForLogs, setSelectedDeviceForLogs] = useState('')
    const [isControlPanelExpanded, setIsControlPanelExpanded] = useState(true)
    const [stoppingDevices, setStoppingDevices] = useState<Set<string>>(new Set())

    const { data: devices = [] } = useQuery({
        queryKey: ['devices'],
        queryFn: () => deviceApi.getDevices().then(res => res.data),
        //refetchInterval: 5000, // Refetch every 5 seconds for real-time updates
        refetchIntervalInBackground: true, // Keep updating even when tab is not focused
    })

    const { data: scripts = [] } = useQuery({
        queryKey: ['scripts'],
        queryFn: () => scriptApi.getScripts().then(res => res.data.scripts),
    })

    const runMutation = useMutation({
        mutationFn: async () => {
            if (selectedDevices.length === 0) throw new Error('No devices selected')
            if (!selectedScript) throw new Error('No script selected')

            const gameOptions: GameOptions = {
                open_game: openGame,
                open_chest: openChests,
                sell_items: sellItems
            }

            // Execute scripts on each device sequentially
            const results = []

            for (const deviceId of selectedDevices) {
                try {
                    const response = await executeApi.runScript(selectedScript, deviceId, gameOptions)
                    results.push({ deviceId, success: true, data: response.data })
                } catch (error) {
                    results.push({ deviceId, success: false, error })
                }
            }

            return results
        },
        onSuccess: (results) => {
            // Store counts before clearing for success message
            const deviceCount = selectedDevices.length
            const successCount = results.filter(r => r.success).length

            // Clear form selections after successful run
            setSelectedDevices([])
            setSelectedScript('')

            // Invalidate and refetch devices data immediately for faster UI update
            queryClient.invalidateQueries({ queryKey: ['devices'] })

            // Show success feedback
            console.log(`Successfully started script on ${successCount}/${deviceCount} device(s)`)

            // Log any failures
            const failures = results.filter(r => !r.success)
            if (failures.length > 0) {
                console.error('Failed devices:', failures)
            }
        },
        onError: (error) => {
            // Handle errors gracefully
            console.error('Failed to start script:', error)
        },
    })

    const stopAllMutation = useMutation({
        mutationFn: () => executeApi.stopAllDevices(),
        onSuccess: (response) => {
            // Immediately invalidate and refetch for faster UI update
            queryClient.invalidateQueries({ queryKey: ['devices'] })
            queryClient.refetchQueries({ queryKey: ['devices'] })

            // Log detailed results for debugging
            const result = response.data
            console.log(`Stop All completed: stopped ${result.stopped_count} device(s)`)

            if (result.errors.length > 0) {
                console.warn('Some devices failed to stop:', result.errors)
            }
        },
        onError: (error) => {
            console.error('Stop All failed:', error)
            // Still try to refresh devices in case some were stopped
            queryClient.invalidateQueries({ queryKey: ['devices'] })
        },
    })

    const stopDeviceMutation = useMutation({
        mutationFn: (executionId: string) => executeApi.stopScript(executionId),
        onSuccess: (_, executionId) => {
            // Immediately invalidate and refetch for faster UI update
            queryClient.invalidateQueries({ queryKey: ['devices'] })
            queryClient.refetchQueries({ queryKey: ['devices'] })
            console.log(`Successfully stopped execution ${executionId}`)
        },
        onError: (error, executionId) => {
            console.error(`Failed to stop execution ${executionId}:`, error)
            // Still try to refresh in case of partial success
            queryClient.invalidateQueries({ queryKey: ['devices'] })
        },
    })

    // Convert devices and scripts to options format
    const deviceOptions = devices.map((device: Device) => {
        const isRunning = !!(device.current_script && device.status === 'busy')
        return {
            value: device.id,
            label: device.name,
            description: `Status: ${device.status}${isRunning ? ' (Running - Cannot select)' : ''}`,
            disabled: isRunning
        }
    })

    const scriptOptions = scripts.map((script: Script) => ({
        value: script.id,
        label: script.name,
    }))

    const handleRunNow = () => {
        runMutation.mutate()
    }

    const handleStopAll = () => {
        stopAllMutation.mutate()
    }

    const handleStopDevice = (deviceId: string) => {
        // Find the device and get its execution_id
        const device = devices.find((d: Device) => d.id === deviceId)
        if (!device || !device.current_execution_id) {
            console.error(`No execution_id found for device ${deviceId}`)
            return
        }

        // Add device to stopping set for UI feedback
        setStoppingDevices(prev => new Set([...prev, deviceId]))

        stopDeviceMutation.mutate(device.current_execution_id, {
            onSettled: () => {
                // Remove device from stopping set when operation completes
                setStoppingDevices(prev => {
                    const newSet = new Set(prev)
                    newSet.delete(deviceId)
                    return newSet
                })
            }
        })
    }

    const runningDevices = devices.filter((device: Device) => device.current_script && device.status === 'busy')

    const handleViewDevice = (deviceId: string) => {
        setSelectedDeviceDetail(deviceId)
        setShowDetailModal(true)
    }

    const handleViewLogs = (deviceId: string) => {
        setSelectedDeviceForLogs(deviceId)
        setShowLogModal(true)
    }

    const getScriptDisplayName = (scriptId: string | null | undefined): string => {
        if (!scriptId) return 'No script';
        const script = scripts.find((s: Script) => s.id === scriptId);
        return script ? script.name : scriptId; // Fallback to ID if name not found
    }


    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700">
            <div className="container mx-auto px-4 py-4 sm:py-8 max-w-7xl">
                <div className="text-center mb-8">
                    <div className="space-y-3">
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white mb-3 tracking-tight">
                            <span className="bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent drop-shadow-lg">
                                KVTM Auto Tools
                            </span>
                        </h1>
                        <div className="flex items-center justify-center space-x-2">
                            <div className="h-px bg-gradient-to-r from-transparent via-white to-transparent w-16 opacity-60"></div>
                            <div className="w-2 h-2 bg-white rounded-full opacity-80"></div>
                            <div className="h-px bg-gradient-to-r from-transparent via-white to-transparent w-16 opacity-60"></div>
                        </div>
                        <div className="flex justify-center items-center space-x-4 pt-2">
                            <div className="w-1 h-1 bg-blue-200 rounded-full animate-bounce [animation-delay:0ms]"></div>
                            <div className="w-1 h-1 bg-blue-300 rounded-full animate-bounce [animation-delay:150ms]"></div>
                            <div className="w-1 h-1 bg-blue-200 rounded-full animate-bounce [animation-delay:300ms]"></div>
                        </div>
                    </div>
                </div>

                <div className="relative z-10 bg-white rounded-xl shadow-2xl p-6 sm:p-8 mb-8 backdrop-blur-sm bg-opacity-95">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-lg sm:text-xl font-bold text-gray-900">Control Panel</h2>
                        <button 
                            onClick={() => setIsControlPanelExpanded(!isControlPanelExpanded)}
                            className="lg:hidden inline-flex items-center px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                        >
                            {isControlPanelExpanded ? (
                                <>
                                    <span className="text-sm font-medium text-gray-700 mr-2">Hide</span>
                                    <ChevronUp className="w-4 h-4 text-gray-600" />
                                </>
                            ) : (
                                <>
                                    <span className="text-sm font-medium text-gray-700 mr-2">Show</span>
                                    <ChevronDown className="w-4 h-4 text-gray-600" />
                                </>
                            )}
                        </button>
                    </div>
                    
                    {/* Collapsible content on mobile, always visible on desktop */}
                    <div className={isControlPanelExpanded ? 'block transition-all duration-300' : 'hidden lg:block transition-all duration-300'}>
                        {/* Device and Script Selection - Same line on desktop */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                            <MultiSelect
                                options={deviceOptions}
                                values={selectedDevices}
                                onChange={setSelectedDevices}
                                placeholder="Select devices..."
                                label="Devices"
                            />
                            <SearchableSelect
                                options={scriptOptions}
                                value={selectedScript}
                                onChange={setSelectedScript}
                                placeholder="Select script..."
                                label="Script"
                            />
                        </div>

                        {/* Game Options and Run Button - Equal width distribution */}
                        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-end">
                            <div className="lg:col-span-3">
                                <h3 className="text-sm font-medium text-gray-700 mb-3">Game Options</h3>
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                    <label className="flex items-center px-3 h-12 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200">
                                        <input
                                            type="checkbox"
                                            checked={openGame}
                                            onChange={(e) => setOpenGame(e.target.checked)}
                                            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="ml-3 text-sm text-gray-700 font-medium">Open Game</span>
                                    </label>
                                    <label className="flex items-center px-3 h-12 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200">
                                        <input
                                            type="checkbox"
                                            checked={openChests}
                                            onChange={(e) => setOpenChests(e.target.checked)}
                                            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="ml-3 text-sm text-gray-700 font-medium">Open Chests</span>
                                    </label>
                                    <label className="flex items-center px-3 h-12 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200">
                                        <input
                                            type="checkbox"
                                            checked={sellItems}
                                            onChange={(e) => setSellItems(e.target.checked)}
                                            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="ml-3 text-sm text-gray-700 font-medium">Sell Items</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div className="lg:col-span-1 flex justify-center lg:justify-end">
                                <button
                                    onClick={handleRunNow}
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

                <div className="relative z-0 bg-white rounded-xl shadow-2xl p-6 sm:p-8 backdrop-blur-sm bg-opacity-95">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-3">
                        <div>
                            <h2 className="text-lg sm:text-xl font-bold text-gray-900">Running Devices</h2>
                            <p className="text-sm text-gray-500 mt-1">
                                {runningDevices.length} device{runningDevices.length !== 1 ? 's' : ''} currently running
                            </p>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                onClick={handleStopAll}
                                disabled={runningDevices.length === 0 || stopAllMutation.isPending}
                                className="inline-flex items-center px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-md transition-colors text-sm min-w-[90px]"
                            >
                                {stopAllMutation.isPending ? (
                                    <>
                                        <div className="w-4 h-4 mr-2 animate-spin border-2 border-white border-t-transparent rounded-full"></div>
                                        Stopping...
                                    </>
                                ) : (
                                    <>
                                        <Square className="w-4 h-4 mr-2" />
                                        Stop All
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {runningDevices.length > 0 ? (
                        <div className="space-y-4">
                            {runningDevices.map((device: Device) => (
                                <div key={device.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
                                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                                        <div className="flex-1">
                                            <h3 className="font-semibold text-gray-900 text-lg">{device.name}</h3>
                                            <p className="text-sm text-gray-600 mt-1">
                                                Script: <span className="font-medium">{getScriptDisplayName(device.current_script)}</span>
                                            </p>
                                            <p className="text-xs text-gray-500 mt-1">
                                                Last seen: {new Date(device.last_seen).toLocaleString()}
                                            </p>
                                            <div className="flex items-center mt-2">
                                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
                                                <span className="text-sm text-green-700 font-medium">Running</span>
                                            </div>
                                        </div>
                                        
                                        {/* Action buttons - Responsive: 1x5 mobile, 3x2 tablet, 5x1 desktop */}
                                        <div className="flex flex-col gap-2 sm:grid sm:grid-cols-3 sm:gap-2 lg:flex lg:flex-row lg:space-x-2">
                                            <button
                                                onClick={() => handleStopDevice(device.id)}
                                                disabled={stoppingDevices.has(device.id)}
                                                className="inline-flex items-center justify-center px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors min-w-[80px]"
                                            >
                                                {stoppingDevices.has(device.id) ? (
                                                    <>
                                                        <div className="w-4 h-4 mr-1 animate-spin border-2 border-white border-t-transparent rounded-full"></div>
                                                        Stop...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Square className="w-4 h-4 mr-1" />
                                                        Stop
                                                    </>
                                                )}
                                            </button>
                                            <button
                                                onClick={() => alert("Support later")}
                                                className="inline-flex items-center justify-center px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm font-medium transition-colors min-w-[80px]"
                                            >
                                                <Monitor className="w-4 h-4 mr-1" />
                                                View
                                            </button>
                                            <button 
                                                onClick={() => handleViewLogs(device.id)}
                                                className="inline-flex items-center justify-center px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm font-medium transition-colors min-w-[80px]"
                                            >
                                                <ScrollText className="w-4 h-4 mr-1" />
                                                Logs
                                            </button>
                                            <button 
                                                onClick={() => handleViewDevice(device.id)}
                                                className="inline-flex items-center justify-center px-3 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 text-sm font-medium transition-colors min-w-[80px]"
                                            >
                                                <Info className="w-4 h-4 mr-1" />
                                                Detail
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

            <DeviceDetailModal 
                isOpen={showDetailModal} 
                onClose={() => setShowDetailModal(false)}
                deviceId={selectedDeviceDetail}
            />
            <DeviceLogModal 
                isOpen={showLogModal} 
                onClose={() => setShowLogModal(false)}
                deviceId={selectedDeviceForLogs}
            />
        </div>
    )
}

export default App
