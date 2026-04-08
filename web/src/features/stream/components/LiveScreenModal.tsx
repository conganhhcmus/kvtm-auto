import React, { useEffect, useRef, useState, useCallback } from 'react'
import { Monitor, AlertCircle, Loader2 } from 'lucide-react'
import { getScreenConnection, startScreenConnection } from '@/shared/lib/signalr'
import type { HubConnection } from '@microsoft/signalr'
import Modal from '@/shared/components/Modal'

// @ts-expect-error - JMuxer doesn't have TypeScript definitions
import JMuxer from 'jmuxer'

interface LiveScreenModalProps {
  isOpen: boolean
  onClose: () => void
  deviceId: string
  deviceName: string
}

const LiveScreenModal: React.FC<LiveScreenModalProps> = ({ isOpen, onClose, deviceId, deviceName }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const connRef = useRef<HubConnection | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const jmuxerRef = useRef<any>(null)
  const isStreamingRef = useRef(false)

  const handleClose = useCallback(() => {
    // Immediately stop streaming state
    setIsStreaming(false)
    isStreamingRef.current = false

    // Clean up JMuxer
    if (jmuxerRef.current) {
      try {
        jmuxerRef.current.destroy()
      } catch (e) {
        console.error('[LiveScreen] Error destroying JMuxer:', e)
      }
      jmuxerRef.current = null
    }

    // Stop the stream on backend
    if (connRef.current) {
      connRef.current.invoke('StopStream', deviceId).catch(() => {})
    }

    onClose()
  }, [onClose, deviceId])

  useEffect(() => {
    if (!isOpen || !deviceId) return

    // Get SignalR connection instance
    const conn = getScreenConnection()
    connRef.current = conn

    const handleConnect = () => {
      console.log('[LiveScreen] SignalR connected')
      setIsConnected(true)
      setError(null)

      // Start streaming
      conn.invoke('StartStream', deviceId).catch((err) => {
        console.error('[LiveScreen] Failed to start stream:', err)
        setError(String(err))
      })
    }

    const handleDisconnect = () => {
      console.log('[LiveScreen] SignalR disconnected')
      setIsConnected(false)
      setIsStreaming(false)
      isStreamingRef.current = false
    }

    const handleStreamStarted = (data: string) => {
      console.log('[LiveScreen] Stream started:', data)
      setIsStreaming(true)
      isStreamingRef.current = true
      setError(null)
    }

    // SignalR JSON protocol encodes byte[] as base64 strings
    const handleStreamData = (data: string | Uint8Array) => {
      if (!isStreamingRef.current || !jmuxerRef.current) {
        return
      }

      try {
        let bytes: Uint8Array
        if (typeof data === 'string') {
          const binary = atob(data)
          bytes = new Uint8Array(binary.length)
          for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i)
          }
        } else {
          bytes = data
        }
        jmuxerRef.current.feed({ video: bytes })
      } catch (err) {
        console.error('[LiveScreen] Error feeding chunk:', err)
      }
    }

    const handleStreamError = (msg: string) => {
      console.error('[LiveScreen] Stream error:', msg)
      setError(msg)
      setIsStreaming(false)
      isStreamingRef.current = false
    }

    const handleStreamEnded = () => {
      console.log('[LiveScreen] Stream ended')
      setIsStreaming(false)
      isStreamingRef.current = false
    }

    // Register event listeners
    conn.on('StreamStarted', handleStreamStarted)
    conn.on('ReceiveFrame', handleStreamData)
    conn.on('StreamError', handleStreamError)
    conn.on('StreamEnded', handleStreamEnded)
    conn.onclose(handleDisconnect)
    conn.onreconnecting(handleDisconnect)
    conn.onreconnected(handleConnect)

    // Connect and start stream
    startScreenConnection()
      .then(handleConnect)
      .catch((err) => {
        console.error('[LiveScreen] Connection failed:', err)
        setError(String(err))
      })

    // Cleanup on unmount or close
    return () => {
      conn.off('StreamStarted', handleStreamStarted)
      conn.off('ReceiveFrame', handleStreamData)
      conn.off('StreamError', handleStreamError)
      conn.off('StreamEnded', handleStreamEnded)
      conn.onclose(() => {})
      conn.onreconnecting(() => {})
      conn.onreconnected(() => {})

      // Stop stream
      conn.invoke('StopStream', deviceId).catch(() => {})

      // Cleanup JMuxer
      if (jmuxerRef.current) {
        try {
          jmuxerRef.current.destroy()
        } catch (e) {
          console.error('[LiveScreen] Error destroying JMuxer:', e)
        }
        jmuxerRef.current = null
      }
    }
  }, [isOpen, deviceId])

  // Initialize JMuxer when streaming starts
  useEffect(() => {
    if (!isStreaming || !videoRef.current) return

    console.log('[LiveScreen] Initializing JMuxer...')

    try {
      const jmuxer = new JMuxer({
        node: videoRef.current,
        mode: 'video',
        flushingTime: 0,
        clearBuffer: true,
        fps: 20,
        debug: false
      })

      jmuxerRef.current = jmuxer
      console.log('[LiveScreen] JMuxer initialized successfully')
    } catch (err) {
      console.error('[LiveScreen] Error initializing JMuxer:', err)
      setError('Failed to initialize video player')
    }

    return () => {
      // Cleanup JMuxer when streaming stops
      if (jmuxerRef.current) {
        try {
          jmuxerRef.current.destroy()
        } catch (e) {
          console.error('[LiveScreen] Error destroying JMuxer:', e)
        }
        jmuxerRef.current = null
      }
    }
  }, [isStreaming])

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={
        <div className="flex items-center space-x-3">
          <Monitor className="w-5 h-5 text-gray-700" />
          <span>Live Screen [{deviceName}]</span>
          {isStreaming && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-red-400">LIVE</span>
            </div>
          )}
        </div>
      }
    >
      <div className="space-y-4">
        {/* Loading State */}
        {!isStreaming && !error && (
          <div className="flex flex-col items-center justify-center py-16 space-y-4">
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
            <p className="text-gray-700 text-base">
              {isConnected ? 'Starting stream...' : 'Connecting...'}
            </p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="flex flex-col items-center justify-center py-16 space-y-4">
            <AlertCircle className="w-12 h-12 text-red-500" />
            <p className="text-gray-900 text-lg font-medium">Stream Error</p>
            <p className="text-gray-600">{error}</p>
            <button
              onClick={handleClose}
              className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        )}

        {/* Video Element */}
        {isStreaming && !error && (
          <div className="space-y-3">
            <div className="relative rounded-lg overflow-hidden shadow-lg bg-black">
              {/* Aspect ratio container for 16:9 */}
              <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="absolute top-0 left-0 w-full h-full object-contain"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </Modal>
  )
}

export default LiveScreenModal
