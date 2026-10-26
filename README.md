# BIP Update

Repo manifest + paket update APK Ferizy BIP.

File yang dipakai aplikasi:

- `update.json` — manifest versi terbaru.
- `BIP-<versi>-<tanggal>.zip` — paket APK berpassword `@R00t12345`.

APK mentah **tidak** di-upload ke repo ini.

## Cara update

1. Build APK release dari proyek `ASDP BIP - git`:
   ```
   python build_apk.py --project "." --variant release --clean --yes
   ```
2. Jalankan `upload.bat` di folder ini.
   Script akan membuat ZIP berpassword, menulis `update.json`, lalu commit + push.
   Push pertama akan meminta login GitHub (Personal Access Token / browser).
3. Selesai. Aplikasi akan membaca:
   `https://raw.githubusercontent.com/bangipulproject/UPDATE/main/update.json`

## Mode sumber update di aplikasi

Di layar **Cek Update -> Server** tersedia dua mode:

- **Git** (default): manifest GitHub raw di atas, paket ZIP berpassword.
- **Web**: manifest `https://bip.bangipul.my.id/update.json`, APK mentah (tanpa ZIP).
- URL kustom tetap bisa diisi manual; **Reset** mengembalikan ke mode Git.

## Password ZIP

Password ditanam di aplikasi (`UpdateCenter.ZIP_PASSWORD`) dan dipakai script ini:
`@R00t12345`

Kalau password diganti, build ulang APK dengan password baru.
