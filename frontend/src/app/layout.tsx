import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'KVTM Auto - Android Device Automation',
    description: 'Automate Android devices with ADB integration',
    icons: {
        icon: 'https://play-lh.googleusercontent.com/Yib_ehd-Akt7XQYgdbzYCLUt_MQ2RBJoBkIGggXrtHJtnYlJ-WvuszoniVyLBpZ2fQ',
    },
}

export const viewport: Viewport = {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    )
}
