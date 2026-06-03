# Local Mobile Testing for Patient Portal

Follow these exact steps to test the Patient Portal on a real mobile phone connected to the same Wi-Fi network as your development PC.

### 1. Find PC IP
Open PowerShell and run:
```powershell
ipconfig
```
Look for the `IPv4 Address` under your active Wi-Fi or Ethernet adapter (e.g., `192.168.1.15`).

### 2. Configure Environment Variables
Open a new PowerShell terminal and set these variables before running the backend. Replace `<PC_IP>` with your actual IPv4 address:

```powershell
$env:FRONTEND_URL="http://<PC_IP>:4200"
$env:ADDITIONAL_CORS_ORIGINS="http://<PC_IP>:4200"
$env:FLASK_HOST="0.0.0.0"
$env:FLASK_PORT="5000"
```

### 3. Run Backend
In the same PowerShell window where you set the variables:
```powershell
cd backend
python app.py
```

### 4. Run Frontend
Open a new terminal (doesn't need the env variables) and run:
```powershell
cd frontend
npm run start:mobile
```

### 5. Open on Phone
Make sure your phone is connected to the **same Wi-Fi** as your PC.
Open your mobile browser and navigate to the Patient Portal using the link generated in the confirmation email, which will look like:
`http://<PC_IP>:4200/patient/portal/<token>`

### 6. Troubleshooting
If the page doesn't load on your phone, you might need to allow Windows Firewall access. Ensure the firewall allows incoming connections for:
- Node.js
- Python
- TCP Port 4200
- TCP Port 5000
