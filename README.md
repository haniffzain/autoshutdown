# AutoShutdown

AutoShutdown ialah utiliti ringan berasaskan Python untuk menjadualkan shutdown atau restart komputer melalui terminal.

## Sasaran v0.1

- Windows dan Linux
- Shutdown selepas tempoh tertentu
- Shutdown pada waktu tertentu
- Restart selepas tempoh tertentu
- Batal arahan shutdown/restart yang telah dijadualkan
- `--dry-run` untuk menguji arahan tanpa mematikan komputer
- Tiada dependency Python pihak ketiga

## Keperluan

- Python 3.10+
- Windows 10/11 atau Linux dengan arahan `shutdown`

## Contoh penggunaan

```bash
python autoshutdown.py shutdown --in 30m
python autoshutdown.py shutdown --at 23:30
python autoshutdown.py restart --in 10m
python autoshutdown.py cancel
python autoshutdown.py shutdown --in 5m --dry-run
```

Format tempoh yang disokong:

- `30s` = 30 saat
- `15m` = 15 minit
- `2h` = 2 jam

## Nota platform

### Windows

AutoShutdown menggunakan arahan terbina dalam Windows `shutdown.exe`.

### Linux

AutoShutdown menggunakan arahan sistem `shutdown`. Sesetengah distro mungkin memerlukan kebenaran `sudo` atau polisi polkit yang sesuai.

## Roadmap

- [x] CLI asas
- [x] Shutdown/restart bertimer
- [x] Shutdown pada waktu tertentu
- [x] Cancel
- [x] Dry-run
- [ ] GUI desktop
- [ ] Jadual harian/mingguan
- [ ] Idle shutdown
- [ ] Shutdown apabila muat turun/tugas selesai
- [ ] Battery/temperature rules
- [ ] System tray
- [ ] Startup integration
- [ ] Log sejarah tindakan

## Lesen

MIT
