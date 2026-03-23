"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

    try {
      if (isRegistering) {
        // Registration Flow
        const res = await fetch(`${API_URL}/api/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: username || email.split("@")[0],
            email: email,
            password: password
          })
        });

        if (!res.ok) {
           const errData = await res.json();
           throw new Error(errData.detail || "Registration failed");
        }
        
        setSuccess("Registration successful! You can now login.");
        setIsRegistering(false); // flip back to login mode
        setPassword("");

      } else {
        // Login Flow
        const formData = new URLSearchParams();
        formData.append("username", email); // backend login uses email as username
        formData.append("password", password);

        const res = await fetch(`${API_URL}/api/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: formData.toString(),
        });

        if (!res.ok) {
          throw new Error("Invalid username or password");
        }

        const data = await res.json();
        setToken(data.access_token);
        router.push("/");
      }
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
          Aether <span className={isRegistering ? "text-emerald-500" : "text-blue-500"}>
            {isRegistering ? "Registry" : "Access"}
          </span>
        </h2>
        
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-md mb-6 text-sm text-center">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-emerald-500/10 border border-emerald-500/50 text-emerald-400 p-3 rounded-md mb-6 text-sm text-center">
            {success}
          </div>
        )}

        <form onSubmit={handleAuth} className="space-y-6">
          {isRegistering && (
             <div>
               <label className="block text-sm font-medium text-gray-300 mb-2">Username</label>
               <input
                 type="text"
                 required={isRegistering}
                 value={username}
                 onChange={(e) => setUsername(e.target.value)}
                 className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all"
                 placeholder="your_handle"
               />
             </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={`w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 transition-all ${isRegistering ? 'focus:ring-emerald-500' : 'focus:ring-blue-500'}`}
              placeholder="admin@aether.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 transition-all ${isRegistering ? 'focus:ring-emerald-500' : 'focus:ring-blue-500'}`}
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full text-white font-semibold py-3 px-4 rounded-lg transition-colors flex justify-center items-center shadow-lg ${isRegistering ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" strokeWidth="4" className="opacity-25" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            ) : (isRegistering ? "Create Profile" : "Authenticate Access")}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button 
             onClick={() => {
               setIsRegistering(!isRegistering);
               setError("");
               setSuccess("");
             }}
             type="button" 
             className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            {isRegistering ? "Already have an account? Sign in." : "Need an account? Register database profile."}
          </button>
        </div>
      </div>
    </div>
  );
}
