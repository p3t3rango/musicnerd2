/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'https://your-deployment-url.vercel.app/api/:path*'
          : 'http://localhost:8000/api/:path*',
      },
    ];
  },
}

module.exports = nextConfig 