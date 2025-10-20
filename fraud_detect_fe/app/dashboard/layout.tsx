"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, CreditCard, BarChart3, Bell, User } from "lucide-react"
import { cn } from "@/lib/utils"

const menuItems = [
  {
    title: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Transactions",
    href: "/dashboard/transactions",
    icon: CreditCard,
  },
  {
    title: "Model Performance",
    href: "/dashboard/model-performance",
    icon: BarChart3,
  },
]

const userMenuItem = {
  title: "User Transaction",
  href: "/user",
  icon: User,
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-[#0a0e27]">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-white/10 bg-[#0f1632]">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b border-white/10 px-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500">
            <svg
              className="h-5 w-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <span className="text-lg font-semibold text-white">Rwanda AI Fraud</span>
        </div>

        {/* Navigation */}
        <nav className="space-y-1 p-4">
          <div className="mb-6">
            <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
              Dashboard
            </p>
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-cyan-500/10 text-cyan-400"
                      : "text-gray-400 hover:bg-white/5 hover:text-white"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.title}
                </Link>
              )
            })}
          </div>
          
          <div className="border-t border-white/10 pt-4">
            <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
              User Portal
            </p>
            <Link
              href={userMenuItem.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                pathname === userMenuItem.href
                  ? "bg-cyan-500/10 text-cyan-400"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
              )}
            >
              <User className="h-5 w-5" />
              {userMenuItem.title}
            </Link>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="pl-64">
        {/* Header */}
        <header className="sticky top-0 z-30 border-b border-white/10 bg-[#0f1632]/80 backdrop-blur">
          <div className="flex h-16 items-center justify-between px-8">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-white">
                AI-Powered Fraud Detection Dashboard
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <button className="relative rounded-lg p-2 text-gray-400 hover:bg-white/5 hover:text-white">
                <Bell className="h-5 w-5" />
                <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
              </button>
              <div className="flex items-center gap-3 rounded-lg bg-white/5 px-3 py-2">
                <div className="h-8 w-8 rounded-full bg-cyan-500 flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-4 w-4 rounded-sm overflow-hidden">
                    <svg viewBox="0 0 3 2" className="h-full w-full">
                      <rect width="3" height="2" fill="#20603D"/>
                      <rect width="3" height="1" y="1" fill="#FAD201"/>
                      <rect width="3" height="0.67" y="1.33" fill="#00A1DE"/>
                    </svg>
                  </span>
                  <span className="text-sm font-medium text-white">Iradukunda Ruth</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-8">{children}</main>
      </div>
    </div>
  )
}
