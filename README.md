[![en](https://img.shields.io/badge/LANG-ENGLISH-red.svg)](https://github.com/vortex-byte/Balancing-Robot/blob/main/README.en.md)

# Balancing Robot

Robot self-balancing menggunakan Arduino Mega dan Raspberry Pi 3, dilengkapi GUI untuk komunikasi dan monitoring.

## Fitur

- GUI Monitoring dan Tuning
- Sensor ultrasonik untuk menghindari rintangan
- Layar LCD untuk menampilkan notifikasi 
- Pilihan mode auto dan kontrol manual

## Desain Komunikasi

<details>
	<summary><b>Topologi</b></summary>

![Topologi](https://images4.imagebam.com/2b/58/1e/MEXTRR0_o.jpg)
</details>

## Cara Penggunaan

### Yang Dibutuhkan

- [Putty](https://www.putty.org/) - Untuk login SSH ke Raspberry Pi
- [Git](https://git-scm.com/downloads)
- Kode Editor - Kode editor andalan anda
- Python >= 3.9
- Pip >= 24.x
- SD Card Reader - Untuk membuat/modifikasi firmware Raspberry Pi

### Raspberry Pi OS
<details>
	<summary><b>Install Raspberry Pi OS</b></summary>
  
1. Masukkan SD Card ke SD Card reader, lalu masukkan ke PC anda
2. Download, install dan buka [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
3. Sesuaikan dengan tipe Raspberry Pi anda, OS, dan SD Card anda

![Type](https://cdn.mos.cms.futurecdn.net/cQHK7tWkKGRENVuMkR5Gkg-1200-80.png.webp)

4. Klik Edit Settings

![Type](https://cdn.mos.cms.futurecdn.net/u3EMmPAXT4AsU9gUeLHoC-1200-80.png.webp)

5. Pada tab General isi hostname, username, password, SSID, Wi-Fi Password. Agar mudah saat proses login, gunakan konfigurasi berikut:
``` 
Hostname: raspberrypi
Username: pi
Password: pi
SSID: Raspi
Wi-Fi Password: 12345678
TImezone: Asia/Jakarta
Keyboard: US
 ```

![Type](https://cdn.mos.cms.futurecdn.net/Et4hHahUd3dN3nufsLKqFN-1200-80.png.webp)

6. Pada Tab Services centang ``` Enable SSH ``` dan ``` Use password auth ``` lalu klik Save dan Yes hingga proses instalasi selesai

![Type](https://cdn.mos.cms.futurecdn.net/FQPA4pWp9qswNM8feDE4ye-1200-80.png.webp)

</details>
<details>
  <summary><b>Mengubah Konfigurasi Wi-Fi Raspberry Pi</b></summary>

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
</details>

## Instalasi

### Instalasi Server GUI

Server GUI diinstal di Raspberry Pi.

1. Nyalakan robot, pastikan Raspberry Pi menyala dan terhubung ke Wi-Fi yang telah anda buat saat proses instalasi Raspberry Pi OS

2. Pada CMD/Terminal ping hostname untuk memastikan Raspberry Pi berada di jaringan yang sama:
```
ping raspberrypi -t
```

Tunggu hingga mendapatkan feedback dari Raspberry Pi

3. Buka Putty lalu pada Hostname isi dengan yang telah anda buat saat proses instalasi. Hostname: ```raspberrypi``` , Port: ```22``` , Connection Type: ```SSH```. Lalu klik Open
   
4. Jika Raspberry Pi belum terpasang Server GUI, clone repository ini untuk instal:
```
git clone --single-branch --branch server https://github.com/vortex-byte/Balancing-Robot.git
```
```
cd Balancing-Robot
```

5. Instal library yang dibutuhkan
```
pip install -r requirements.txt
```

6. Jalankan program Python server GUI
```
python server.py
```

7. Simpan alamat IP yang muncul pada server (misalnya, 192.168.x.x)


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
pip install -r requirements.txt
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
