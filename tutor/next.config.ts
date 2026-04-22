import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ["@copilotkit/runtime"],
  assetPrefix: process.env.NEXT_ASSET_PREFIX || "",
};

export default nextConfig;
