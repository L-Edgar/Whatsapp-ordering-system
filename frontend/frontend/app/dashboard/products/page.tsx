// app/dashboard/products/page.tsx
"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";

type Product = {
  id: number; name: string; price: string; is_available: boolean; category: number | null;
};

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<{id: number; name: string}[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", price: "", category: "", unit: "kg", stock_quantity: "0" });

  const load = () => api.get("/products/").then(({ data }) => setProducts(data));

  useEffect(() => {
    load();
    api.get("/categories/").then(({ data }) => setCategories(data));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/products/", { ...form, category: form.category || null });
    setForm({ name: "", price: "", category: "", unit: "kg", stock_quantity: "0" });
    setShowForm(false);
    load();
  };

  return (
    // app/dashboard/products/page.tsx — replace the closing <table> block with this
<div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-4">
  {/* mobile: cards */}
  <div className="space-y-2 md:hidden">
    {products.map((p) => (
      <div key={p.id} className="border rounded p-3 flex justify-between items-center">
        <div>
          <p className="font-medium">{p.name}</p>
          <p className="text-sm text-gray-500">UGX {p.price}</p>
        </div>
        <span className={`text-xs px-2 py-1 rounded ${p.is_available ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"}`}>
          {p.is_available ? "Available" : "Out of stock"}
        </span>
      </div>
    ))}
  </div>

  {/* desktop: table */}
  <table className="w-full text-left hidden md:table">
    <thead><tr className="border-b"><th>Name</th><th>Price</th><th>Status</th></tr></thead>
    <tbody>
      {products.map((p) => (
        <tr key={p.id} className="border-b">
          <td className="py-2">{p.name}</td>
          <td>UGX {p.price}</td>
          <td>{p.is_available ? "Available" : "Out of stock"}</td>
        </tr>
      ))}
    </tbody>
  </table>
</div>
  );
}