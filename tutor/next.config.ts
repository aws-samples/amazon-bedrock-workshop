import type { NextConfig } from "next";

const studioBasePath = process.env.NEXT_BASE_PATH || "";

const nextConfig: NextConfig = {
  serverExternalPackages: ["@copilotkit/runtime"],
  basePath: studioBasePath,
  assetPrefix: studioBasePath ? studioBasePath + "/" : "",
};

export default nextConfig;
