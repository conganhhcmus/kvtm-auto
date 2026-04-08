import type React from 'react'
import { useEffect, useRef, useState, useCallback } from 'react'
import { ScrollText, Copy, RefreshCw } from 'lucide-react'
import { getLogConnection, startLogConnection } from '@/shared/lib/signalr'
import Modal from '@/shared/components/Modal'

interface DeviceLogModalProps {
  isOpen: boolean
  onClose: () => void
  deviceId: string
}

const DeviceLogModal: React.FC<DeviceLogModalProps> = ({ isOpen, onClose, deviceId }) => {
  const logContainerRef = useRef<HTMLDivElement>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isConnected, setIsConnected] = useState(false)

  const loadLogsAndSubscribe = useCallback(async (signal: AbortSignal) => {
    setIsLoading(true)
    try {
      const conn = getLogConnection()
      await startLogConnection()
      if (signal.aborted) return

      setIsConnected(true)

      const history: string[] = await conn.invoke('GetLogs', deviceId)
      if (signal.aborted) return
      setLogs(history)

      await conn.invoke('SubscribeLogs', deviceId)
    } catch {
      // connection failed — logs will be empty
    } finally {
      setIsLoading(false)
    }
  }, [deviceId])

  useEffect(() => {
    if (!isOpen || !deviceId) return

    const controller = new AbortController()

    const conn = getLogConnection()

    const onReceiveLog = (entry: string) => {
      setLogs(prev => [...prev, entry])
    }

    conn.on('ReceiveLog', onReceiveLog)
    loadLogsAndSubscribe(controller.signal)

    return () => {
      controller.abort()
      conn.off('ReceiveLog', onReceiveLog)
      conn.invoke('UnsubscribeLogs', deviceId).catch(() => {})
      setLogs([])
      setIsConnected(false)
    }
  }, [isOpen, deviceId, loadLogsAndSubscribe])

  // Auto-scroll to bottom on new log entries
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])

  const handleRefresh = () => {
    setLogs([])
    setIsConnected(false)
    const controller = new AbortController()
    loadLogsAndSubscribe(controller.signal)
  }

  const handleCopyLogs = () => {
    if (logs.length) navigator.clipboard.writeText(logs.join('\n'))
  }

  const getLogColor = (line: string) => {
    const lower = line.toLowerCase()
    if (lower.includes('error') || lower.includes('traceback')) return 'text-red-400'
    if (lower.includes('warning') || lower.includes('warn')) return 'text-yellow-400'
    if (lower.includes('started') || lower.includes('completed')) return 'text-green-400'
    return 'text-gray-300'
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Device Logs - ${deviceId}`}>
      <div className="space-y-4">
        <div className="flex items-center justify-between pb-2 border-b">
          <div className="flex items-center space-x-2">
            <ScrollText className="w-5 h-5 text-gray-600" />
            <span className="text-sm text-gray-600">
              {isLoading ? 'Connecting...' : `${logs.length} log entries`}
            </span>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="inline-flex items-center px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={handleCopyLogs}
              disabled={!logs.length}
              className="inline-flex items-center px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50 transition-colors"
            >
              <Copy className="w-4 h-4 mr-1" />
              Copy All
            </button>
          </div>
        </div>

        <div
          ref={logContainerRef}
          className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-96 overflow-y-auto border"
          style={{ fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace' }}
        >
          {isLoading ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              <RefreshCw className="w-6 h-6 mr-2 animate-spin" />
              Connecting...
            </div>
          ) : !logs.length ? (
            <div className="flex items-center justify-center h-full text-gray-500">
              No logs available for this device.
            </div>
          ) : (
            <div className="space-y-1">
              {logs.map((line, i) => (
                <div key={i} className={`leading-relaxed ${getLogColor(line)}`}>{line}</div>
              ))}
            </div>
          )}
        </div>

        <div className="text-xs text-gray-500 pt-2 border-t flex items-center space-x-1">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`} />
          <span>{isConnected ? 'Live via SignalR' : 'Disconnected'}</span>
        </div>
      </div>
    </Modal>
  )
}

export default DeviceLogModal
