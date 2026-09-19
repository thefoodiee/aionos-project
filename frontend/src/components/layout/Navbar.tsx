// components/layout/Navbar.tsx
"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Layers, Users, SlidersHorizontal, Plus, Database, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { employeeService } from "@/services/employeeService";

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isSeeding, setIsSeeding] = useState(false);

  const handleLoadTestData = async () => {
    try {
      setIsSeeding(true);
      await employeeService.seedTestData();
      router.push("/team-builder?demo=true");
    } catch (err) {
      console.error("Failed to load test data:", err);
      // Still navigate to demo page even if already seeded
      router.push("/team-builder?demo=true");
    } finally {
      setIsSeeding(false);
    }
  };

  const navItems = [
    { label: "Dashboard", href: "/", icon: Layers },
    { label: "Engineering Roster", href: "/employees", icon: Users },
    { label: "Staffing Planner", href: "/team-builder", icon: SlidersHorizontal },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-gray-900 text-white font-semibold text-xs tracking-tight">
              SB
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold tracking-tight text-gray-900 group-hover:text-gray-700 transition-colors">
                StaffBuilder
              </span>
              <span className="text-[10px] text-gray-400 -mt-0.5 font-normal tracking-normal">
                Resource Allocation System
              </span>
            </div>
          </Link>

          {/* Nav items */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                    isActive
                      ? "bg-gray-100 text-gray-900"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  )}
                >
                  <Icon className="h-3.5 w-3.5 text-gray-500" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right tools */}
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={handleLoadTestData}
            disabled={isSeeding}
            className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors shadow-2xs disabled:opacity-60 disabled:cursor-not-allowed"
            title="Upload candidate seed data and open prefilled project description"
          >
            {isSeeding ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin text-gray-600" />
                <span>Loading Data...</span>
              </>
            ) : (
              <>
                <Database className="h-3.5 w-3.5 text-gray-500" />
                <span>Load Test Data</span>
              </>
            )}
          </button>

          <Link
            href="/team-builder"
            className="inline-flex items-center gap-1.5 rounded-md bg-gray-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-gray-800 transition-colors shadow-xs"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>New Allocation</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
