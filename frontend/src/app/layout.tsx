import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "Crypto AI Research", description: "Crypto market research platform" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="vi"><body>{children}</body></html>;
}
