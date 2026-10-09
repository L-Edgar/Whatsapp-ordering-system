// app/register/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function Register() {
  const router = useRouter();
  const [form, setForm] = useState({
    business_name: "", owner_name: "", email: "", phone: "", password: "",
  });
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/register/", form);
      // registration doesn't log in automatically — send them to login
      router.push("/login");
    } catch (err: any) {
      setError(err.response?.data?.email?.[0] || "Registration failed. Check your details.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-sm mx-auto mt-16 space-y-4">
      <h1 className="text-xl font-semibold">Create your shop</h1>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {["business_name", "owner_name", "email", "phone"].map((field) => (
        <input
          key={field}
          placeholder={field.replace("_", " ")}
          className="w-full border rounded p-2"
          value={(form as any)[field]}
          onChange={(e) => setForm({ ...form, [field]: e.target.value })}
        />
      ))}
      <input
        type="password"
        placeholder="password"
        className="w-full border rounded p-2"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
      />
      <button className="w-full bg-black text-white rounded p-2">Create Business</button>
    </form>
  );
}