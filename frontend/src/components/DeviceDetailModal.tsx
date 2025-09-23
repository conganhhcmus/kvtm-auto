import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { deviceApi } from '@/api'
import { Smartphone, Wifi, PlayCircle, Settings } from 'lucide-react'
import Modal from '@/components/Modal'

interface DeviceDetailModalProps {
    isOpen: boolean
    onClose: () => void
    deviceId: string
}

const DeviceDetailModal: React.FC<DeviceDetailModalProps> = ({ isOpen, onClose, deviceId }) => {
    const { data: device, isLoading, error } = useQuery({
        queryKey: ['device-detail', deviceId],
        queryFn: () => deviceApi.getDevice(deviceId).then(res => res.data),
        enabled: isOpen && !!deviceId,
    })

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Device Details" size="lg">
            <div>
                {isLoading && (
                    <div className="text-center py-8">Loading device details...</div>
                )}

                {error && (
                    <div className="text-red-600 text-center py-8">Error loading device details</div>
                )}

                {device && (
                    <div className="space-y-6">
                        {/* Device Header */}
                        <div className="flex items-center space-x-4">
                            <Smartphone className="w-12 h-12 text-gray-600" />
                            <div>
                                <h3 className="text-xl font-bold text-gray-900">{device.name}</h3>
                                <p className="text-gray-600">{device.model || `Device ${device.id}`}</p>
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    device.status === 'busy' ? 'text-green-600 bg-green-100' :
                                    device.status === 'available' ? 'text-blue-600 bg-blue-100' :
                                    'text-gray-600 bg-gray-100'
                                }`}>
                                    {device.status}
                                </span>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Device Information */}
                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                                    <Smartphone className="w-5 h-5 mr-2" />
                                    Device Information
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Device ID:</span>
                                        <span className="font-medium font-mono text-xs">{device.id}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Device Name:</span>
                                        <span className="font-medium">{device.name}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Status:</span>
                                        <span className="font-medium capitalize">{device.status}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Screen Size:</span>
                                        <span className="font-medium">
                                            {device.screen_size ? `${device.screen_size[0]}x${device.screen_size[1]}` : 'Unknown'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Last Seen:</span>
                                        <span className="font-medium text-xs">
                                            {device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Unknown'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Script Execution Info */}
                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                                    <PlayCircle className="w-5 h-5 mr-2" />
                                    Script Execution
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Script ID:</span>
                                        <span className="font-medium font-mono text-xs">{device.current_script || 'None'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Script Name:</span>
                                        <span className="font-medium">{device.script_name || 'No script running'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Execution Status:</span>
                                        <span className={`font-medium ${
                                            device.status === 'busy' ? 'text-green-600' : 'text-gray-500'
                                        }`}>
                                            {device.status === 'busy' ? 'Active' : 'Not Running'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Connection Info */}
                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                                    <Wifi className="w-5 h-5 mr-2" />
                                    Connection Info
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Connection Type:</span>
                                        <span className="font-medium">{device.connection_type || 'USB'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">IP Address:</span>
                                        <span className="font-medium">{device.ip_address || 'N/A'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Model:</span>
                                        <span className="font-medium">{device.model || 'Android Device'}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Game Options */}
                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                                    <Settings className="w-5 h-5 mr-2" />
                                    Game Options
                                </h4>
                                {device.game_options ? (
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Open Game:</span>
                                            <span className={`font-medium ${device.game_options.open_game ? 'text-green-600' : 'text-red-600'}`}>
                                                {device.game_options.open_game ? 'Enabled' : 'Disabled'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Open Chests:</span>
                                            <span className={`font-medium ${device.game_options.open_chest ? 'text-green-600' : 'text-red-600'}`}>
                                                {device.game_options.open_chest ? 'Enabled' : 'Disabled'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Sell Items:</span>
                                            <span className={`font-medium ${device.game_options.sell_items ? 'text-green-600' : 'text-red-600'}`}>
                                                {device.game_options.sell_items ? 'Enabled' : 'Disabled'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Max Loops:</span>
                                            <span className="font-medium">{device.game_options.max_loops || 1000}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Loop Delay:</span>
                                            <span className="font-medium">{device.game_options.loop_delay || 1.0}s</span>
                                        </div>
                                    </div>
                                ) : (
                                    <p className="text-gray-500 text-sm">No game options configured</p>
                                )}
                            </div>
                        </div>

                        {/* Current Script Status */}
                        {device.current_script && (
                            <div className={`rounded-lg p-4 ${
                                device.status === 'busy' ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'
                            }`}>
                                <h4 className={`font-semibold mb-2 ${
                                    device.status === 'busy' ? 'text-green-900' : 'text-yellow-900'
                                }`}>
                                    Current Script Execution
                                </h4>
                                <div className="space-y-1 text-sm">
                                    <p className={`font-medium ${
                                        device.status === 'busy' ? 'text-green-800' : 'text-yellow-800'
                                    }`}>
                                        Running: {device.script_name || device.current_script}
                                    </p>
                                    <p className={`text-xs ${
                                        device.status === 'busy' ? 'text-green-600' : 'text-yellow-600'
                                    }`}>
                                        Script ID: {device.current_script}
                                    </p>
                                    {device.status === 'busy' && (
                                        <div className="flex items-center mt-2">
                                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
                                            <span className="text-green-700 text-xs font-medium">Active</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </Modal>
    )
}

export default DeviceDetailModal
