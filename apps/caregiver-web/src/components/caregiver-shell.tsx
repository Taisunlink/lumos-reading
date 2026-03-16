"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { caregiverNavItems } from "@/lib/navigation";

export function CaregiverShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const activeItem = caregiverNavItems.find((item) =>
    item.href === "/" ? pathname === "/" : pathname.startsWith(item.href),
  );

  return (
    <div className="shell">
      <aside className="shell__sidebar">
        <div className="sidebar-panel">
          <div>
            <div className="brand-kicker">V2 caregiver surface</div>
            <h1 className="brand-title">LumosReading</h1>
            <p className="brand-copy">
              Contracts-first dashboard for household planning, progress, and distribution-aware content
              operations.
            </p>
          </div>

          <div className="badge-row">
            <span className="badge is-warm">apps/web is legacy</span>
            <span className="badge is-green">contracts first</span>
          </div>

          <nav className="nav-list" aria-label="Primary">
            {caregiverNavItems.map((item) => {
              const isActive = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`nav-link${isActive ? " is-active" : ""}`}
                >
                  <span className="nav-link__label">{item.label}</span>
                  <span className="nav-link__meta">{item.description}</span>
                </Link>
              );
            })}
          </nav>

          <div className="sidebar-note">
            Start every session from `docs/v2/01`, `docs/v2/02`, then `packages/contracts/schemas`.
          </div>
        </div>
      </aside>

      <div className="shell__content">
        <header className="topbar">
          <div>
            <h2 className="topbar__title">{activeItem?.label ?? "Caregiver"}</h2>
            <p className="topbar__copy">{activeItem?.description ?? "V2 caregiver workspace"}</p>
          </div>
          <div className="topbar__status">
            <span>Active route</span>
            <span className="mono">{pathname}</span>
          </div>
        </header>

        {children}
      </div>
    </div>
  );
}
