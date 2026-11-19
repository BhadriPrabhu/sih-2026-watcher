# SIH 2026 Result Watcher

A lightweight, serverless Python bot running on **GitHub Actions** and routed through a **Vercel Mumbai (`bom1`) proxy** that monitors `sih.gov.in` every 30 minutes and sends an instant push notification to your phone via **ntfy.sh** whenever the page updates.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Serverless-2088FF?logo=github-actions&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Mumbai_bom1-000000?logo=vercel&logoColor=white)
![ntfy.sh](https://img.shields.io/badge/Notifications-ntfy.sh-339989)

---

## Architecture

```mermaid
graph TD
    Cron["GitHub Actions Scheduler (Cron every 30 mins)"]
    Runner["GitHub Actions Runner (Ubuntu + Python 3.11)"]
    Secrets[("GitHub Secrets (WEBHOOK_URL)")]
    Repo[("GitHub Repository (last_hash.txt)")]
    Script["SIH Watcher Script (check_sih.py + BeautifulSoup)"]
    Proxy["Vercel Serverless Proxy (api/sih.js - Mumbai bom1)"]
    SIH["SIH 2026 Portal (sih.gov.in over HTTPS)"]
    Ntfy["ntfy.sh Server (HTTP Push API)"]
    Phone["User Phone (ntfy Mobile App)"]

    Cron -->|Triggers scheduled workflow run| Runner
    Runner -->|Checks out files and executes| Script
    Secrets -->|Injects WEBHOOK_URL environment variable into| Script
    Script -->|Sends HTTP GET request to| Proxy
    Proxy -->|Fetches page from Indian region IP| SIH
    SIH -->|Returns HTML content to| Proxy
    Proxy -->|Forwards HTML response to| Script
    Script -->|Reads previous SHA-256 hash from| Repo
    Script -->|Writes new hash on content change to| Repo
    Runner -->|Commits and pushes updated last_hash.txt to| Repo
    Script -->|Sends HTTP POST alert with matched keywords to| Ntfy
    Ntfy -->|Delivers instant push notification to| Phone
```

---

## Features

- **Zero Cost & Serverless:** Runs entirely on GitHub Actions and Vercel's free tier.
- **Geo-Block Bypass:** Routes requests through a custom Vercel serverless function pinned to Mumbai (`bom1`) to avoid `.gov.in` foreign IP blocks.
- **Change Detection:** Uses SHA-256 hashing to catch *any* text update on the SIH portal without sending duplicate alerts.
- **Keyword Matching:** Scans for terms like `shortlisted`, `result`, `grand finale 2026`, and `results out`.
- **Instant Push Alerts:** Uses [ntfy.sh](https://ntfy.sh/) - no account sign-up or email passwords required.

---

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── check.yml      # Cron schedule, Python setup, and auto-commit job
├── api/
│   └── sih.js             # Vercel serverless proxy function
├── vercel.json            # Pins Vercel compute region to Mumbai (bom1)
├── check_sih.py           # Scraper, hasher, and ntfy notification script
├── last_hash.txt          # Auto-generated state file (tracks last known page hash)
└── README.md
```

---

## Setup Guide

### 1. Deploy the Mumbai Proxy (Vercel)
1. Sign in to [Vercel](https://vercel.com) with GitHub and import this repository.
2. Click **Deploy** (default settings). `vercel.json` automatically pins the function to Mumbai (`bom1`).
3. Copy your deployed endpoint URL (`https://<your-app>.vercel.app/api/sih`) and paste it into `PROXY_URL` in `check_sih.py`.

### 2. Subscribe on Your Phone (ntfy)
1. Install the **ntfy** app ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) / [iOS](https://apps.apple.com/us/app/ntfy/id1625396347)).
2. Tap **+** and subscribe to a hard-to-guess topic name (e.g., `sih-2026-alert-9x8k2m`).
   > Treat your topic name like a password - anyone who knows it can view or send messages to it.

### 3. Configure GitHub Secrets & Permissions
1. Go to **Settings → Secrets and variables → Actions → New repository secret**.
   - **Name:** `WEBHOOK_URL`
   - **Value:** `https://ntfy.sh/your-secret-topic-name`
2. Go to **Settings → Actions → General → Workflow permissions**, select **Read and write permissions**, and click **Save**.

### 4. Test It
Go to the **Actions** tab → **SIH 2026 Result Watcher** → **Run workflow**.  
The first run creates `last_hash.txt` and sends a test alert. Subsequent runs stay silent until the website changes.

---

## Customization

- **Check Frequency:** Edit the `cron` expression in `.github/workflows/check.yml` (default: `'*/30 * * * *'` for every 30 minutes).
- **Keywords:** Modify the `KEYWORDS` list at the top of `check_sih.py`.
