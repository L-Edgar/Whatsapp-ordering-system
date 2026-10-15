// app/dashboard/page.tsx
"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";

export default function DashboardHome() {
  const [counts, setCounts] = useState({ products: 0, orders: 0, customers: 0 });

  useEffect(() => {
    Promise.all([api.get("/products/"), api.get("/orders/"), api.get("/customers/")]).then(([products, orders, customers]) => {
      const today = new Date().toDateString();
      const ordersToday = orders.data.filter(
        (o: Order) => new Date(o.created_at).toDateString() === today
      ).length;
      setCounts({
        products: products.data.length,
        orders: ordersToday,
        customers: customers.data.length,
      });
    });
  }, []);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <h1 className="text-xl font-semibold mb-4">Good afternoon 👋</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="border rounded p-4"><p className="text-2xl">{counts.orders}</p><p className="text-sm text-gray-500">Orders today</p></div>
        <div className="border rounded p-4"><p className="text-2xl">{counts.products}</p><p className="text-sm text-gray-500">Products</p></div>
        <div className="border rounded p-4"><p className="text-2xl">{counts.customers}</p><p className="text-sm text-gray-500">Customers</p></div>
      </div>
    </div>
  );
}