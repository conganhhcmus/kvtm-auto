import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { deviceApi } from '@/api'
import { Smartphone, Battery, Cpu, HardDrive, Wifi } from 'lucide-react'
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
                        <div className="flex items-center space-x-4">
                            <Smartphone className="w-12 h-12 text-gray-600" />
                            <div>
                                <h3 className="text-xl font-bold text-gray-900">{device.name || device.id}</h3>
                                <p className="text-gray-600">{device.model}</p>
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    device.status === 'connected' ? 'text-green-600 bg-green-100' :
                                        device.status === 'disconnected' ? 'text-yellow-600 bg-yellow-100' :
                                            'text-red-600 bg-red-100'
                                }`}>
                                    {device.status}
                                </span>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                                    <Cpu className="w-5 h-5 mr-2" />
                  System Information
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Android Version:</span>
                                        <span className="font-medium">{device.android_version || 'Unknown'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">API Level:</span>
                                        <span className="font-medium">{device.api_level || 'Unknown'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Architecture:</span>
                                        <span className="font-medium">{device.architecture || 'Unknown'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Serial:</span>
                                        <span className="font-medium font-mono text-xs">{device.id}</span>
                                    </div>
                                </div>
                            </div>

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
                                        <span className="text-gray-600">Last Seen:</span>
                                        <span className="font-medium">
                                            {device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Unknown'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                                    <Battery className="w-5 h-5 mr-2" />
                  Hardware Status
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Battery Level:</span>
                                        <span className="font-medium">{device.battery_level ? `${device.battery_level}%` : 'Unknown'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Screen State:</span>
                                        <span className="font-medium">{device.screen_on ? 'On' : 'Off'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">CPU Usage:</span>
                                        <span className="font-medium">{device.cpu_usage ? `${device.cpu_usage}%` : 'Unknown'}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                                    <HardDrive className="w-5 h-5 mr-2" />
                  Storage
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Total Storage:</span>
                                        <span className="font-medium">{device.total_storage || 'Unknown'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Available:</span>
                                        <span className="font-medium">{device.available_storage || 'Unknown'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">RAM:</span>
                                        <span className="font-medium">{device.ram || 'Unknown'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {device.current_auto && (
                            <div className="bg-blue-50 rounded-lg p-4">
                                <h4 className="font-semibold text-blue-900 mb-2">Current Automation</h4>
                                <p className="text-blue-800">Running: {device.current_auto}</p>
                                <p className="text-blue-600 text-sm">Game: Khu Vườn Trên Mây</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </Modal>
    )
}

export default DeviceDetailModal
