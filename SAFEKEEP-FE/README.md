# SAFEKEEP Frontend (SAFEKEEP-FE)

React + Vite frontend for the SAFEKEEP Dead Man's Switch backend.

## Setup

```bash
cd SAFEKEEP-FE
npm install
cp .env.example .env   # adjust API URL if needed
npm run dev
```

By default the frontend calls the backend at:

```env
VITE_API_BASE_URL=https://127.0.0.1:8080
```

Change this in `.env` if your backend runs on another host/port.

## Scripts

- `npm run dev` – start dev server
- `npm run build` – production build
- `npm run preview` – preview production build

## Features

- Register / Login (JWT)
- Dashboard: timer status, heartbeat, timeout changes
- Vaults: create / edit / delete multiple encrypted payloads
- Beneficiaries: create / edit / delete recipients

