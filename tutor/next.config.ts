import type { NextConfig } from "next";

const basePath = process.env.NEXT_BASE_PATH || "";

const nextConfig: NextConfig = {
  serverExternalPackages: ["@copilotkit/runtime"],
  basePath,
  assetPrefix: basePath,
};

export default nextConfig;
