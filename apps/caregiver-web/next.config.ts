import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@lumosreading/contracts"],
  turbopack: {
    root: path.join(__dirname, "../.."),
  },
};

export default nextConfig;
