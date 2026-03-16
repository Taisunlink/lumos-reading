import type { Metadata } from "next";
import { CaregiverShell } from "@/components/caregiver-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "LumosReading Caregiver Web",
  description: "V2 caregiver surface for LumosReading.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <CaregiverShell>{children}</CaregiverShell>
      </body>
    </html>
  );
}
