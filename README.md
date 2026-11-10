# 🌸 Flower FL Simulation (3 Client 1 Server) - Streamlit Cloud Ready

Aplikasi simulasi **Federated Learning (Flower FL)** interaktif yang siap di-deploy secara publik ke **Streamlit Community Cloud (streamlit.io)** dalam beberapa klik!

---

## 🎯 Fitur Aplikasi

- 🌐 **Visual Canvas 60 FPS**: Animasi aliran paket data gRPC (`query.gap_check` / `reply.gap_check` / `FitIns` / `FitRes`) antara 1 Server dan 3 Client.
- 🎛️ **Kontrol Interaktif**: Tombol *Step*, *Reset*, *Broadcast (Server ➔ Klien)*, *Unggah Update*, dan *Agregasi FedAvg*.
- 📶 **Simulasi Client Dropout**: Toggle switch untuk mematikan/menghidupkan klien secara dinamis.
- 📈 **Kurva Konvergensi Plotly**: Grafik interaktif akurasi dan penurunan loss per round.
- 📋 **Inspektor Kepatuhan Regulasi**: Tabel checklist 12 persyaratan UK MDR 2002 (R01-R12) untuk ketiga klien.
- 🛡️ **Privacy-Preserving 100%**: Zero dokumen mentah yang ditransmisikan ke server.

---

## 🚀 Langkah-Langkah Deploy ke Streamlit.io (Streamlit Community Cloud)

### 1. Buat Repository Baru di GitHub
1. Buka [github.com](https://github.com) dan login ke akun GitHub Anda.
2. Klik tombol **New Repository**.
3. Beri nama repository, misalnya: `flower-fl-simulation`.
4. Pilih **Public**, lalu klik **Create repository**.

### 2. Upload / Push Kode ke GitHub
Buka terminal (Git Bash / PowerShell) di folder project ini:
```bash
cd C:\Users\hi\.gemini\antigravity\scratch\flower-streamlit-app
git init
git add .
git commit -m "Initial Flower FL Streamlit simulation app"
git branch -M main
git remote add origin https://github.com/USERNAME_ANDA/flower-fl-simulation.git
git push -u origin main
```
*(Ganti `USERNAME_ANDA` dengan username GitHub Anda)*.

### 3. Deploy di Streamlit.io (share.streamlit.io)
1. Buka situs [share.streamlit.io](https://share.streamlit.io/) dan login menggunakan akun GitHub Anda.
2. Klik tombol **"Create app"** (atau **"New app"**).
3. Isi form deployment:
   - **Repository**: pilih `USERNAME_ANDA/flower-fl-simulation`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (Opsional): bisa pilih nama custom seperti `flower-fl-simulation.streamlit.app`
4. Klik **Deploy!** 🚀
5. Tunggu sekitar 1 - 2 menit hingga build selesai. Aplikasi Anda sekarang sudah online dan bisa diakses oleh siapa saja di seluruh dunia!

---

## 💻 Cara Menjalankan Secara Lokal (Sebelum Deploy)

Cukup klik ganda file:
```
run_local.bat
```
Atau jalankan via terminal:
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka di browser pada `http://localhost:8501`.
