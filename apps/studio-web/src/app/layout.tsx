import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LumosReading Studio Web",
  description: "Minimal V2 studio shell consuming shared caregiver contracts.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
