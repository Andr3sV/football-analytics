"use client"

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Home, 
  Users, 
  ChevronLeft, 
  ChevronRight,
  Activity,
  BarChart3,
  Target,
  Globe,
  Zap,
  TrendingUp
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { PrimePlayersLogo } from './logo'

interface SidebarProps {
  className?: string
}

const navigation = [
  {
    name: 'Home',
    href: '/',
    icon: Home,
  },
  {
    name: 'Training Club and Players',
    href: '/players',
    icon: Users,
  },
  {
    name: 'Development Analysis',
    href: '/development',
    icon: Target,
  },
  {
    name: 'Geographic Analysis',
    href: '/geographic',
    icon: Globe,
  },
  {
    name: 'Performance Metrics',
    href: '/performance',
    icon: Zap,
  },
  {
    name: 'Predictive Analytics',
    href: '/predictive',
    icon: TrendingUp,
  },
]

export function Sidebar({ className }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <div className={cn(
      "relative flex h-screen flex-col border-r border-border bg-sidebar transition-all duration-300 ease-in-out",
      collapsed ? "w-16" : "w-64",
      className
    )}>
      {/* Header */}
      <div className="flex h-16 items-center border-b border-border px-4">
        <div className={cn(
          "flex items-center gap-3 overflow-hidden transition-all duration-300",
          collapsed && "opacity-0"
        )}>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg">
            <PrimePlayersLogo className="h-6 w-6" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-sidebar-foreground">
              Prime Players
            </span>
            <span className="text-xs text-muted-foreground">
              Football Analytics Center
            </span>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          className={cn(
            "ml-auto h-8 w-8 p-0 hover:bg-sidebar-accent",
            collapsed && "ml-0"
          )}
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-hidden px-3 py-4">
        <ul className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                    isActive
                      ? "bg-sidebar-primary text-sidebar-primary-foreground"
                      : "text-sidebar-foreground"
                  )}
                >
                  <item.icon className="h-4 w-4 flex-shrink-0" />
                  <span className={cn(
                    "truncate transition-all duration-300",
                    collapsed && "opacity-0 w-0"
                  )}>
                    {item.name}
                  </span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="border-t border-border p-4">
        <div className={cn(
          "flex items-center gap-3 overflow-hidden transition-all duration-300",
          collapsed && "opacity-0"
        )}>
          <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="text-xs font-medium text-primary">A</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-sidebar-foreground">
              Admin
            </span>
            <span className="text-xs text-muted-foreground">
              Analytics Dashboard
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
