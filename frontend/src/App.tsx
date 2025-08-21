import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { deviceApi, scriptApi, GameOptions } from '@/api'
import { ChevronDown, X, FileText, ChevronUp } from 'lucide-react'
import DeviceModal from '@/components/DeviceModal'
import LogsModal from '@/components/LogsModal'
import DeviceDetailModal from '@/components/DeviceDetailModal'

interface Device {
    id: string
    device_name: string
    device_status: string
    device_running_id?: string
    screen_size?: [number, number]
    last_seen?: string
    current_script?: {
        script_id: string
        script_name: string
        execution_id: string
        state: string
        started_at: string
    }
}

interface Script {
    id: string
    name: string
    description?: string
}

interface ScriptExecution {
    id: string
    script_id: string
    device_ids: string[]
    status: 'running' | 'completed' | 'failed'
    started_at: string
    completed_at?: string
}

function App() {
    const queryClient = useQueryClient()
    const [selectedDevice, setSelectedDevice] = useState('')
    const [selectedScript, setSelectedScript] = useState('')
    const [openGame, setOpenGame] = useState(true)
    const [openChests, setOpenChests] = useState(true)
    const [sellItems, setSellItems] = useState(true)
  
    const [showDeviceModal, setShowDeviceModal] = useState(false)
    const [showLogsModal, setShowLogsModal] = useState(false)
    const [showDetailModal, setShowDetailModal] = useState(false)
    const [selectedDeviceDetail, setSelectedDeviceDetail] = useState('')
    const [showDeviceTable, setShowDeviceTable] = useState(false)

    const { data: devices = [] } = useQuery({
        queryKey: ['devices'],
        queryFn: () => deviceApi.getDevices().then(res => res.data),
    })

    const { data: scripts = [] } = useQuery({
        queryKey: ['scripts'],
        queryFn: () => scriptApi.getScripts().then(res => res.data),
    })

    const runMutation = useMutation({
        mutationFn: () => {
            if (!selectedDevice) throw new Error('No device selected')
            if (!selectedScript) throw new Error('No script selected')
            
            const gameOptions: GameOptions = {
                open_game: openGame,
                open_chest: openChests,
                sell_items: sellItems
            }
            
            return scriptApi.runScript(selectedScript, [selectedDevice], gameOptions)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['devices'] })
        },
    })

    const stopAllMutation = useMutation({
        mutationFn: async () => {
            const executions = await scriptApi.getScriptExecutions()
            const runningExecutions = executions.data.filter((exec: ScriptExecution) => exec.status === 'running')
            await Promise.all(runningExecutions.map((exec: ScriptExecution) => scriptApi.stopScript(exec.id)))
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['devices'] })
        },
    })

    const stopDeviceMutation = useMutation({
        mutationFn: async (deviceId: string) => {
            const executions = await scriptApi.getScriptExecutions()
            const deviceExecutions = executions.data.filter((exec: ScriptExecution) => 
                exec.status === 'running' && exec.device_ids.includes(deviceId)
            )
            await Promise.all(deviceExecutions.map((exec: ScriptExecution) => scriptApi.stopScript(exec.id)))
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['devices'] })
        },
    })

    const removeDevice = (deviceId: string) => {
        setSelectedDevice(prev => prev === deviceId ? '' : prev)
    }

    const handleRunNow = () => {
        runMutation.mutate()
    }

    const handleStopAll = () => {
        stopAllMutation.mutate()
    }

    const handleStopDevice = (deviceId: string) => {
        stopDeviceMutation.mutate(deviceId)
    }

    const runningDevices = devices.filter((device: Device) => device.current_script && device.current_script.state === 'running')

    const handleViewDevice = (deviceId: string) => {
        setSelectedDeviceDetail(deviceId)
        setShowDetailModal(true)
    }

    const toggleDeviceTable = () => {
        setShowDeviceTable(!showDeviceTable)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600">
            <div className="container mx-auto px-4 py-4 sm:py-8 max-w-6xl">
                <div className="text-center mb-6 sm:mb-8">
                    <h1 className="text-2xl sm:text-3xl font-bold text-white mb-4">Welcome to Auto Tools!</h1>
          
                </div>

                <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6 mb-6 sm:mb-8">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
                        <div>
                            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">Settings</h2>
              
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Devices</label>
                                    <div className="relative">
                                        <select
                                            value={selectedDevice}
                                            onChange={(e) => setSelectedDevice(e.target.value)}
                                            className="w-full p-3 border border-gray-300 rounded-lg appearance-none bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
                                        >
                                            <option value="">Select Device</option>
                                            {devices.map((device: Device) => (
                                                <option key={device.id} value={device.id}>
                                                    {device.device_name || device.id}
                                                </option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                                        {selectedDevice && (
                                            <button
                                                onClick={() => removeDevice(selectedDevice)}
                                                className="absolute right-10 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Script</label>
                                    <div className="relative">
                                        <select
                                            value={selectedScript}
                                            onChange={(e) => setSelectedScript(e.target.value)}
                                            className="w-full p-3 border border-gray-300 rounded-lg appearance-none bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
                                        >
                                            <option value="">Select Script</option>
                                            {scripts.map((script: Script) => (
                                                <option key={script.id} value={script.id}>
                                                    {script.name}
                                                </option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">Game Option</h2>
              
                            <div className="space-y-4">

                                <div className="grid grid-cols-3 gap-2 sm:gap-4">
                                    <label className="flex items-center">
                                        <input
                                            type="checkbox"
                                            checked={openGame}
                                            onChange={(e) => setOpenGame(e.target.checked)}
                                            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="ml-1 sm:ml-2 text-xs sm:text-sm text-gray-700">Open Game</span>
                                    </label>
                  
                                    <label className="flex items-center">
                                        <input
                                            type="checkbox"
                                            checked={openChests}
                                            onChange={(e) => setOpenChests(e.target.checked)}
                                            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="ml-1 sm:ml-2 text-xs sm:text-sm text-gray-700">Open Chests</span>
                                    </label>
                  
                                    <label className="flex items-center">
                                        <input
                                            type="checkbox"
                                            checked={sellItems}
                                            onChange={(e) => setSellItems(e.target.checked)}
                                            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="ml-1 sm:ml-2 text-xs sm:text-sm text-gray-700">Sell Items</span>
                                    </label>
                                </div>


                                <div className="flex justify-start">
                                    <button
                                        onClick={handleRunNow}
                                        disabled={!selectedDevice || !selectedScript || runMutation.isPending}
                                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm sm:text-base"
                                    >
                    Run now!
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {/* Collapse/Expand icon at bottom of settings */}
                    <div className="flex justify-center pt-4 border-t border-gray-200">
                        <button
                            onClick={toggleDeviceTable}
                            className="flex items-center justify-center w-10 h-10 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                            title={showDeviceTable ? "Hide Device Table" : "Show Device Table"}
                        >
                            {showDeviceTable ? (
                                <ChevronUp className="w-5 h-5 text-gray-600" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-gray-600" />
                            )}
                        </button>
                    </div>
                </div>

                <div className={`bg-white rounded-lg shadow-lg p-4 sm:p-6 transition-all duration-300 ${!showDeviceTable ? 'hidden' : ''}`}>
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 sm:mb-6 gap-3">
                        <h2 className="text-lg sm:text-xl font-bold text-gray-900">Running Devices</h2>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => setShowLogsModal(true)}
                                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-md transition-colors text-sm sm:text-base"
                            >
                                <FileText className="w-4 h-4 mr-2" />
                                Logs
                            </button>
                            <button
                                onClick={handleStopAll}
                                disabled={runningDevices.length === 0 || stopAllMutation.isPending}
                                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
                            >
                                Stop All
                            </button>
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full table-auto min-w-[600px]">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="text-left py-3 px-2 sm:px-4 font-medium text-gray-700 text-sm">
                                        <input type="checkbox" className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded" />
                                    </th>
                                    <th className="text-left py-3 px-2 sm:px-4 font-medium text-gray-700 text-sm">Device</th>
                                    <th className="text-left py-3 px-2 sm:px-4 font-medium text-gray-700 text-sm">Script</th>
                                    <th className="text-left py-3 px-2 sm:px-4 font-medium text-gray-700 text-sm">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {runningDevices.map((device: Device) => (
                                    <tr key={device.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="py-3 sm:py-4 px-2 sm:px-4">
                                            <input type="checkbox" className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded" />
                                        </td>
                                        <td className="py-3 sm:py-4 px-2 sm:px-4 font-medium text-gray-900 text-sm">
                                            {device.device_name || device.id}
                                        </td>
                                        <td className="py-3 sm:py-4 px-2 sm:px-4 text-gray-700 text-sm">
                                            {device.current_script?.script_name || 'No script'}
                                        </td>
                                        <td className="py-3 sm:py-4 px-2 sm:px-4">
                                            <div className="flex flex-wrap gap-1 sm:gap-2">
                                                <button
                                                    onClick={() => handleStopDevice(device.id)}
                                                    className="px-2 sm:px-3 py-1 bg-red-500 text-white rounded text-xs sm:text-sm hover:bg-red-600"
                                                >
                          Stop
                                                </button>
                                                <button 
                                                    onClick={() => handleViewDevice(device.id)}
                                                    className="px-2 sm:px-3 py-1 bg-blue-500 text-white rounded text-xs sm:text-sm hover:bg-blue-600"
                                                >
                          View
                                                </button>
                                                <button 
                                                    onClick={() => setShowLogsModal(true)}
                                                    className="px-2 sm:px-3 py-1 bg-blue-500 text-white rounded text-xs sm:text-sm hover:bg-blue-600"
                                                >
                          Logs
                                                </button>
                                                <button 
                                                    onClick={() => handleViewDevice(device.id)}
                                                    className="px-2 sm:px-3 py-1 bg-blue-500 text-white rounded text-xs sm:text-sm hover:bg-blue-600"
                                                >
                          Detail
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                                <tr className="border-b border-gray-100 hover:bg-gray-50">
                                    <td className="py-3 sm:py-4 px-2 sm:px-4">
                                        <input type="checkbox" className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded" />
                                    </td>
                                    <td className="py-3 sm:py-4 px-2 sm:px-4 font-medium text-gray-900 text-sm">
                    Kai
                                    </td>
                                    <td className="py-3 sm:py-4 px-2 sm:px-4 text-gray-700 text-sm">
                    Example Script
                                    </td>
                                    <td className="py-3 sm:py-4 px-2 sm:px-4">
                                        <div className="flex flex-wrap gap-1 sm:gap-2">
                                            <button 
                                                onClick={() => handleStopDevice('kai')}
                                                className="px-2 sm:px-3 py-1 bg-red-500 text-white rounded text-xs sm:text-sm hover:bg-red-600"
                                            >
                        Stop
                                            </button>
                                            <button 
                                                onClick={() => handleViewDevice('kai')}
                                                className="px-2 sm:px-3 py-1 bg-blue-500 text-white rounded text-xs sm:text-sm hover:bg-blue-600"
                                            >
                        View
                                            </button>
                                            <button 
                                                onClick={() => setShowLogsModal(true)}
                                                className="px-2 sm:px-3 py-1 bg-blue-500 text-white rounded text-xs sm:text-sm hover:bg-blue-600"
                                            >
                        Logs
                                            </button>
                                            <button 
                                                onClick={() => handleViewDevice('kai')}
                                                className="px-2 sm:px-3 py-1 bg-blue-500 text-white rounded text-xs sm:text-sm hover:bg-blue-600"
                                            >
                        Detail
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                {runningDevices.length === 0 && (
                                    <tr>
                                        <td colSpan={4} className="py-8 text-center text-gray-500 text-sm">
                      No devices are currently running
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>

                    <div className="flex justify-center mt-4 sm:mt-6">
                        <div className="flex items-center space-x-2">
                            <button className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">
                &lt;
                            </button>
                            <button className="px-3 py-1 bg-blue-500 text-white rounded text-sm">
                1
                            </button>
                            <button className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50">
                &gt;
                            </button>
                        </div>
                    </div>
                </div>

                <div className="text-center mt-8">
                    <p className="text-white text-sm">© Design by conganhhcmus</p>
                </div>
            </div>

            <DeviceModal 
                isOpen={showDeviceModal} 
                onClose={() => setShowDeviceModal(false)} 
            />
            <LogsModal 
                isOpen={showLogsModal} 
                onClose={() => setShowLogsModal(false)} 
            />
            <DeviceDetailModal 
                isOpen={showDetailModal} 
                onClose={() => setShowDetailModal(false)}
                deviceId={selectedDeviceDetail}
            />
        </div>
    )
}

export default App
