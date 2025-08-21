import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { deviceApi } from '@/api'
import { Smartphone, Wifi, WifiOff, RefreshCw } from 'lucide-react'
import Modal from '@/components/Modal'

interface Device {
    id: string
    name: string
    status: 'connected' | 'disconnected' | 'offline'
    model?: string
    android_version?: string
    last_seen?: string
}

interface DeviceModalProps {
    isOpen: boolean
    onClose: () => void
}

const DeviceModal: React.FC<DeviceModalProps> = ({ isOpen, onClose }) => {
    const queryClient = useQueryClient()

    const { data: devices = [], isLoading, error } = useQuery({
        queryKey: ['devices'],
        queryFn: () => deviceApi.getDevices().then(res => res.data.devices),
        refetchInterval: 5000,
        enabled: isOpen,
    })

    const refreshMutation = useMutation({
        mutationFn: deviceApi.refreshDevices,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['devices'] })
        },
    })

    const connectMutation = useMutation({
        mutationFn: (deviceId: string) => deviceApi.connectDevice(deviceId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['devices'] })
        },
    })

    const disconnectMutation = useMutation({
        mutationFn: (deviceId: string) => deviceApi.disconnectDevice(deviceId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['devices'] })
        },
    })

    const getStatusColor = (status: Device['status']) => {
        switch (status) {
            case 'connected': return 'text-green-600 bg-green-100'
            case 'disconnected': return 'text-yellow-600 bg-yellow-100'
            case 'offline': return 'text-red-600 bg-red-100'
            default: return 'text-gray-600 bg-gray-100'
        }
    }

    const getStatusIcon = (status: Device['status']) => {
        switch (status) {
            case 'connected': return <Wifi className="w-4 h-4" />
            case 'disconnected': case 'offline': return <WifiOff className="w-4 h-4" />
            default: return <Smartphone className="w-4 h-4" />
        }
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Device Management" size="lg">
            <div>
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold text-gray-900">Android Devices</h2>
                    <button
                        onClick={() => refreshMutation.mutate()}
                        disabled={refreshMutation.isPending}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 mr-2 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
            Refresh
                    </button>
                </div>

                {isLoading && (
                    <div className="text-center py-8">Loading devices...</div>
                )}

                {error ? (
                    <div className="text-red-600 text-center py-8">
                        Error loading devices: {(error as Error)?.message || 'Unknown error'}
                    </div>
                ) : null}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                    {devices.map((device: Device) => (
                        <div key={device.id} className="bg-gray-50 rounded-lg shadow p-4">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center">
                                    <Smartphone className="w-6 h-6 text-gray-600 mr-2" />
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">{device.name || device.id}</h3>
                                        <p className="text-sm text-gray-500">{device.model}</p>
                                    </div>
                                </div>
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(device.status)}`}>
                                    {getStatusIcon(device.status)}
                                    <span className="ml-1 capitalize">{device.status}</span>
                                </span>
                            </div>

                            <div className="space-y-2 text-sm text-gray-600 mb-4">
                                {device.android_version && (
                                    <p>Android: {device.android_version}</p>
                                )}
                                {device.last_seen && (
                                    <p>Last seen: {new Date(device.last_seen).toLocaleString()}</p>
                                )}
                            </div>

                            <div className="flex space-x-2">
                                {device.status === 'disconnected' ? (
                                    <button
                                        onClick={() => connectMutation.mutate(device.id)}
                                        disabled={connectMutation.isPending}
                                        className="flex-1 bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50"
                                    >
                    Connect
                                    </button>
                                ) : device.status === 'connected' ? (
                                    <button
                                        onClick={() => disconnectMutation.mutate(device.id)}
                                        disabled={disconnectMutation.isPending}
                                        className="flex-1 bg-red-600 text-white px-3 py-2 rounded text-sm hover:bg-red-700 disabled:opacity-50"
                                    >
                    Disconnect
                                    </button>
                                ) : (
                                    <button
                                        disabled
                                        className="flex-1 bg-gray-400 text-white px-3 py-2 rounded text-sm cursor-not-allowed"
                                    >
                    Offline
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                {devices.length === 0 && !isLoading && (
                    <div className="text-center py-12">
                        <Smartphone className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No devices found</h3>
                        <p className="text-gray-500">Connect Android devices via USB and enable USB debugging</p>
                    </div>
                )}
            </div>
        </Modal>
    )
}

export default DeviceModal
