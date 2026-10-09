// app/login/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { data } = await api.post("/token/", { email, password });
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-sm mx-auto mt-8 sm:mt-16 space-y-4 px-4">
      <h1 className="text-xl font-semibold">Log in</h1>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <input placeholder="email" className="w-full border rounded p-2" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input type="password" placeholder="password" className="w-full border rounded p-2" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button className="w-full bg-black text-white rounded p-2">Log In</button>
    </form>
  );
}