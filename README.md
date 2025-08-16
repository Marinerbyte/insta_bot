# 📹 Telegram Instagram Video Downloader Bot

A lightweight **Telegram bot** built with Flask, deployed on **Render free-tier**, that downloads Instagram videos, compresses them if needed, and sends them back to the user.

---

## 🚀 Features
- Download Instagram videos using **yt-dlp**
- Compress videos larger than `MAX_MB` using **ffmpeg**
- Deletes temp files after sending → **low disk usage**
- Webhook-based (no polling, works on free Render tier)
- Graceful error handling
- `/health` route for Render health checks

---

## 🛠 Setup

### 1. Clone Repository
