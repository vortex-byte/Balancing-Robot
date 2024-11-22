[![en](https://img.shields.io/badge/LANG-ENGLISH-red.svg)](https://github.com/vortex-byte/Balancing-Robot/blob/main/README.en.md)

# Balancing Robot

Robot self-balancing menggunakan Arduino Mega dan Raspberry Pi 3, dilengkapi GUI untuk komunikasi dan monitoring.

## Fitur

- GUI Monitoring dan Tuning
- Sensor ultrasonik untuk menghindari rintangan
- Layar LCD untuk menampilkan notifikasi 
- Pilihan mode auto pilot dan remote (soon)

## Cara Penggunaan

### Yang Dibutuhkan

- [Putty](https://www.putty.org/) - Untuk login SSH ke Raspberry Pi
- [Git](https://git-scm.com/downloads)
- Kode Editor - Kode editor andalan anda
- Python >= 3.9
- Pip >= 24.x
- SD Card Reader - Untuk modifikasi firmware Raspberry Pi

### Mengubah Konfigurasi Wi-Fi Raspberry Pi

Raspberry Pi memerlukan koneksi Wi-Fi agar bisa berkomunikasi dengan GUI Client. Berikut cara mengubah konfigurasinya:

- Lepas SD Card dari Raspberry Pi
- Gunakan SD Card Reader untuk menghubungkan SD Card dengan PC
- Buka partisi Boot lalu cari file ```wpa_supplicant.conf```
- Edit file tersebut, lalu ubah nama SSID dan password Wi-Fi sesuai dengan jaringan Anda:
```
network={
    ssid="Nama_SSID"
    psk="Password_WiFi"
}
```
- Simpan file lalu pasang kembali SD Card ke Raspberry Pi

## Instalasi

### Instalasi Server GUI

Server GUI diinstal di Raspberry Pi.

1. Nyalakan robot, pastikan Raspberry Pi menyala dan terhubung ke Wi-Fi

2. Pada CMD/Terminal cek ping untuk memastikan Raspberry Pi pada jaringan yang sama:
```
ping raspberrypi -t
```

Tunggu hingga mendapatkan feedback dari Raspberry Pi

3. Buka Putty lalu masukkan pada Hostname: ```raspberrypi``` , Port: ```22``` , Connection Type: ```SSH```. Lalu klik Open
   
4. Jika Raspberry Pi belum terpasang Server GUI, clone repository ini untuk instal:
```
git clone --single-branch --branch server https://github.com/vortex-byte/Balancing-Robot.git
```
```
cd Balancing-Robot
```

5. Instal library yang dibutuhkan
```
pip install requirements
```

6. Jalankan program Python server GUI
```
python server.py
```

7. Simpan alamat IP publik yang muncul pada server (misalnya, 192.168.x.x)


### Instalasi Client GUI

Client GUI dipasang di PC Anda

1. Clone repository ini untuk instalasi
```
git clone --single-branch --branch client https://github.com/vortex-byte/Balancing-Robot.git
```
```
cd Balancing-Robot
```

2. Instal library yang dibutuhkan
```
pip install requirements
```

3. Jalankan program Python server GUI
```
python client.py
```

4. Masukkan alamat IP server yang tadi disimpan

Jika ingin mengubah desain GUI Client, Anda bisa mengikuti tutorial berikut: [Tkinter Designer](https://www.youtube.com/watch?v=Qd-jJjduWeQ)

## Hardware Schematic

![Schematic](https://raw.githubusercontent.com/vortex-byte/Balancing-Robot/refs/heads/main/skematik.jpg)

## Get in touch w/ me :)

- [@vortex-byte](mailto:mzimam.ath@gmail.com)
