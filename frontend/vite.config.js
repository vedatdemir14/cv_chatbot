import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // For GitHub Pages project sites, set VITE_BASE="/<repo-name>/" at build time.
  base: process.env.VITE_BASE || "/",
});
