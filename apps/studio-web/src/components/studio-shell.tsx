"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { studioNavItems } from "@/lib/navigation";

export function StudioShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const activeItem =
    studioNavItems.find((item) =>
      item.href === "/" ? pathname === "/" : pathname.startsWith(item.href),
    ) ?? studioNavItems[0];

  return (
    <div className="studio-frame">
      <aside className="studio-rail">
        <div className="studio-rail__panel">
          <div>
            <div className="brand-kicker">V2 studio ops</div>
            <h1 className="brand-title">LumosReading</h1>
            <p className="brand-copy">
              Release-aware console for draft review, publish control, recall handling, and audit traceability.
            </p>
          </div>

          <div className="badge-row">
            <span className="badge badge--accent">phase 6</span>
            <span className="badge badge--neutral">contracts first</span>
          </div>

          <nav className="nav-list" aria-label="Studio primary">
            {studioNavItems.map((item) => {
              const isActive =
                item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
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
            Runtime packages must stay versioned, reviewable, and recallable. Studio should not rebuild release logic
            inside page components.
          </div>
        </div>
      </aside>

      <div className="studio-main">
        <header className="studio-topbar">
          <div>
            <h2 className="studio-topbar__title">{activeItem.label}</h2>
            <p className="studio-topbar__copy">{activeItem.description}</p>
          </div>
          <div className="studio-topbar__status">
            <span>Active route</span>
            <span className="mono">{pathname}</span>
          </div>
        </header>

        {children}
      </div>
    </div>
  );
}
