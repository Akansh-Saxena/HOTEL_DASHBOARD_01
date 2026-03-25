"use client";

import { useEffect, useState } from "react";
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
  const [searchCity, setSearchCity] = useState("NYC");
  const [isSearching, setIsSearching] = useState(false);
  
  const [hotels, setHotels] = useState<any[]>([]);
  const [food, setFood] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<{revenue: any[], occupancy: any[]}>({revenue: [], occupancy: []});
  const router = useRouter();

  const [notifying, setNotifying] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [aadharNo, setAadharNo] = useState("");
  const [kycError, setKycError] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const fetchDashboardData = async (city: string) => {
    setIsSearching(true);
    try {
      const [scanRes, analyticsRes] = await Promise.all([
        fetchWithAuth(`${API_URL}/api/v1/akansh/scan/all?city=${city}`),
        fetchWithAuth(`${API_URL}/api/v1/akansh/analytics/dashboard`)
      ]);

      if (scanRes.ok) {
        const data = await scanRes.json();
        setHotels(data.results?.hotels || []);
        setFood(data.results?.food_compare || []);
      } else {
        setHotels([]);
        setFood([]);
      }

      if (analyticsRes.ok) {
        const aData = await analyticsRes.json();
        setAnalytics(aData);
      }
    } catch (err) {
      console.error("Failed to fetch dashboard data", err);
    } finally {
      setIsSearching(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }
    fetchDashboardData(searchCity);
  }, [router, API_URL]);

  const handleLogout = () => {
    removeToken();
    router.push("/login");
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDashboardData(searchCity);
  };

  const handleBookNow = async () => {
    if (!selectedItem) return;
    if (aadharNo.length !== 12) {
      setKycError("Aadhar number must be exactly 12 digits.");
      return;
    }
    setKycError("");
    
    const isHotel = !!selectedItem.hotel_name;
    const itemName = isHotel ? selectedItem.hotel_name : selectedItem.item;
    const price = isHotel 
         ? selectedItem.price_usd * 83 
         : Math.min(selectedItem.zomato || 9999, selectedItem.swiggy || 9999, selectedItem.zepto || 9999, selectedItem.blinkit || 9999);
         
    setNotifying(itemName);
    
    try {
      const res = await fetchWithAuth(`${API_URL}/api/v1/akansh/pay/secure`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hotel_name: itemName,
          amount_inr: Math.round(price),
          aadhar_no: aadharNo
        })
      });
      
      if (!res.ok) {
        const err = await res.json();
        alert(`Checkout Failed: ${err.detail}`);
        setNotifying(null);
        return;
      }

      const orderData = await res.json();
      
      const resScript = await loadRazorpayScript();
      if (!resScript) {
        alert("Razorpay SDK failed to load. Are you online?");
        setNotifying(null);
        return;
      }
      
      const options = {
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || "rzp_test_mock_key",
        amount: orderData.amount_paise,
        currency: orderData.currency,
        name: "Aether Global Super-App",
        description: `Secure Booking for ${itemName}`,
        order_id: orderData.order_id,
        handler: async function (response: any) {
             alert(`💳 Payment Verified! Order ID: ${response.razorpay_order_id}. Your Aadhar KYC was verified successfully.`);
             setSelectedItem(null);
             setAadharNo("");
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0B1120] text-white">
        <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <div className="text-xl font-light tracking-widest text-blue-400">INITIALIZING AETHER GLOBAL...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B1120] text-gray-100 font-sans selection:bg-blue-500/30">
      {/* Navbar */}
      <nav className="fixed w-full z-50 bg-[#0B1120]/80 backdrop-blur-lg border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
             <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center font-bold text-white shadow-[0_0_15px_rgba(16,185,129,0.5)]">A</div>
             <h1 className="text-2xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
               Aether Global
             </h1>
          </div>
          <button 
            onClick={handleLogout}
            className="px-5 py-2 rounded-full border border-red-500/50 text-red-400 hover:bg-red-500 hover:text-white transition-all text-sm font-medium shadow-[0_0_10px_rgba(239,68,68,0.2)] hover:shadow-[0_0_20px_rgba(239,68,68,0.4)]"
          >
            Logout session
          </button>
        </div>
      </nav>

      <main className="pt-28 pb-20 px-6 max-w-7xl mx-auto">
        
        {/* Search Hero Section (MakeMyTrip Style) */}
        <div className="relative rounded-3xl overflow-hidden mb-12 shadow-2xl border border-gray-800 p-1">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-900/40 to-emerald-900/20 backdrop-blur-3xl z-0"></div>
          <div className="relative z-10 bg-[#111827]/80 rounded-[22px] p-8 md:p-12">
             <h2 className="text-3xl md:text-5xl font-bold mb-4 text-white">
               Book Hotels, Flights & <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-green-300">Quick Commerce</span>
             </h2>
             <p className="text-gray-400 text-lg mb-8 max-w-2xl">
               Experience the Super-App powered by LRU caching and Elastic API Gateways for rapid real-time multi-platform aggregation.
             </p>
             
             <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl">📍</span>
                  <input 
                    type="text" 
                    value={searchCity}
                    onChange={(e) => setSearchCity(e.target.value)}
                    className="w-full pl-12 pr-4 py-4 rounded-xl bg-gray-900/80 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-lg font-medium"
                    placeholder="Where to? (e.g. NYC, LON, TYO)"
                  />
                </div>
                <button 
                  type="submit"
                  disabled={isSearching}
                  className="px-10 py-4 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-lg shadow-[0_4px_20px_rgba(59,130,246,0.4)] hover:shadow-[0_8px_30px_rgba(59,130,246,0.6)] transition-all disabled:opacity-50 min-w-[160px]"
                >
                  {isSearching ? <span className="animate-pulse">Scanning...</span> : "Deep Scan"}
                </button>
             </form>
          </div>
        </div>

        {/* Aggregation Results Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
           
           {/* Hotels Section */}
           <section>
             <div className="flex items-center gap-3 mb-6">
                <div className="w-2 h-8 bg-blue-500 rounded-full"></div>
                <h3 className="text-2xl font-bold">Stay Aggregation</h3>
             </div>
             
             <div className="space-y-4">
                {hotels.length === 0 ? (
                  <div className="p-8 rounded-2xl border border-dashed border-gray-700 text-center text-gray-500 bg-gray-900/30">
                     No hotel inventory found.
                  </div>
                ) : (
                  hotels.map((hotel, idx) => (
                    <div key={idx} className="bg-gray-800/60 backdrop-blur-md rounded-2xl p-5 border border-gray-700/50 hover:border-blue-500/50 transition-all flex items-center justify-between group">
                       <div>
                         <h4 className="font-semibold text-lg text-white group-hover:text-blue-400 transition-colors">{hotel.hotel_name}</h4>
                         <div className="flex gap-2 text-sm mt-1">
                           <span className="text-gray-400">Via {hotel.platform}</span>
                           <span className="text-gray-600">•</span>
                           <span className="text-yellow-500 font-medium">★ {hotel.rating}</span>
                         </div>
                       </div>
                       <div className="text-right">
                         <div className="text-2xl font-black text-white">${hotel.price_usd}</div>
                         <button 
                           onClick={() => { setSelectedItem(null); setTimeout(() => setSelectedItem(hotel), 50); }}
                           className="text-blue-400 text-sm font-semibold hover:text-blue-300 transition-colors mt-1"
                         >
                           Select →
                         </button>
                       </div>
                    </div>
                  ))
                )}
             </div>
           </section>

           {/* Food Section */}
           <section>
             <div className="flex items-center gap-3 mb-6">
                <div className="w-2 h-8 bg-emerald-500 rounded-full"></div>
                <h3 className="text-2xl font-bold">Quick Commerce</h3>
             </div>
             
             <div className="space-y-4">
                {food.length === 0 ? (
                  <div className="p-8 rounded-2xl border border-dashed border-gray-700 text-center text-gray-500 bg-gray-900/30">
                     No food items found.
                  </div>
                ) : (
                  food.map((f, idx) => {
                    const bestPrice = Math.min(f.zomato || 9999, f.swiggy || 9999, f.zepto || 9999, f.blinkit || 9999);
                    return (
                    <div key={idx} className="bg-gray-800/60 backdrop-blur-md rounded-2xl p-5 border border-gray-700/50 hover:border-emerald-500/50 transition-all flex items-center justify-between group">
                       <div>
                         <h4 className="font-semibold text-lg text-white group-hover:text-emerald-400 transition-colors">{f.item}</h4>
                         <div className="flex gap-2 text-sm mt-1 mb-2">
                           {f.zomato && <span className="px-2 py-0.5 rounded text-xs bg-red-500/10 text-red-400 border border-red-500/20">Zomato: ₹{f.zomato}</span>}
                           {f.swiggy && <span className="px-2 py-0.5 rounded text-xs bg-orange-500/10 text-orange-400 border border-orange-500/20">Swiggy: ₹{f.swiggy}</span>}
                           {f.zepto && <span className="px-2 py-0.5 rounded text-xs bg-purple-500/10 text-purple-400 border border-purple-500/20">Zepto: ₹{f.zepto}</span>}
                         </div>
                       </div>
                       <div className="text-right flex flex-col items-end">
                         <div className="text-xl font-black text-white">₹{bestPrice}</div>
                         <div className="text-[10px] text-emerald-400 font-medium tracking-wide uppercase mt-0.5 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                           Best on {f.best_vendor}
                         </div>
                         <button 
                           onClick={() => { setSelectedItem(null); setTimeout(() => setSelectedItem(f), 50); }}
                           className="text-emerald-400 text-sm font-semibold hover:text-emerald-300 transition-colors mt-2"
                         >
                           Add to Cart →
                         </button>
                       </div>
                    </div>
                  )})
                )}
             </div>
           </section>
        </div>

        {/* Analytics Section */}
        <section className="mt-16 border-t border-gray-800 pt-16">
           <div className="flex justify-between items-end mb-10">
               <div>
                  <h3 className="text-2xl font-bold mb-2">Platform Analytics</h3>
                  <p className="text-gray-400">Real-time macro transaction monitoring across Aether Global network.</p>
               </div>
           </div>
           
           <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-[#111827] p-6 rounded-2xl border border-gray-800 shadow-xl">
                 <h4 className="text-gray-400 text-sm font-semibold uppercase tracking-widest mb-6 flex items-center gap-2">
                   <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div> Total Revenue Pipeline
                 </h4>
                 <div className="h-72 w-full">
                   <ResponsiveContainer width="100%" height="100%">
                     <BarChart data={analytics.revenue} margin={{top: 0, right: 0, left: -20, bottom: 0}}>
                       <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                       <XAxis dataKey="name" stroke="#6B7280" tick={{fill: '#9CA3AF', fontSize: 12}} axisLine={false} tickLine={false} />
                       <YAxis stroke="#6B7280" tickFormatter={(value) => `$${value/1000}k`} tick={{fill: '#9CA3AF', fontSize: 12}} axisLine={false} tickLine={false} />
                       <Tooltip cursor={{fill: '#1F2937'}} contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px' }} />
                       <Bar dataKey="revenue" fill="url(#blueGradient)" radius={[6, 6, 0, 0]} barSize={40} />
                       <defs>
                          <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#3B82F6" />
                            <stop offset="100%" stopColor="#1D4ED8" />
                          </linearGradient>
                       </defs>
                     </BarChart>
                   </ResponsiveContainer>
                 </div>
              </div>
              
              <div className="bg-[#111827] p-6 rounded-2xl border border-gray-800 shadow-xl">
                 <h4 className="text-gray-400 text-sm font-semibold uppercase tracking-widest mb-6 flex items-center gap-2">
                   <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div> Utilization & Fulfillment
                 </h4>
                 <div className="h-72 w-full">
                   <ResponsiveContainer width="100%" height="100%">
                     <BarChart data={analytics.occupancy} layout="vertical" margin={{top: 0, right: 0, left: 0, bottom: 0}}>
                       <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" horizontal={false} />
                       <XAxis type="number" stroke="#6B7280" domain={[0, 100]} tick={{fill: '#9CA3AF', fontSize: 12}} axisLine={false} tickLine={false} />
                       <YAxis dataKey="name" type="category" stroke="#6B7280" width={80} tick={{fill: '#9CA3AF', fontSize: 12}} axisLine={false} tickLine={false} />
                       <Tooltip cursor={{fill: '#1F2937'}} contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px' }} />
                       <Bar dataKey="rate" fill="url(#emeraldGradient)" radius={[0, 6, 6, 0]} barSize={24} />
                       <defs>
                          <linearGradient id="emeraldGradient" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stopColor="#059669" />
                            <stop offset="100%" stopColor="#10B981" />
                          </linearGradient>
                       </defs>
                     </BarChart>
                   </ResponsiveContainer>
                 </div>
              </div>
           </div>
        </section>
      </main>

      {/* Aadhar KYC Booking Modal */}
      {selectedItem && (
         <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm transition-opacity">
            <div className="bg-gray-900 border border-gray-700 rounded-3xl p-8 max-w-md w-full shadow-2xl relative">
               <button 
                 onClick={() => { setSelectedItem(null); setAadharNo(""); setKycError(""); }}
                 className="absolute top-6 right-6 text-gray-400 hover:text-white"
               >
                 ✕
               </button>
               
               <div className="mb-8">
                  <h3 className="text-2xl font-bold text-white mb-2">Secure Checkout</h3>
                  <p className="text-gray-400">Complete Aadhar verification to book <span className="text-white font-medium">{selectedItem.hotel_name || selectedItem.item}</span>.</p>
               </div>

               <div className="space-y-6">
                 <div>
                   <label className="block text-sm font-medium text-gray-300 mb-2">12-Digit Aadhar Number</label>
                   <input
                     type="text"
                     maxLength={12}
                     value={aadharNo}
                     onChange={(e) => setAadharNo(e.target.value.replace(/\D/g, ''))}
                     className={`w-full px-4 py-3 bg-[#0B1120] border ${kycError ? 'border-red-500' : 'border-gray-700'} rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all font-mono tracking-widest text-center text-lg`}
                     placeholder="0000 0000 0000"
                   />
                   {kycError && <p className="text-red-400 text-sm mt-2">{kycError}</p>}
                 </div>

                 <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 flex gap-4 items-center">
                    <div className="text-blue-400 text-2xl">🛡️</div>
                    <p className="text-xs text-blue-300 leading-relaxed">
                      Your identity is verified securely via Aadhar protocols before initiating the <strong className="text-white">Razorpay</strong> gateway.
                    </p>
                 </div>

                 <button 
                    onClick={handleBookNow}
                    disabled={!!notifying || aadharNo.length !== 12}
                    className="w-full py-4 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 disabled:from-gray-700 disabled:to-gray-700 disabled:text-gray-400 disabled:cursor-not-allowed rounded-xl text-white font-bold text-lg shadow-[0_4px_20px_rgba(16,185,129,0.3)] transition-all flex justify-center items-center"
                 >
                    {notifying ? "Establishing Gateway..." : "Verify & Pay"}
                 </button>
               </div>
            </div>
         </div>
      )}

    </div>
  );
}
