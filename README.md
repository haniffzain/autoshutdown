# AutoShutdown

AutoShutdown ialah utiliti ringan Python untuk menjadualkan shutdown, restart, logout, menutup aplikasi dan menyekat aplikasi buat sementara waktu.

## Fungsi semasa

- Windows dan Linux
- Timed shutdown
- Timed restart
- Timed logout
- Timed close app
- Timed restrict app
- Cancel task aktif
- `--dry-run` untuk CLI
- GUI desktop Tkinter
- Pilihan masa pantas: 5 min, 15 min, 30 min, 1 jam, 2 jam, 3 jam
- App Lock dengan kata laluan
- Kata laluan disimpan sebagai PBKDF2-SHA256 hash dengan salt, bukan plaintext
- Panel kiri dengan animasi ASCII kucing

## Keperluan

- Python 3.10+
- Tkinter
- `psutil`

Pasang dependency:

```bash
pip install -r requirements.txt
```

Pada Linux, jika Tkinter belum tersedia, pasang pakej Tk untuk Python menggunakan package manager distro anda.

## Jalankan GUI

```bash
python gui.py
```

Pada pelancaran pertama, AutoShutdown akan meminta anda menetapkan kata laluan App Lock. Kata laluan diperlukan sebelum task atau sekatan boleh diubah atau dibatalkan.

## CLI

```bash
python autoshutdown.py shutdown --in 30m
python autoshutdown.py shutdown --at 23:30
python autoshutdown.py restart --in 10m
python autoshutdown.py logout --in 15m
python autoshutdown.py logout --at 22:00
python autoshutdown.py cancel
python autoshutdown.py shutdown --in 5m --dry-run
```

Format tempoh:

- `30s` = 30 saat
- `5m` = 5 minit
- `15m` = 15 minit
- `30m` = 30 minit
- `1h` = 1 jam
- `2h` = 2 jam
- `3h` = 3 jam

## Timed Close App

Pilih executable atau masukkan nama process seperti `notepad.exe`. Apabila timer tamat, proses yang sepadan akan ditamatkan.

> Aplikasi mungkin mempunyai kerja yang belum disimpan.

## Timed Restrict App

Pilih aplikasi, masa mula dan tempoh sekatan. Sepanjang sekatan aktif, AutoShutdown memeriksa proses sasaran dan menutupnya jika ia dibuka.

Sekatan ini bersifat sementara dan hanya aktif selagi AutoShutdown berjalan. Ia tidak mengubah registry, permissions atau polisi keselamatan sistem.

## App Lock

Konfigurasi keselamatan disimpan di:

```text
~/.autoshutdown/security.json
```

Fail hanya menyimpan salt dan hash PBKDF2-SHA256. Kata laluan asal tidak disimpan.

## Nota platform

### Windows

Shutdown/restart/logout menggunakan kemudahan native Windows apabila sesuai.

### Linux

Shutdown/restart menggunakan arahan sistem `shutdown`. Logout menggunakan `loginctl`. Sesetengah distro mungkin memerlukan kebenaran sistem yang sesuai.

## Roadmap

- [x] CLI asas
- [x] Shutdown/restart bertimer
- [x] Logout bertimer
- [x] Timed close app
- [x] Timed restrict app
- [x] GUI desktop
- [x] Time presets
- [x] Password App Lock
- [x] ASCII cat animation
- [ ] Countdown visual besar
- [ ] Senarai task berbilang
- [ ] Jadual harian/mingguan
- [ ] System tray
- [ ] Startup integration
- [ ] Log sejarah tindakan
- [ ] Notifikasi sebelum tindakan

## Lesen

MIT
