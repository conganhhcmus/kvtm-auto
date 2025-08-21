import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { logsApi } from '@/api'
import { FileText, Download } from 'lucide-react'
import Modal from '@/components/Modal'

interface Log {
    id: string
    timestamp: string
    level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'
    message: string
    device_id?: string
    script_id?: string
}

interface LogsModalProps {
    isOpen: boolean
    onClose: () => void
}

const LogsModal: React.FC<LogsModalProps> = ({ isOpen, onClose }) => {
    const [levelFilter, setLevelFilter] = useState<string>('')
    const [deviceFilter, setDeviceFilter] = useState<string>('')

    const { data: logs = [], isLoading, error } = useQuery({
        queryKey: ['logs', levelFilter, deviceFilter],
        queryFn: () => logsApi.getLogs({
            level: levelFilter || undefined,
            device_id: deviceFilter || undefined,
            limit: 100
        }).then(res => res.data),
        refetchInterval: 2000,
        enabled: isOpen,
    })

    const getLevelColor = (level: string) => {
        switch (level) {
            case 'ERROR': return 'text-red-600 bg-red-100'
            case 'WARNING': return 'text-yellow-600 bg-yellow-100'
            case 'INFO': return 'text-blue-600 bg-blue-100'
            case 'DEBUG': return 'text-gray-600 bg-gray-100'
            default: return 'text-gray-600 bg-gray-100'
        }
    }

    const exportLogs = () => {
        const logText = logs.map((log: Log) => 
            `[${log.timestamp}] ${log.level}: ${log.message} ${log.device_id ? `(Device: ${log.device_id})` : ''}`
        ).join('\n')
    
        const blob = new Blob([logText], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `kvtm-logs-${new Date().toISOString().split('T')[0]}.txt`
        a.click()
        URL.revokeObjectURL(url)
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Application Logs" size="xl">
            <div>
                <div className="flex justify-between items-center mb-6">
                    <div className="flex space-x-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
                            <select
                                value={levelFilter}
                                onChange={(e) => setLevelFilter(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="">All Levels</option>
                                <option value="ERROR">Error</option>
                                <option value="WARNING">Warning</option>
                                <option value="INFO">Info</option>
                                <option value="DEBUG">Debug</option>
                            </select>
                        </div>
            
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Device</label>
                            <input
                                type="text"
                                value={deviceFilter}
                                onChange={(e) => setDeviceFilter(e.target.value)}
                                placeholder="Filter by device"
                                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </div>
          
                    <button
                        onClick={exportLogs}
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                    >
                        <Download className="w-4 h-4 mr-2" />
            Export
                    </button>
                </div>

                {isLoading && (
                    <div className="text-center py-8">Loading logs...</div>
                )}

                {!!error && (
                    <div className="text-red-600 text-center py-8">
            Error loading logs
                    </div>
                )}

                <div className="bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <div className="space-y-2">
                        {logs.map((log: Log) => (
                            <div key={log.id} className="flex items-start space-x-3 text-sm">
                                <span className="text-gray-400 whitespace-nowrap">
                                    {new Date(log.timestamp).toLocaleTimeString()}
                                </span>
                                <span className={`px-2 py-1 rounded text-xs font-medium ${getLevelColor(log.level)}`}>
                                    {log.level}
                                </span>
                                <span className="text-white flex-1">{log.message}</span>
                                {log.device_id && (
                                    <span className="text-blue-400 text-xs">{log.device_id}</span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {logs.length === 0 && !isLoading && (
                    <div className="text-center py-12">
                        <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No logs found</h3>
                        <p className="text-gray-500">Logs will appear here when the application is running</p>
                    </div>
                )}
            </div>
        </Modal>
    )
}

export default LogsModal
