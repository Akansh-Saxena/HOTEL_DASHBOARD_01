"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken, removeToken, fetchWithAuth } from "@/lib/auth";

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [hotels, setHotels] = useState<any[]>([]);
  const router = useRouter();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    // Example of calling a protected endpoint
    const fetchHotels = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        const res = await fetchWithAuth(`${API_URL}/api/search-hotels`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            city_code: "NYC",
            check_in: "2026-05-01",
            check_out: "2026-05-05",
          }),
        });

        if (res.ok) {
          const data = await res.json();
          setHotels(data.rates || []);
        } else {
          // If auth failed, fetchWithAuth redirects to /login automatically
          setHotels([]);
        }
      } catch (err) {
        console.error("Failed to fetch hotels", err);
      } finally {
        setLoading(false);
      }
    };

    fetchHotels();
  }, [router]);

  const handleLogout = () => {
    removeToken();
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <div className="animate-pulse">Loading Aether Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-12 border-b border-gray-800 pb-6">
          <h1 className="text-3xl font-bold">
            Aether <span className="text-blue-500">Dashboard</span>
          </h1>
          <button 
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors text-sm font-medium"
          >
            Logout
          </button>
        </header>

        <section>
          <h2 className="text-xl font-semibold mb-6 text-gray-300">Live Hotel Rates (NYC)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {hotels.map((hotel, idx) => (
              <div key={idx} className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-500 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-medium text-lg text-blue-400">{hotel.hotel_name}</h3>
                  <span className="bg-gray-900 px-2 py-1 rounded text-xs text-yellow-500 font-bold border border-gray-700">
                    ★ {hotel.rating}
                  </span>
                </div>
                <div className="mt-4">
                  <p className="text-sm text-gray-400 mb-1">Platform: {hotel.platform}</p>
                  <p className="text-2xl font-bold">${hotel.price_usd}</p>
                </div>
                <button className="mt-6 w-full py-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm font-semibold transition-colors">
                  Book Now
                </button>
              </div>
            ))}
          </div>
          {hotels.length === 0 && (
            <div className="text-gray-500 py-12 text-center border border-dashed border-gray-700 rounded-xl">
              No hotels available or Failed to load.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
