"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getToken, removeToken, fetchWithAuth } from "@/lib/auth";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

const loadRazorpayScript = () => {
    return new Promise((resolve) => {
        const script = document.createElement("script");
        script.src = "https://checkout.razorpay.com/v1/checkout.js";
        script.onload = () => resolve(true);
        script.onerror = () => resolve(false);
        document.body.appendChild(script);
    });
};

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [hotels, setHotels] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<{revenue: any[], occupancy: any[]}>({revenue: [], occupancy: []});
  const router = useRouter();

  const [notifying, setNotifying] = useState<string | null>(null);
  const [analyzingSentiment, setAnalyzingSentiment] = useState<string | null>(null);
  const [sentimentResults, setSentimentResults] = useState<Record<string, any>>({});

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    const fetchData = async () => {
      try {
        const [hotelsRes, analyticsRes] = await Promise.all([
          fetchWithAuth(`${API_URL}/api/search-hotels`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ city_code: "NYC", check_in: "2026-05-01", check_out: "2026-05-05" }),
          }),
          fetchWithAuth(`${API_URL}/api/analytics/dashboard`)
        ]);

        if (hotelsRes.ok) {
          const data = await hotelsRes.json();
          setHotels(data.rates || []);
        } else {
          setHotels([]);
        }

        if (analyticsRes.ok) {
          const aData = await analyticsRes.json();
          setAnalytics(aData);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router, API_URL]);

  const handleLogout = () => {
    removeToken();
    router.push("/login");
  };

  const handleBookNow = async (hotel: any) => {
    setNotifying(hotel.hotel_name);
    try {
      // 1. Fetch Order ID from backend
      const res = await fetchWithAuth(`${API_URL}/api/payments/create-order`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hotel_name: hotel.hotel_name,
          amount_inr: Math.round(hotel.price_usd * 83)
        })
      });
      
      const orderData = await res.json();
      
      // 2. Load Razorpay script if not already present
      const resScript = await loadRazorpayScript();
      if (!resScript) {
        alert("Razorpay SDK failed to load. Are you online?");
        return;
      }
      
      // 3. Open Checkout
      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "rzp_test_mock_key",
        amount: orderData.amount_paise,
        currency: orderData.currency,
        name: "Aether Global",
        description: `Booking for ${hotel.hotel_name}`,
        order_id: orderData.order_id,
        handler: async function (response: any) {
             // 4. Verify & Auto-Notify Dual-Channel
             const verifyRes = await fetchWithAuth(`${API_URL}/api/payments/verify`, {
                 method: "POST",
                 headers: { "Content-Type": "application/json" },
                 body: JSON.stringify({
                     razorpay_order_id: response.razorpay_order_id,
                     razorpay_payment_id: response.razorpay_payment_id,
                     razorpay_signature: response.razorpay_signature,
                     hotel_name: hotel.hotel_name,
                     amount_inr: Math.round(hotel.price_usd * 83),
                     user_phone: "+919027276598" 
                 })
             });
             if (verifyRes.ok) {
                 alert(`💳 Payment Verified! Check WhatsApp and your Email for confirmations.`);
             } else {
                 alert("Payment Verification Failed by Server");
             }
        },
        prefill: {
            name: "Akansh Saxena",
            email: "admin@aether.com",
            contact: "9027276598"
        },
        theme: {
            color: "#10B981"
        }
      };
      
      const rzp1 = new (window as any).Razorpay(options);
      rzp1.open();

    } catch(e) {
      console.error(e);
      alert("Failed to initialize Razorpay gateway.");
    } finally {
      setNotifying(null);
    }
  };

  const handleDeepScan = async (hotelName: string) => {
    setAnalyzingSentiment(hotelName);
    try {
      const res = await fetchWithAuth(`${API_URL}/api/analyze-reviews/${encodeURIComponent(hotelName)}`);
      if (res.ok) {
        const data = await res.json();
        setSentimentResults(prev => ({...prev, [hotelName]: data}));
      } else {
        alert("Deep Scan failed. Model might be loading.");
      }
    } catch (e) {
      console.error("Deep Scan Error:", e);
    } finally {
      setAnalyzingSentiment(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <div className="animate-pulse">Loading Aether Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8 border-b border-gray-800 pb-6">
          <h1 className="text-3xl font-bold tracking-tight">
            Aether <span className="text-blue-500">Dashboard</span>
          </h1>
          <button 
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors text-sm font-medium shadow-lg"
          >
            Logout
          </button>
        </header>

        {/* Analytics Section */}
        <section className="mb-12 grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
             <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-widest mb-4">Total Revenue by City ($)</h3>
             <div className="h-64 w-full">
               <ResponsiveContainer width="100%" height="100%">
                 <BarChart data={analytics.revenue}>
                   <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                   <XAxis dataKey="name" stroke="#9CA3AF" />
                   <YAxis stroke="#9CA3AF" tickFormatter={(value) => `$${value/1000}k`} />
                   <Tooltip cursor={{fill: '#1F2937'}} contentStyle={{ backgroundColor: '#111827', borderColor: '#374151' }} />
                   <Legend />
                   <Bar dataKey="revenue" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Revenue" />
                 </BarChart>
               </ResponsiveContainer>
             </div>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-xl">
             <h3 className="text-gray-400 text-sm font-semibold uppercase tracking-widest mb-4">Occupancy Rates by City (%)</h3>
             <div className="h-64 w-full">
               <ResponsiveContainer width="100%" height="100%">
                 <BarChart data={analytics.occupancy} layout="vertical">
                   <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                   <XAxis type="number" stroke="#9CA3AF" domain={[0, 100]} />
                   <YAxis dataKey="name" type="category" stroke="#9CA3AF" width={80} />
                   <Tooltip cursor={{fill: '#1F2937'}} contentStyle={{ backgroundColor: '#111827', borderColor: '#374151' }} />
                   <Legend />
                   <Bar dataKey="rate" fill="#10B981" radius={[0, 4, 4, 0]} name="Occupancy %" />
                 </BarChart>
               </ResponsiveContainer>
             </div>
          </div>
        </section>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Main Hotel List Area */}
          <section className="flex-1">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              Live Rates (NYC)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {hotels.map((hotel, idx) => (
                <div key={idx} className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-500 transition-all shadow-md group">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="font-medium text-lg text-blue-400 group-hover:text-blue-300 transition">{hotel.hotel_name}</h3>
                    <span className="bg-gray-900 px-2 py-1 rounded-full text-xs text-yellow-500 font-bold border border-gray-700 flex items-center gap-1">
                      ★ {hotel.rating}
                    </span>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm text-gray-400 mb-1 font-medium tracking-wide uppercase">Platform: {hotel.platform}</p>
                    <p className="text-3xl font-extrabold text-white">${hotel.price_usd}</p>
                  </div>

                  {/* Sentiment Results Panel */}
                  {sentimentResults[hotel.hotel_name] && (
                    <div className="mt-4 p-3 bg-gray-900 border border-purple-500/30 rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                         <span className="text-xs font-bold uppercase tracking-widest text-purple-400">Deep Scan Analysis</span>
                         <span className="text-sm font-black text-white">{sentimentResults[hotel.hotel_name].true_sentiment_score}/100</span>
                      </div>
                      <p className="text-xs text-gray-400 mb-2">Based on {sentimentResults[hotel.hotel_name].total_analyzed} Google Reviews</p>
                      
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        {Object.entries(sentimentResults[hotel.hotel_name].category_breakdown || {}).map(([cat, scores]: any, i) => {
                          if (scores.total === 0) return null;
                          const pct = Math.round((scores.positive / scores.total) * 100);
                          return (
                            <div key={i} className="flex justify-between bg-gray-800 p-1.5 rounded border border-gray-700">
                              <span className="text-gray-300">{cat}</span>
                              <span className={pct > 70 ? "text-emerald-400 font-bold" : pct > 40 ? "text-amber-400 font-bold" : "text-red-400 font-bold"}>{pct}%</span>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  <div className="mt-6 flex flex-col sm:flex-row gap-3">
                    <button 
                      onClick={() => handleDeepScan(hotel.hotel_name)}
                      disabled={analyzingSentiment === hotel.hotel_name}
                      className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 border border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-semibold transition-all text-purple-300 hover:text-purple-200"
                    >
                      {analyzingSentiment === hotel.hotel_name ? "Scanning Model..." : "NLP Deep Scan"}
                    </button>
                    
                    <button 
                      onClick={() => handleBookNow(hotel)}
                      disabled={notifying === hotel.hotel_name}
                      className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg text-white text-sm font-semibold transition-all shadow-lg hover:shadow-blue-500/25"
                    >
                      {notifying === hotel.hotel_name ? "Processing Gateway..." : "Secure Checkout"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
            {hotels.length === 0 && (
               <div className="w-full h-48 flex items-center justify-center border-2 border-dashed border-gray-700 rounded-xl text-gray-500 mt-6">
                 No inventory located or failed to authenticate.
               </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
