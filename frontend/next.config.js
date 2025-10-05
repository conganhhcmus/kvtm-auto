/** @type {import('next').NextConfig} */
const nextConfig = {
  // API proxy configuration - rewrites /api requests to backend
  // This proxies frontend requests to the Flask backend
  // Frontend: http://localhost:3000/api/* -> Backend: http://localhost:3001/api/*
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001'

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },

  // Disable strict mode to match current behavior
  reactStrictMode: false,

  // Output configuration
  distDir: '.next',

  // Optimize for production
  poweredByHeader: false,
  compress: true,

  // Logging
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
}

module.exports = nextConfig
