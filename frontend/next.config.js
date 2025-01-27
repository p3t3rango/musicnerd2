/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'https://musicnerd2.vercel.app/api/:path*'  // Replace with your actual Vercel URL
          : 'http://localhost:8000/api/:path*',
      },
    ];
  },
}

module.exports = nextConfig 