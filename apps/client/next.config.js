/** @type {import('next').NextConfig} */
const nextConfig = {
  // Note: API and Socket.IO proxying is handled by the custom server (server.ts)
  // Next.js rewrites don't work with custom servers

  // Disable strict mode to match current behavior
  reactStrictMode: false,

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
