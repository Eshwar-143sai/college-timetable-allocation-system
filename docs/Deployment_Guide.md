# Deployment Guide
## College Timetable Allocation System

This document outlines the steps to deploy the College Timetable Allocation System into a production-grade hosting environment.

---

## 1. Production Architecture Overview

In production, the application is divided into a three-tier system:
1. **Frontend**: Static files served directly via **Nginx** for high speed and low latency.
2. **Backend**: FastAPI running inside **Uvicorn** workers, managed by process managers like **Gunicorn** or **PM2**.
3. **Database**: A production-grade **MySQL Server** instance or managed DB.

---

## 2. Server Configuration

### 2.1 Backend Process Manager (Gunicorn + Uvicorn)
To run the backend with multiple CPU cores support and auto-restart capability, run Gunicorn with Uvicorn workers:
1. Install Gunicorn inside the python virtual environment:
   ```bash
   pip install gunicorn
   ```
2. Create a systemd service file `/etc/systemd/system/timetable-backend.service`:
   ```ini
   [Unit]
   Description=FastAPI Timetable Backend Server
   After=network.target

   [Service]
   User=deploy
   WorkingDirectory=/var/www/college-timetable-allocation-system/backend
   EnvironmentFile=/var/www/college-timetable-allocation-system/backend/.env
   ExecStart=/var/www/college-timetable-allocation-system/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable timetable-backend
   sudo systemctl start timetable-backend
   ```

---

## 3. Reverse Proxy Setup (Nginx)

Install Nginx and configure it to serve static frontend files directly and proxy API requests to the Gunicorn server.

1. Install Nginx:
   ```bash
   sudo apt update
   sudo apt install nginx
   ```
2. Create a new site configuration file `/etc/nginx/sites-available/timetable`:
   ```nginx
   server {
       listen 80;
       server_name timetable.yourcollege.edu;

       # 1. Frontend Static Files
       root /var/www/college-timetable-allocation-system/frontend;
       index public/dashboard.html;

       location / {
           try_files $uri $uri/ =404;
       }

       # Serve static assets directly with caching headers
       location /static/ {
           expires 30d;
           add_header Cache-Control "public, no-transform";
       }

       # 2. Backend API Proxy
       location /api/ {
           proxy_pass http://127.0.0.1:8000/api/;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
3. Enable the configuration and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/timetable /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 4. HTTPS Encryption (Let's Encrypt Certbot)

Encrypt all transit data using SSL certificates:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d timetable.yourcollege.edu
```
Follow the interactive prompt to automatically configure redirecting HTTP to HTTPS.

---

## 5. Security & Maintenance Checklist
* **Credentials**: Never commit `.env` files to git. Use secure environment configuration managers.
* **Firewall Setup**: Restrict ports so that only port 80/443 (HTTP/HTTPS) and SSH are open to the public internet. Block port 3306 (MySQL) and port 8000 (FastAPI raw port) to prevent external attacks.
* **Logs Monitor**: Monitor systemd journal logs:
  ```bash
  sudo journalctl -u timetable-backend -f
  ```
