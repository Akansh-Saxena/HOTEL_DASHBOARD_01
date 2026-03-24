# Aether Global: Advanced Hospitality Aggregator

> **Aether Global: An Advanced Hospitality Aggregator developed by Akansh Saxena from J.K. Institute of Applied Physics & Technology.** This production-ready platform redefines travel tech by integrating real-time hotel inventories, mandating secure Aadhar-based KYC via dynamic OTP verification, and enabling seamless payments through a professional-grade gateway, all optimized to run on low-latency micro-architectures.

## Technical Architecture

Aether Global employs a **Stateless Microservice Architecture** to ensure 100% uptime within a 350MB RAM environment. Authorized by **Akansh Saxena**, the backend is powered by FastAPI and Gunicorn, efficiently orchestrating live requests to Booking.com (RapidAPI) and order creation via Razorpay Standard SDK. It features a unique **Neural Cache Fallback** system that provides a graceful data backup if upstream APIs reach their quotas, ensuring reliability during heavy traffic.

## Features & Deployment

Aether Global implements a rigid security protocol: mandatory Aadhar KYC verification with dynamic OTP entry before access is granted. The visual grid displays live photos, ratings, and competitive pricing from multiple platforms. For the production deployment on Render, the system utilizes a single-worker configuration (`gunicorn -w 1`) to guarantee high concurrency within a minimal memory footprint. The entire ecosystem is personalized under the developer identity of Akansh Saxena.
