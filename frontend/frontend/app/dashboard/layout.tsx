// app/dashboard/layout.tsx
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import api from "@/lib/api";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/products", label: "Products" },
  { href: "/dashboard/categories", label: "Categories" },
  { href: "/dashboard/orders", label: "Orders" },
  { href: "/dashboard/customers", label: "Customers" },
  { href: "/dashboard/whatsapp", label: "WhatsApp" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [businessName, setBusinessName] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("access")) {
      router.push("/login");
      return;
    }
    api.get("/businesses/").then(({ data }) => {
      if (data.length) setBusinessName(data[0].name);
    });
  }, []);

  // close the drawer automatically whenever the route changes
  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  return (
    <div className="min-h-screen md:flex">
      {/* mobile top bar */}
      <div className="flex items-center justify-between p-4 border-b md:hidden">
        <span className="font-semibold">{businessName || "…"}</span>
        <button
          onClick={() => setSidebarOpen(true)}
          aria-label="Open menu"
          className="p-2 -mr-2"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18M3 12h18M3 18h18" />
          </svg>
        </button>
      </div>

      {/* backdrop, mobile only, shown while drawer is open */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* sidebar: static column on desktop, slide-in drawer on mobile */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 bg-white border-r p-4 flex flex-col justify-between
          transition-transform duration-200 ease-out
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          md:static md:translate-x-0 md:w-56 md:z-auto
        `}
      >
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-semibold">{businessName || "…"}</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              aria-label="Close menu"
              className="p-1 md:hidden"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>
          </div>
          <nav className="space-y-1">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`block px-3 py-2 rounded text-sm ${
                  pathname === item.href ? "bg-gray-200 font-medium" : "hover:bg-gray-100"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <button
          onClick={() => {
            localStorage.clear();
            router.push("/login");
          }}
          className="text-left px-3 py-2 text-red-600 text-sm"
        >
          Log out
        </button>
      </aside>

      <main className="flex-1 p-4 md:p-8 min-w-0">{children}</main>
    </div>
  );
}