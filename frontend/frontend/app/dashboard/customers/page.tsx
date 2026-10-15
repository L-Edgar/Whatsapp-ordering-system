"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";

type Customer = { id: number; name: string; whatsapp_number: string; orders_count: number };

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/customers/")
      .then(({ data }) => setCustomers(data))
      .catch(() => setError("Couldn't load customers."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500">Loading customers…</p>;

  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Customers</h1>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      {customers.length === 0 ? (
        <p className="text-gray-500">Customers appear here automatically when they message your WhatsApp number.</p>
      ) : (
        <ul className="space-y-2">
          {customers.map((c) => (
            <li key={c.id} className="border rounded p-3 flex justify-between items-center gap-3">
              <div className="min-w-0">
                <p className="font-medium truncate">{c.name || "Unknown"}</p>
                <p className="text-sm text-gray-500">+{c.whatsapp_number}</p>
              </div>
              <span className="text-sm text-gray-500 whitespace-nowrap">
                {c.orders_count} {c.orders_count === 1 ? "order" : "orders"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}