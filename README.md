# 🎵 Image Music Looper

โปรแกรมสำหรับสร้างวิดีโอจากภาพและเพลง พร้อมฟีเจอร์ Loop เพลงแบบไร้รอยต่อ

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## 🌟 คุณสมบัติเด่น

- 🖼️ **รองรับไฟล์ภาพหลากหลาย** - JPG, PNG, BMP
- 🎵 **ลูปเพลงไร้รอยต่อ** - ระบบ Crossfade อัตโนมัติ
- ⚙️ **ตั้งค่าได้ตามต้องการ** - ความยาว, อัตราส่วน, Crossfade
- 👁️ **ดูตัวอย่างก่อนสร้าง** - Preview ภาพก่อนและหลัง Crop
- 🖥️ **ใช้งานง่าย** - หน้าต่างโปรแกรมที่ใช้งานง่าย
- 🚀 **ประมวลผลเร็ว** - เครื่องมือที่ปรับแต่งมาให้มีประสิทธิภาพ

## 📥 ดาวน์โหลด

### เวอร์ชันล่าสุด

[**ดาวน์โหลด ImageMusicLooper.exe**](https://github.com/kengkreingkrai/image-music-looper/releases/latest/download/ImageMusicLooper.exe)

### เวอร์ชันก่อนหน้า

[ดูเวอร์ชันทั้งหมด](https://github.com/kengkreingkrai/image-music-looper/releases)

## 🔧 ข้อกำหนดระบบ

- **ระบบปฏิบัติการ:** Windows 10 ขึ้นไป
- **หน่วยความจำ:** RAM อย่างน้อย 4GB
- **พื้นที่ว่าง:** อย่างน้อย 1GB
- **อื่นๆ:** ไม่ต้องติดตั้งโปรแกรมเพิ่มเติม

## 🚀 วิธีใช้งาน

### การติดตั้ง

1. ดาวน์โหลดไฟล์ `ImageMusicLooper.exe`
2. บันทึกไฟล์ไว้ในโฟลเดอร์ที่ต้องการ
3. ดับเบิลคลิกที่ไฟล์เพื่อเริ่มใช้งาน

### การใช้งาน

1. **เลือกไฟล์** - เลือกภาพพื้นหลังและไฟล์เสียง
2. **ตั้งค่า** - กำหนดความยาววิดีโอและอัตราส่วนภาพ
3. **ปรับแต่ง** - ตั้งค่า Crossfade (ถ้าต้องการ)
4. **ดูตัวอย่าง** - ตรวจสอบผลลัพธ์ก่อนสร้าง
5. **สร้างวิดีโอ** - เริ่มการประมวลผล

## 🎯 ไฟล์ที่รองรับ

### ไฟล์ภาพ

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **Bitmap** (.bmp)

### ไฟล์เสียง

- **MP3** (.mp3)
- **WAV** (.wav)
- **M4A** (.m4a)
- **FLAC** (.flac)

## 🛠️ การพัฒนา

### ความต้องการสำหรับการพัฒนา

```bash
pip install -r requirements.txt
```

### การ Build โปรแกรม

```bash
# วิธี 1: ใช้ build script (แนะนำ)
python build.py

# วิธี 2: ใช้ batch file (Windows)
build.bat

# วิธี 3: ใช้ PyInstaller โดยตรง
pyinstaller --onefile --windowed --name ImageMusicLooper app.py
```

### การ Deploy เว็บไซต์ไปยัง GitHub Pages

```bash
# 1. เปิดใช้งาน GitHub Pages
# ไปที่ Settings > Pages ของ repository
# เลือก Source: Deploy from a branch
# เลือก Branch: main / (root)

# 2. เว็บไซต์จะใช้ไฟล์ index.html ใน root directory
# ไม่ต้องสร้าง branch แยก เพราะ index.html อยู่ใน main แล้ว
```

### การสร้าง Release และอัปโหลด .exe

```bash
# 1. Build โปรแกรม
python build.py

# 2. สร้าง tag และ release
git tag v1.0
git push origin v1.0

# 3. ไปที่ GitHub > Releases > Create a new release
# 4. อัปโหลดไฟล์ ImageMusicLooper.exe และ README.txt จาก release/
```

### โครงสร้างโปรแกรม

```
image-music-looper/
├── app.py               # โปรแกรมหลัก
├── build.py            # Script สำหรับ build
├── build.bat           # Batch file สำหรับ Windows
├── requirements.txt    # Dependencies
├── index.html         # GitHub Pages website
├── LICENSE            # MIT License
└── README.md
```

## 🤝 การมีส่วนร่วม

เรายินดีรับการมีส่วนร่วมจากชุมชน! หากคุณต้องการ:

1. **รายงานปัญหา** - [เปิด Issue](https://github.com/kengkreingkrai/image-music-looper/issues)
2. **เสนอฟีเจอร์ใหม่** - [เปิด Feature Request](https://github.com/kengkreingkrai/image-music-looper/issues)
3. **ส่ง Code** - Fork โปรเจกต์และส่ง Pull Request

### การตั้งค่าสำหรับการพัฒนา

```bash
# Clone repository
git clone https://github.com/kengkreingkrai/image-music-looper.git
cd image-music-looper

# ติดตั้ง dependencies
pip install -r requirements.txt

# รันโปรแกรม
python app.py
```

### การ Deploy และ Release

สำหรับผู้ที่ต้องการ deploy โปรเจกต์นี้ ดูคู่มือใน **[DEPLOY.md](DEPLOY.md)** ที่มีขั้นตอนแบบ manual ทั้งหมด

## 📝 สิทธิ์การใช้งาน

โปรเจกต์นี้ใช้สิทธิ์ [MIT License](LICENSE) - ดูรายละเอียดในไฟล์ LICENSE

## 🔗 ลิงก์ที่เป็นประโยชน์

- 🌐 **เว็บไซต์:** [https://kengkreingkrai.github.io/image-music-looper](https://kengkreingkrai.github.io/image-music-looper)
- 📥 **ดาวน์โหลด:** [Releases](https://github.com/kengkreingkrai/image-music-looper/releases)
- 🐛 **รายงานปัญหา:** [Issues](https://github.com/kengkreingkrai/image-music-looper/issues)
- 💡 **เสนอไอเดีย:** [Discussions](https://github.com/kengkreingkrai/image-music-looper/discussions)

## 📊 สถิติ

![GitHub stars](https://img.shields.io/github/stars/kengkreingkrai/image-music-looper?style=social)
![GitHub forks](https://img.shields.io/github/forks/kengkreingkrai/image-music-looper?style=social)
![GitHub issues](https://img.shields.io/github/issues/kengkreingkrai/image-music-looper)
![GitHub pull requests](https://img.shields.io/github/issues-pr/kengkreingkrai/image-music-looper)

## 🙏 ขอบคุณ

ขอบคุณชุมชน Python และ open source community ที่ทำให้โปรเจกต์นี้เป็นไปได้

---

<p align="center">
  สร้างด้วย ❤️ สำหรับชุมชน<br>
  <a href="https://github.com/kengkreingkrai">GitHub Profile</a>
</p>
