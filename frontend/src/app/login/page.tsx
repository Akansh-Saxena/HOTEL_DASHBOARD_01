"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

    try {
      const res = await fetch(`${API_URL}/api/v1/akansh/auth/send-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email })
      });

      if (!res.ok) {
         const errData = await res.json();
         throw new Error(errData.detail || "Failed to dispatch OTP");
      }
      
      setSuccess("Secure code dispatched. Check your inbox.");
      setStep(2);

    } catch (err: any) {
      setError(err.message || "An error occurred dispatching OTP");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

    try {
      const res = await fetch(`${API_URL}/api/v1/akansh/auth/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, otp: otp })
      });

      if (!res.ok) {
        throw new Error("Invalid or Expired Security Code");
      }

      const data = await res.json();
      setToken(data.access_token);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "An authentication error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
      <div className="max-w-md w-full bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-emerald-500"></div>
        <h2 className="text-3xl font-bold text-center text-white mb-8 tracking-tight">
          Aether <span className="text-emerald-500">Gateway</span>
        </h2>
        
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-md mb-6 text-sm text-center">
            {error}
          </div>
        )}

        {success && step === 2 && (
          <div className="bg-emerald-500/10 border border-emerald-500/50 text-emerald-400 p-3 rounded-md mb-6 text-sm text-center">
            {success}
          </div>
        )}

        {step === 1 ? (
            <form onSubmit={handleSendOTP} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  placeholder="admin@aether.com"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full text-white font-semibold py-3 px-4 rounded-lg transition-colors flex justify-center items-center shadow-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? "Transmitting..." : "Send Access Code"}
              </button>
            </form>
        ) : (
            <form onSubmit={handleVerifyOTP} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Neural OTP Code</label>
                <input
                  type="text"
                  required
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all tracking-[0.5em] text-center text-xl font-mono"
                  placeholder="------"
                />
              </div>

              <button
                type="submit"
                disabled={loading || otp.length < 6}
                className="w-full text-white font-semibold py-3 px-4 rounded-lg transition-colors flex justify-center items-center shadow-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50"
              >
                {loading ? "Verifying..." : "Authenticate Access"}
              </button>
              
              <button 
                type="button" 
                onClick={() => setStep(1)}
                className="w-full text-gray-400 text-sm hover:text-white mt-4"
              >
                 ← Use a different email
              </button>
            </form>
        )}
      </div>
    </div>
  );
}
