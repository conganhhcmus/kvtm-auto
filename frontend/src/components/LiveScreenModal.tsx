import React, { useEffect, useRef, useState, useCallback } from 'react'
import { Monitor, AlertCircle, Loader2 } from 'lucide-react'
import { getSocket } from '@/lib/socket'
import type { Socket } from 'socket.io-client'
import Modal from './Modal'

// @ts-expect-error - JMuxer doesn't have TypeScript definitions
import JMuxer from 'jmuxer'

interface LiveScreenModalProps {
    isOpen: boolean
    onClose: () => void
    deviceId: string,
    deviceName: string,
}

const LiveScreenModal: React.FC<LiveScreenModalProps> = ({ isOpen, onClose, deviceId, deviceName }) => {
    const [isConnected, setIsConnected] = useState(false)
    const [isStreaming, setIsStreaming] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const socketRef = useRef<Socket | null>(null)
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
        if (socketRef.current?.connected) {
            socketRef.current.emit('stop_stream')
        }

        onClose()
    }, [onClose])

    useEffect(() => {
        if (!isOpen || !deviceId) return

        // Get Socket.IO instance
        const socket = getSocket()
        socketRef.current = socket

        const handleConnect = () => {
            console.log('[LiveScreen] Socket connected')
            setIsConnected(true)
            setError(null)

            // Start streaming
            socket.emit('start_stream', { device_id: deviceId })
        }

        const handleDisconnect = () => {
            console.log('[LiveScreen] Socket disconnected')
            setIsConnected(false)
            setIsStreaming(false)
            isStreamingRef.current = false
        }

        const handleStreamStarted = (data: { device_id: string }) => {
            console.log('[LiveScreen] Stream started:', data)
            setIsStreaming(true)
            isStreamingRef.current = true
            setError(null)
        }

        const handleStreamData = (data: { chunk: ArrayBuffer }) => {
            // Check if we should still process chunks
            if (!isStreamingRef.current || !jmuxerRef.current) {
                return
            }

            // Handle binary or base64 data
            try {
                const bytes: Uint8Array = new Uint8Array(data.chunk)

                // Feed H.264 data directly to JMuxer
                jmuxerRef.current.feed({
                    video: bytes
                })
            } catch (err) {
                console.error('[LiveScreen] Error feeding chunk:', err)
            }
        }

        const handleStreamError = (data: { error: string }) => {
            console.error('[LiveScreen] Stream error:', data.error)
            setError(data.error)
            setIsStreaming(false)
            isStreamingRef.current = false
        }

        const handleStreamEnded = () => {
            console.log('[LiveScreen] Stream ended')
            setIsStreaming(false)
            isStreamingRef.current = false
        }

        // Register event listeners
        socket.on('connect', handleConnect)
        socket.on('disconnect', handleDisconnect)
        socket.on('stream_started', handleStreamStarted)
        socket.on('stream_data', handleStreamData)
        socket.on('stream_error', handleStreamError)
        socket.on('stream_ended', handleStreamEnded)

        // If already connected, start stream
        if (socket.connected) {
            handleConnect()
        }

        // Cleanup on unmount or close
        return () => {
            socket.off('connect', handleConnect)
            socket.off('disconnect', handleDisconnect)
            socket.off('stream_started', handleStreamStarted)
            socket.off('stream_data', handleStreamData)
            socket.off('stream_error', handleStreamError)
            socket.off('stream_ended', handleStreamEnded)

            // Stop stream
            if (socket.connected) {
                socket.emit('stop_stream')
            }

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
            // Create JMuxer instance with buffering for smoother playback
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
                            {/* Aspect ratio container for 16:9 (1920x1080) */}
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
