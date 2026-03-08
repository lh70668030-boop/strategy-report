/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // 关键：强制所有页面为静态生成
  revalidate: 60, // 缓存 60 秒，可选
};

module.exports = nextConfig;