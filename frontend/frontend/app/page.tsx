// app/page.tsx
"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const hasToken = typeof window !== "undefined" && localStorage.getItem("access");
    router.replace(hasToken ? "/dashboard" : "/login");
  }, []);

  return null;
}