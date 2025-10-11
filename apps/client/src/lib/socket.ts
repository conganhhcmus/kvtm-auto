import { io, Socket } from 'socket.io-client'

// Socket.IO connection URL - use relative path for proxy
const SOCKET_URL = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'

let socket: Socket | null = null

/**
 * Get or create Socket.IO client instance
 * @returns Socket.IO client
 */
export const getSocket = (): Socket => {
  if (!socket) {
    socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    })

    socket.on('connect', () => {
      console.log('[Socket.IO] Connected:', socket?.id)
    })

    socket.on('disconnect', (reason) => {
      console.log('[Socket.IO] Disconnected:', reason)
    })

    socket.on('connect_error', (error) => {
      console.error('[Socket.IO] Connection error:', error)
    })
  }

  return socket
}

/**
 * Disconnect and cleanup socket
 */
export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

export default getSocket
