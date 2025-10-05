import React, { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ScrollText, Copy, RefreshCw } from 'lucide-react'
import { deviceApi } from '@/api'
import Modal from './Modal'

interface DeviceLogModalProps {
    isOpen: boolean
    onClose: () => void
    deviceId: string
}

// LogResponse is now just an array of strings
type LogResponse = string[]

const DeviceLogModal: React.FC<DeviceLogModalProps> = ({ isOpen, onClose, deviceId }) => {
    const logContainerRef = useRef<HTMLDivElement>(null)
    
    const { data: logData, isLoading, isError, refetch } = useQuery<LogResponse>({
        queryKey: ['device-logs', deviceId],
        queryFn: () => deviceApi.getDeviceLogs(deviceId, 500).then(res => res.data),
        enabled: isOpen && !!deviceId,
        refetchInterval: 3000, // Auto-refresh every 3 seconds
    })

    // Auto-scroll to bottom when new logs are added
    useEffect(() => {
        if (logContainerRef.current && logData) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
        }
    }, [logData])

    const handleCopyLogs = () => {
        if (logData) {
            const logText = logData.join('\n')
            navigator.clipboard.writeText(logText)
        }
    }

    const getLogColor = (logLine: string) => {
        const lowerLine = logLine.toLowerCase()
        if (lowerLine.includes('error') || lowerLine.includes('traceback') || lowerLine.includes('modulenotfounderror')) {
            return 'text-red-400'
        }
        if (lowerLine.includes('warning') || lowerLine.includes('warn')) {
            return 'text-yellow-400'
        }
        if (lowerLine.includes('started') || lowerLine.includes('completed')) {
            return 'text-green-400'
        }
        return 'text-gray-300'
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={`Device Logs - ${deviceId}`}>
            <div className="space-y-4">
                {/* Header with controls */}
                <div className="flex items-center justify-between pb-2 border-b">
                    <div className="flex items-center space-x-2">
                        <ScrollText className="w-5 h-5 text-gray-600" />
                        <span className="text-sm text-gray-600">
                            {logData ? `${logData.length} log entries` : 'Loading logs...'}
                        </span>
                    </div>
                    <div className="flex space-x-2">
                        <button
                            onClick={() => refetch()}
                            disabled={isLoading}
                            className="inline-flex items-center px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 disabled:opacity-50 transition-colors"
                        >
                            <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                            Refresh
                        </button>
                        <button
                            onClick={handleCopyLogs}
                            disabled={!logData?.length}
                            className="inline-flex items-center px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50 transition-colors"
                        >
                            <Copy className="w-4 h-4 mr-1" />
                            Copy All
                        </button>
                    </div>
                </div>

                {/* Log content */}
                <div 
                    ref={logContainerRef}
                    className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-96 overflow-y-auto border"
                    style={{ fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace' }}
                >
                    {isLoading ? (
                        <div className="flex items-center justify-center h-full text-gray-500">
                            <RefreshCw className="w-6 h-6 mr-2 animate-spin" />
                            Loading logs...
                        </div>
                    ) : isError ? (
                        <div className="flex items-center justify-center h-full text-red-400">
                            <span>Error loading logs. Please try refreshing.</span>
                        </div>
                    ) : !logData?.length ? (
                        <div className="flex items-center justify-center h-full text-gray-500">
                            <span>No logs available for this device.</span>
                        </div>
                    ) : (
                        <div className="space-y-1">
                            {logData.map((logLine, index) => (
                                <div key={index} className={`leading-relaxed ${getLogColor(logLine)}`}>
                                    {logLine}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer info */}
                <div className="text-xs text-gray-500 pt-2 border-t">
                    Auto-refreshes every 3 seconds • Scroll to see older logs • Click "Copy All" to copy all logs to clipboard
                </div>
            </div>
        </Modal>
    )
}

export default DeviceLogModal