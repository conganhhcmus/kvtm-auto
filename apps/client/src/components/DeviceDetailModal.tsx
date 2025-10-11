import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { deviceApi } from '@/api'
import { Smartphone, Settings } from 'lucide-react'
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
        <Modal isOpen={isOpen} onClose={onClose} title="Device Details">
            <div>
                {isLoading && (
                    <div className="text-center py-8">Loading device details...</div>
                )}

                {!!error && (
                    <div className="text-red-600 text-center py-8">Error loading device details</div>
                )}

                {device && (
                    <div className="space-y-6">
                        {/* Device Header */}
                        <div className="flex items-center space-x-4">
                            <Smartphone className="w-12 h-12 text-gray-600" />
                            <div>
                                <h3 className="text-xl font-bold text-gray-900">{device.name}</h3>
                                <p className="text-gray-600">{`Device ${device.id}`}</p>
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
                                        <span className="text-gray-600">Last Seen:</span>
                                        <span className="font-medium text-xs">
                                            {device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Unknown'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Running Options */}
                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                                    <Settings className="w-5 h-5 mr-2" />
                                    Running Options
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Script Name:</span>
                                        <span className="font-medium">{device.current_script_name || 'No script running'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Open Game:</span>
                                        <span className={`font-medium ${device.game_options?.open_game ? 'text-green-600' : 'text-gray-500'}`}>
                                            {device.game_options?.open_game ? 'Enabled' : 'Disabled'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Open Chest:</span>
                                        <span className={`font-medium ${device.game_options?.open_chest ? 'text-green-600' : 'text-gray-500'}`}>
                                            {device.game_options?.open_chest ? 'Enabled' : 'Disabled'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Sell Items:</span>
                                        <span className={`font-medium ${device.game_options?.sell_items ? 'text-green-600' : 'text-gray-500'}`}>
                                            {device.game_options?.sell_items ? 'Enabled' : 'Disabled'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </Modal>
    )
}

export default DeviceDetailModal
