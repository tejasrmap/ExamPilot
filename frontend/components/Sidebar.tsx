"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  ScanLine, 
  BotMessageSquare, 
  BookOpenCheck, 
  FileText, 
  Library, 
  History, 
  BarChart3, 
  KeyRound, 
  Settings,
  Sparkles
} from "lucide-react";

const navItems = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Question Scanner", href: "/scanner", icon: ScanLine },
  { name: "AI Assistant", href: "/assistant", icon: BotMessageSquare },
  { name: "Practice Tests", href: "/practice", icon: BookOpenCheck },
  { name: "PDF Question Papers", href: "/pdf-papers", icon: FileText },
  { name: "Knowledge Library", href: "/library", icon: Library },
  { name: "Question History", href: "/history", icon: History },
  { name: "Analytics & Usage", href: "/analytics", icon: BarChart3 },
  { name: "API Providers", href: "/providers", icon: KeyRound },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-sidebar border-r border-cardBorder flex flex-col justify-between shrink-0 h-screen sticky top-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-cardBorder gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-base tracking-wide text-foreground flex items-center gap-1.5">
              ExamPilot <span className="text-xs px-1.5 py-0.5 rounded bg-primary/20 text-primary font-mono">2.0</span>
            </h1>
            <p className="text-[11px] text-muted font-medium">GT InnoX LLP</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary text-white shadow-md shadow-primary/25"
                    : "text-muted hover:text-foreground hover:bg-card"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-muted"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-cardBorder bg-[#0c111d]/60">
        <div className="text-xs text-muted">
          <div className="flex items-center justify-between font-semibold text-foreground mb-1">
            <span>Online SaaS</span>
            <span className="flex items-center gap-1.5 text-success">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
              Live API
            </span>
          </div>
          <p className="text-[11px] leading-tight text-muted/80">Understand Questions. Learn the Answers.</p>
        </div>
      </div>
    </aside>
  );
}

