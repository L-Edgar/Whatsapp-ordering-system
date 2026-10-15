// app/dashboard/orders/page.tsx
"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";

type OrderItem = {
    id: number;
    product_name: string;
    quantity: number;
    unit_price: string;
    subtotal: string;
};

type Order = {
    id: number;
    order_number: string;
    status: string;
    customer_name: string;
    customer_phone: string;
    subtotal: string;
    delivery_fee: string;
    total: string;
    delivery_address: string;
    items: OrderItem[];
    created_at: string;
};

const STATUS_OPTIONS = ["pending", "confirmed", "ready", "completed"];

const STATUS_STYLES: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-800",
    confirmed: "bg-blue-100 text-blue-800",
    ready: "bg-purple-100 text-purple-800",
    completed: "bg-green-100 text-green-800",
};

export default function Orders() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [expandedId, setExpandedId] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [updatingId, setUpdatingId] = useState<number | null>(null);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState<{ type: "ok" | "warn"; text: string } | null>(null);

    const load = (silent = false) => {
        if (!silent) setLoading(true);
        api.get("/orders/")
            .then(({ data }) => setOrders(data))
            .catch((err) => {
                if (!silent) setError(`Couldn't load orders (${err.response?.status || "network error"}).`);
            })
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        load();
        const timer = setInterval(() => load(true), 15000);
        return () => clearInterval(timer);
    }, []);

    const handleStatusChange = async (orderId: number, newStatus: string) => {
        setUpdatingId(orderId);
        setNotice(null);
        try {
            const { data } = await api.patch(`/orders/${orderId}/update_status/`, { status: newStatus });
            setOrders((prev) => prev.map((o) => (o.id === orderId ? { ...o, status: data.status } : o)));

            if (data.customer_notified) {
                setNotice({ type: "ok", text: `${data.order_number}: customer notified on WhatsApp.` });
            } else if (newStatus !== "pending") {
                setNotice({
                    type: "warn",
                    text: `${data.order_number} updated, but the WhatsApp message could not be delivered.`,
                });
            }
        } catch {
            alert("Couldn't update order status. Try again.");
        } finally {
            setUpdatingId(null);
        }
    };

    if (loading) return <p className="text-gray-500">Loading orders…</p>;

    return (
        <div>
            <h1 className="text-xl font-semibold mb-4">Orders</h1>
            {notice && (
                <p className={`mb-4 text-sm rounded px-3 py-2 ${notice.type === "ok" ? "bg-green-50 text-green-800" : "bg-yellow-50 text-yellow-800"
                    }`}>
                    {notice.text}
                </p>
            )}
            {orders.length === 0 ? (
                <p className="text-gray-500">
                    No orders yet. They'll appear here once customers start checking out.
                </p>
            ) : (
                <div className="space-y-3">
                    {orders.map((order) => (
                        <div key={order.id} className="border rounded">

                            <div
                                className="flex flex-col gap-2 sm:flex-row sm:justify-between sm:items-center p-4 cursor-pointer"
                                onClick={() => setExpandedId(expandedId === order.id ? null : order.id)}
                            >
                                <div>
                                    <p className="font-medium">{order.order_number}</p>
                                    <p className="text-sm text-gray-500">
                                        {order.customer_name || "Unknown"} · {order.customer_phone}
                                    </p>
                                </div>
                                <div className="flex items-center justify-between sm:justify-end gap-3">
                                    <span className="text-xs sm:text-sm text-gray-500">
                                        {new Date(order.created_at).toLocaleString()}
                                    </span>
                                    <span className="font-medium">UGX {Number(order.total).toLocaleString()}</span>
                                    <select
                                        value={order.status}
                                        disabled={updatingId === order.id}
                                        onClick={(e) => e.stopPropagation()}
                                        onChange={(e) => handleStatusChange(order.id, e.target.value)}
                                        className={`text-xs rounded px-2 py-1 border-0 font-medium ${STATUS_STYLES[order.status]}`}
                                    >
                                        {STATUS_OPTIONS.map((s) => (
                                            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {expandedId === order.id && (
                                <div className="border-t p-4 bg-gray-50 text-sm">
                                    <p className="text-gray-500 mb-2">Deliver to: {order.delivery_address}</p>
                                    <table className="w-full">
                                        <tbody>
                                            {order.items.map((item) => (
                                                <tr key={item.id}>
                                                    <td className="py-1">{item.product_name}</td>
                                                    <td className="py-1 text-gray-500">× {item.quantity}</td>
                                                    <td className="py-1 text-right">UGX {Number(item.subtotal).toLocaleString()}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                        <tfoot>
                                            <tr className="border-t">
                                                <td colSpan={2} className="pt-2 text-gray-500">Subtotal</td>
                                                <td className="pt-2 text-right">UGX {Number(order.subtotal).toLocaleString()}</td>
                                            </tr>
                                            <tr>
                                                <td colSpan={2} className="text-gray-500">Delivery</td>
                                                <td className="text-right">UGX {Number(order.delivery_fee).toLocaleString()}</td>
                                            </tr>
                                            <tr className="font-medium">
                                                <td colSpan={2} className="pt-1">Total</td>
                                                <td className="pt-1 text-right">UGX {Number(order.total).toLocaleString()}</td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}