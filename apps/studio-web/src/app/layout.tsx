import type { Metadata } from "next";
import { StudioShell } from "@/components/studio-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "LumosReading Studio Web",
  description: "Phase 4 studio operations console for package review and release control.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <StudioShell>{children}</StudioShell>
      </body>
    </html>
  );
}
