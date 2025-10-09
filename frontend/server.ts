import express, {Request} from 'express'
import next from 'next'
import { createProxyMiddleware } from 'http-proxy-middleware'
import { Socket } from 'net'

const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const handle = app.getRequestHandler()
const port = parseInt(process.env.PORT || '3000', 10)
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001'

app.prepare().then(() => {
  const server = express()

  // Create proxy middleware instances for reuse
  const apiProxy = createProxyMiddleware({
    target: backendUrl,
    changeOrigin: true,
    ws: false, // Don't proxy WebSocket on /api
    onProxyReq: (_proxyReq, req) => {
      console.log(`[API Proxy] ${req.method} ${req.url} -> ${backendUrl}${req.url}`)
    },
    onError: (err, _req, res) => {
      console.error('[API Proxy Error]', err)
      // res is already typed as express.Response by http-proxy-middleware
      res.status(500).json({ error: 'Proxy error', details: err.message })
    },
  })

  const socketIOProxy = createProxyMiddleware({
    target: backendUrl,
    changeOrigin: true,
    ws: true, // Enable WebSocket proxy
    onProxyReq: (_proxyReq, req) => {
      console.log(`[Socket.IO Proxy] ${req.method} ${req.url} -> ${backendUrl}${req.url}`)
    },
    onError: (err, _req, res) => {
      console.error('[Socket.IO Proxy Error]', err)
      // res is already typed as express.Response by http-proxy-middleware
      res.status(500).json({ error: 'WebSocket proxy error', details: err.message })
    },
  })

  // Apply proxy middleware
  server.use('/api', apiProxy)
  server.use('/socket.io', socketIOProxy)

  // Handle all other requests with Next.js
  server.all('*', (req, res) => {
    return handle(req, res)
  })

  // Start server and listen for WebSocket upgrades
  const httpServer = server.listen(port, () => {
    console.log(`> Ready on http://localhost:${port}`)
    console.log(`> Proxying /api/* to ${backendUrl}/api/*`)
    console.log(`> Proxying /socket.io/* to ${backendUrl}/socket.io/* (WebSocket enabled)`)
  })

  // Handle WebSocket upgrade for Socket.IO
  httpServer.on('upgrade', (req, socket, head) => {
    console.log(`[WebSocket Upgrade] ${req.url}`)
    if (req.url?.startsWith('/socket.io')) {
      // Use the socketIOProxy's upgrade method if available
      if (socketIOProxy.upgrade) {
        // Cast req and socket to proper types for http-proxy-middleware
        socketIOProxy.upgrade(req as Request, socket as Socket, head)
      } else {
        console.error('[WebSocket Upgrade] socketIOProxy.upgrade is not available')
        socket.destroy()
      }
    } else {
      socket.destroy()
    }
  })
})
