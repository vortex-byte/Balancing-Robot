
# Balancing Robot

Robot self balancing menggunakan Arduino Mega dan Raspberry Pi 3 sebagai server komunikasi dengan GUI.
## Fitur

- GUI Monitoring dan Tuning
- Sensor ultrasonik untuk menghindari rintangan
- Layar LCD untuk pemberitahuan
- Pilihan mode auto pilot dan remote (soon)


## Penggunaan

### Hal yang Dibutuhkan

- [Putty](https://www.putty.org/) - Untuk login SSH ke Raspberry Pi
- Kode Editor - Kode editor andalan anda
- Python >= 3.9
- Pip >= 24.x
- SD Card Reader - Untuk modifikasi firmware Raspberry Pi

### Mengubah Konfigurasi Wi-Fi Raspberry Pi

Raspberry Pi membutuhkan Wi-Fi untuk komunikasi dengan Client GUI. Untuk mengubah konfigurasi Wi-Fi pada Raspberry Pi berikut langkahnya:

- Lepas SD Card dari Raspberry Pi
- Gunakan SD Card Reader untuk menghubungkan SD Card dengan PC
- Buka partisi Boot lalu cari file ```wpa_supplicant.conf```
- Cari text seperti berikut, lalu ubah SSID dan password Wi-Fi
```
network={
    ssid="Nama_SSID"
    psk="Password_WiFi"
}
```
- Simpan file lalu pasang kembali SD Card ke Raspberry Pi
## Instalasi

### Instalasi Server GUI

Server GUI dipasang di Raspberry Pi

1. Nyalakan robot, pastikan Raspberry Pi menyala dan terhubung ke Wi-Fi

2. Pada CMD/Terminal cek ping untuk memastikan Raspberry Pi terhubung 1 jaringan dengan PC
```
ping raspberrypi -t
```
3. Jika Raspberry Pi belum terpasang Server GUI, clone repository ini untuk instalasi
```
git clone https://github.com/vortex-byte/Balancing-Robot.git
cd GUI/server
```

4. Instal library yang dibutuhkan
```
pip install requirements
```

5. Jalankan program python server GUI
```
python server.py
```

6. Simpan alamat IP publik yang muncul pada server. Contohnya 192.168.x.x


### Instalasi Client GUI

Client GUI dipasang di PC

1. Clone repository ini untuk instalasi
```
git clone https://github.com/vortex-byte/Balancing-Robot.git
cd GUI/client
```

2. Instal library yang dibutuhkan
```
pip install requirements
```

3. Jalankan program python server GUI
```
python client.py
```

4. Masukkan alamat IP server yang tadi disimpan

Untuk mengubah desain client GUI, anda bisa melakukannya mengikuti tutorial berikut [Tkinter Designer](https://www.youtube.com/watch?v=Qd-jJjduWeQ)
## Get in touch w/ me :)

- [@vortex-byte](mailto:mzimam.ath@gmail.com)
