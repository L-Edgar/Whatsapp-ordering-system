// app/dashboard/categories/page.tsx
"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";

type Category = { id: number; name: string; description: string };

export default function Categories() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ name: "", description: "" });

    const load = () => api.get("/categories/").then(({ data }) => setCategories(data));

    useEffect(() => { load(); }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await api.post("/categories/", form);
        setForm({ name: "", description: "" });
        setShowForm(false);
        load();
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-xl font-semibold">Categories</h1>
                <button onClick={() => setShowForm(!showForm)} className="bg-black text-white rounded px-3 py-1">
                    + Add Category
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleSubmit} className="mb-6 space-y-2 max-w-sm border p-4 rounded">
                    <input placeholder="Category name" className="w-full border rounded p-2"
                        value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                    <input placeholder="Description (optional)" className="w-full border rounded p-2"
                        value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
                    <button className="bg-black text-white rounded px-3 py-1">Save Category</button>
                </form>
            )}


            <ul className="space-y-2">
                {categories.map((c) => (
                    <li key={c.id} className="border rounded px-3 py-2 sm:border-0 sm:border-b sm:rounded-none sm:px-0">
                        {c.name}
                    </li>
                ))}
            </ul>
        </div>
    );
}