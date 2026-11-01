import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { TopDock } from "@/components/TopDock";
import { BottomDock } from "@/components/BottomDock";
import { ClickSpark } from "@/components/ClickSpark";
import FluxLines from "@/components/FluxLines";

const inter = Inter({ subsets: ["latin"], variable: "--agri-font-body" });
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--agri-font-heading" });

export const metadata: Metadata = {
  title: "AgriConnect - Farm to Market Marketplace",
  description: "Connecting farmers and buyers for fresh produce",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${spaceGrotesk.variable} antialiased`} style={{ margin: 0, padding: 0, position: "relative" }}>
        <AuthProvider>
          <FluxLines
            colors={["#059669", "#10b981", "#065f46"]}
            glow={2}
            rimWidth={0.2}
            lineWidth={1}
            flowDirection="down"
            mouseInteraction
            clickSwirl
            speed={0.5}
            scale={1.6}
            turbulence={1}
            fluidity={0.1}
            sharpness={2.5}
            shimmer={1.5}
            mouseStrength={1}
            mouseRadius={0.35}
            intro
            lightMode
            style={{ position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none" }}
          />
          <ClickSpark>
            <TopDock />
            <BottomDock />
            <main className="agri-main">
              {children}
            </main>
          </ClickSpark>
        </AuthProvider>
      </body>
    </html>
  );
}
