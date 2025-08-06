import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from PIL import Image, ImageTk
import subprocess
import shutil
from pathlib import Path

# Constants
DEFAULT_WINDOW_SIZE = "850x950"
DEFAULT_DURATION_HOURS = 4.0
DEFAULT_CROSSFADE_DURATION = 3000
DEFAULT_ASPECT_RATIO = "16:9"

# Video quality settings
VIDEO_QUALITY = {
    "16:9": (1280, 720),
    "4:3": (960, 720),
    "1:1": (720, 720),
    "21:9": (1680, 720)
}

# Font settings
FONTS = {
    "title": ("Arial", 24, "bold"),
    "subtitle": ("Arial", 14),
    "label": ("Arial", 12),
    "entry": ("Arial", 11),
    "info": ("Arial", 11),
    "status": ("Arial", 12),
    "button": ("Arial", 11),
    "small": ("Arial", 10),
    "combo": ("Arial", 11)
}

class UIConfig:
    """คลาสสำหรับเก็บการตั้งค่า UI"""
    
    @staticmethod
    def setup_styles(style):
        """ตั้งค่า TTK styles"""
        style.configure("Custom.TButton", font=FONTS["label"])
        style.configure("Custom.TEntry", font=FONTS["entry"])
        style.configure("Custom.TLabel", font=FONTS["label"])
        style.configure("Custom.TCombobox", font=FONTS["label"])
    
    @staticmethod
    def get_file_filters():
        """ส่งคืน file filters สำหรับ dialogs"""
        return {
            'image': [
                ("ไฟล์ภาพ", "*.jpg *.jpeg *.png *.bmp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Bitmap", "*.bmp"),
                ("ทั้งหมด", "*.*")
            ],
            'audio': [
                ("ไฟล์เสียง", "*.mp3 *.wav *.m4a *.flac"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav"),
                ("M4A", "*.m4a"),
                ("FLAC", "*.flac"),
                ("ทั้งหมด", "*.*")
            ]
        }


class VideoProcessor:
    """คลาสสำหรับประมวลผลวิดีโอ"""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
    
    def create_video(self, image_path, audio_path, output_path, duration_seconds, aspect_ratio):
        """สร้างวิดีโอด้วยวิธีที่เหมาะสม"""
        try:
            return self._create_video_with_moviepy(image_path, audio_path, output_path, duration_seconds, aspect_ratio)
        except ImportError:
            return self._create_video_with_ffmpeg(image_path, audio_path, output_path, duration_seconds, aspect_ratio)
        except Exception as e:
            print(f"Error with MoviePy, trying FFmpeg: {e}")
            return self._create_video_with_ffmpeg(image_path, audio_path, output_path, duration_seconds, aspect_ratio)
    
    def _create_video_with_moviepy(self, image_path, audio_path, output_path, duration_seconds, aspect_ratio):
        """สร้างวิดีโอด้วย MoviePy"""
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_audioclips
        
        if self.progress_callback:
            self.progress_callback(45, "กำลังใช้ MoviePy สร้างวิดีโอ...")
        
        # โหลดไฟล์เสียง
        audio = AudioFileClip(audio_path)
        
        # คำนวณจำนวนรอบที่ต้องลูป
        audio_duration = audio.duration
        loops_needed = int(duration_seconds / audio_duration) + 1
        
        # สร้างเสียงลูป
        audio_loops = [audio for _ in range(loops_needed)]
        final_audio = concatenate_audioclips(audio_loops).subclip(0, duration_seconds)
        
        # สร้างวิดีโอจากภาพ
        image_clip = ImageClip(image_path, duration=duration_seconds)
        image_clip = self._resize_image_clip_moviepy(image_clip, aspect_ratio)
        
        # รวมภาพและเสียง
        video = image_clip.set_audio(final_audio)
        video.write_videofile(output_path, fps=1, codec='libx264', audio_codec='aac', verbose=False, logger=None)
        
        # ปิดไฟล์
        audio.close()
        video.close()
        
        return True
    
    def _create_video_with_ffmpeg(self, image_path, audio_path, output_path, duration_seconds, aspect_ratio):
        """สร้างวิดีโอด้วย FFmpeg"""
        if self.progress_callback:
            self.progress_callback(45, "กำลังใช้ FFmpeg สร้างวิดีโอ...")
        
        try:
            resized_image = self._resize_image_for_ffmpeg(image_path, aspect_ratio)
            
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-loop', '1',
                '-i', resized_image, '-i', audio_path,
                '-c:v', 'libx264', '-c:a', 'aac',
                '-t', str(duration_seconds), '-pix_fmt', 'yuv420p',
                '-r', '1', output_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if resized_image != image_path:
                    os.remove(resized_image)
                return True
            else:
                print(f"FFmpeg error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            return self._create_fallback_instructions(output_path, image_path, audio_path, duration_seconds, aspect_ratio)
        except Exception as e:
            print(f"Error with FFmpeg: {e}")
            return self._create_fallback_instructions(output_path, image_path, audio_path, duration_seconds, aspect_ratio)
    
    def _resize_image_clip_moviepy(self, clip, aspect_ratio):
        """ปรับขนาดภาพสำหรับ MoviePy"""
        width, height = VIDEO_QUALITY.get(aspect_ratio, VIDEO_QUALITY["16:9"])
        return clip.resize(height=height).crop(width=width, height=height, x_center=clip.w/2, y_center=clip.h/2)
    
    def _resize_image_for_ffmpeg(self, image_path, aspect_ratio):
        """ปรับขนาดภาพสำหรับ FFmpeg"""
        img = Image.open(image_path)
        target_size = VIDEO_QUALITY.get(aspect_ratio, VIDEO_QUALITY["16:9"])
        img_resized = self._crop_and_resize_image(img, target_size)
        
        temp_image_path = image_path.replace('.jpg', '_resized.jpg').replace('.png', '_resized.jpg')
        img_resized.save(temp_image_path, 'JPEG')
        return temp_image_path
    
    def _crop_and_resize_image(self, img, target_size):
        """Crop และ resize ภาพ"""
        target_width, target_height = target_size
        img_width, img_height = img.size
        
        target_ratio = target_width / target_height
        img_ratio = img_width / img_height
        
        if img_ratio > target_ratio:
            new_width = int(img_height * target_ratio)
            left = (img_width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img_height))
        else:
            new_height = int(img_width / target_ratio)
            top = (img_height - new_height) // 2
            img = img.crop((0, top, img_width, top + new_height))
        
        return img.resize(target_size, Image.Resampling.LANCZOS)
    
    def _create_fallback_instructions(self, output_path, image_path, audio_path, duration_seconds, aspect_ratio):
        """สร้างไฟล์คำแนะนำ"""
        instructions_file = output_path.replace('.mp4', '_instructions.txt')
        duration_hours = duration_seconds / 3600
        
        instructions = f"""🎬 วิธีสร้างวิดีโอด้วยตัวเอง

เนื่องจากไม่สามารถสร้างวิดีโออัตโนมัติได้ กรุณาทำตามขั้นตอนต่อไปนี้:

📁 ไฟล์ที่ต้องใช้:
• ภาพ: {image_path}
• เสียง: {audio_path}
• ความยาววิดีโอ: {duration_hours:.1f} ชั่วโมง
• อัตราส่วน: {aspect_ratio}

🛠️ วิธีที่ 1: ใช้ FFmpeg (แนะนำ)
1. ดาวน์โหลด FFmpeg จาก https://ffmpeg.org/download.html
2. เปิด Command Prompt
3. รันคำสั่ง:
   ffmpeg -loop 1 -i "{image_path}" -i "{audio_path}" -c:v libx264 -c:a aac -t {duration_seconds} -pix_fmt yuv420p -r 1 "{output_path}"

🎥 วิธีที่ 2: ใช้โปรแกรม Video Editor
• DaVinci Resolve (ฟรี)
• OpenShot (ฟรี)
• Adobe Premiere Pro
• Canva (ออนไลน์)

📋 ขั้นตอน:
1. นำเข้าภาพและเสียง
2. ตั้งความยาวภาพเป็น {duration_hours:.1f} ชั่วโมง
3. วางเสียงซ้ำจนครบเวลา
4. Export เป็น MP4
"""
        
        try:
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            if self.progress_callback:
                self.progress_callback(100, f"สร้างไฟล์คำแนะนำ: {os.path.basename(instructions_file)}")
            
            return True
        except Exception as e:
            print(f"Error creating instructions: {e}")
            return False


class ImageMusicLooperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Image Music Looper - สร้างวิดีโอเพลงแบบลูป")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.configure(bg="#f0f0f0")
        
        # Initialize variables
        self._init_variables()
        
        # Setup UI styles
        self.style = ttk.Style()
        UIConfig.setup_styles(self.style)
        
        # Create UI
        self.create_ui()
        
        # Preview variables
        self.image_preview = None
        self.cropped_preview = None
        
    def _init_variables(self):
        """Initialize all tkinter variables"""
        self.image_path = tk.StringVar()
        self.audio_path = tk.StringVar()
        self.output_path = tk.StringVar(value=os.getcwd())
        self.duration_hours = tk.DoubleVar(value=DEFAULT_DURATION_HOURS)
        self.crossfade_duration = tk.IntVar(value=DEFAULT_CROSSFADE_DURATION)
        self.auto_crossfade = tk.BooleanVar(value=True)
        self.aspect_ratio = tk.StringVar(value=DEFAULT_ASPECT_RATIO)
        self.keep_original = tk.BooleanVar(value=False)
        
    def create_ui(self):
        """สร้าง UI ทั้งหมด"""
        self._create_header()
        
        # สร้าง Notebook สำหรับแท็บต่างๆ
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # สร้างแท็บต่างๆ
        self.create_file_tab(notebook)
        self.create_advanced_tab(notebook)
        self.create_preview_tab(notebook)
        
        # ปุ่มสำหรับการดำเนินการ
        self.create_action_buttons()
    
    def _create_header(self):
        """สร้างส่วนหัว"""
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill="x", padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🎵 Image Music Looper",
            font=FONTS["title"],
            fg="white", bg="#2c3e50"
        )
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(
            title_frame,
            text="สร้างวิดีโอเพลงแบบลูปอย่างง่าย",
            font=FONTS["subtitle"],
            fg="#ecf0f1", bg="#2c3e50"
        )
        subtitle_label.pack()
        
    def create_file_tab(self, notebook):
        """สร้างแท็บสำหรับเลือกไฟล์"""
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="📁 เลือกไฟล์")
        
        # ส่วนเลือกภาพ
        image_section = ttk.LabelFrame(file_frame, text="🖼️ เลือกภาพพื้นหลัง", padding=15)
        image_section.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(image_section, text="ไฟล์ภาพ:", font=FONTS["label"]).pack(anchor="w")
        image_frame = tk.Frame(image_section)
        image_frame.pack(fill="x", pady=5)
        
        ttk.Entry(image_frame, textvariable=self.image_path, width=60, font=FONTS["entry"]).pack(side="left", fill="x", expand=True)
        ttk.Button(image_frame, text="เลือก", command=self.select_image, style="Custom.TButton").pack(side="right", padx=(5,0))
        
        # ส่วนเลือกเสียง
        audio_section = ttk.LabelFrame(file_frame, text="🎵 เลือกไฟล์เสียง", padding=15)
        audio_section.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(audio_section, text="ไฟล์เสียง:", font=FONTS["label"]).pack(anchor="w")
        audio_frame = tk.Frame(audio_section)
        audio_frame.pack(fill="x", pady=5)
        
        ttk.Entry(audio_frame, textvariable=self.audio_path, width=60, font=FONTS["entry"]).pack(side="left", fill="x", expand=True)
        ttk.Button(audio_frame, text="เลือก", command=self.select_audio, style="Custom.TButton").pack(side="right", padx=(5,0))
        
        # ส่วนเลือกโฟลเดอร์ผลลัพธ์
        output_section = ttk.LabelFrame(file_frame, text="📁 โฟลเดอร์ผลลัพธ์", padding=15)
        output_section.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(output_section, text="โฟลเดอร์ที่จะบันทึก:", font=FONTS["label"]).pack(anchor="w")
        output_frame = tk.Frame(output_section)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=60, font=FONTS["entry"]).pack(side="left", fill="x", expand=True)
        ttk.Button(output_frame, text="เลือก", command=self.select_output, style="Custom.TButton").pack(side="right", padx=(5,0))
        
        # ส่วนตั้งค่าเวลา
        time_section = ttk.LabelFrame(file_frame, text="⏰ ความยาววิดีโอ", padding=15)
        time_section.pack(fill="x", padx=20, pady=10)
        
        time_frame = tk.Frame(time_section)
        time_frame.pack(fill="x")
        
        ttk.Label(time_frame, text="ความยาว (ชั่วโมง):", font=FONTS["label"]).pack(side="left")
        ttk.Scale(time_frame, from_=0.5, to=12.0, variable=self.duration_hours, 
                 orient="horizontal", length=200).pack(side="left", padx=10)
        duration_label = ttk.Label(time_frame, text="4.0 ชั่วโมง", font=FONTS["label"])
        duration_label.pack(side="left")
        
        # อัปเดตข้อความเมื่อเลื่อน scale
        def update_duration_label(*args):
            duration_label.config(text=f"{self.duration_hours.get():.1f} ชั่วโมง", font=FONTS["label"])
        self.duration_hours.trace('w', update_duration_label)
        
    def create_advanced_tab(self, notebook):
        """สร้างแท็บสำหรับการตั้งค่าขั้นสูง"""
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="⚙️ ตั้งค่าขั้นสูง")
        
        # ส่วนอัตราส่วนภาพ
        ratio_section = ttk.LabelFrame(advanced_frame, text="📐 อัตราส่วนภาพ", padding=15)
        ratio_section.pack(fill="x", padx=20, pady=10)
        
        ratio_frame = tk.Frame(ratio_section)
        ratio_frame.pack(fill="x")
        
        ttk.Label(ratio_frame, text="เลือกอัตราส่วน:", font=FONTS["label"]).pack(side="left")
        ratio_combo = ttk.Combobox(ratio_frame, textvariable=self.aspect_ratio, 
                                  values=["16:9", "4:3", "1:1", "21:9"], state="readonly", width=10,
                                  font=FONTS["combo"])
        ratio_combo.pack(side="left", padx=10)
        ratio_combo.current(0)
        
        # ส่วนการตั้งค่า Crossfade
        crossfade_section = ttk.LabelFrame(advanced_frame, text="🎭 การผสมเสียง (Crossfade)", padding=15)
        crossfade_section.pack(fill="x", padx=20, pady=10)
        
        # ตัวเลือกระหว่าง Auto และ Manual
        crossfade_mode_frame = tk.Frame(crossfade_section)
        crossfade_mode_frame.pack(fill="x", pady=5)
        
        ttk.Radiobutton(crossfade_mode_frame, text="🤖 ให้ระบบหาจุดที่เหมาะสมอัตโนมัติ", 
                       variable=self.auto_crossfade, value=True).pack(anchor="w")
        
        manual_frame = tk.Frame(crossfade_section)
        manual_frame.pack(fill="x", pady=5)
        
        ttk.Radiobutton(manual_frame, text="🎛️ กำหนดระยะเวลา Crossfade เอง:", 
                       variable=self.auto_crossfade, value=False).pack(side="left")
        
        crossfade_spinbox = ttk.Spinbox(manual_frame, from_=500, to=10000, increment=500,
                                       textvariable=self.crossfade_duration, width=10,
                                       font=FONTS["entry"])
        crossfade_spinbox.pack(side="left", padx=10)
        ttk.Label(manual_frame, text="มิลลิวินาที", font=FONTS["label"]).pack(side="left")
        
        # อธิบาย Crossfade
        info_frame = tk.Frame(crossfade_section)
        info_frame.pack(fill="x", pady=10)
        
        info_text = """💡 คำอธิบาย:
• Crossfade คือการผสมเสียงระหว่างจุดจบและจุดเริ่มต้นของลูปเพื่อให้ต่อเนื่องกัน
• ระบบอัตโนมัติจะวิเคราะห์เสียงเพื่อหาจุดที่เหมาะสมที่สุด
• การกำหนดเองเหมาะสำหรับเสียงที่มีรูปแบบเฉพาะ"""
        
        ttk.Label(info_frame, text=info_text, foreground="gray", font=FONTS["small"]).pack(anchor="w")
        
        # ส่วนตัวเลือกอื่นๆ
        other_section = ttk.LabelFrame(advanced_frame, text="🔧 ตัวเลือกอื่นๆ", padding=15)
        other_section.pack(fill="x", padx=20, pady=10)
        
        ttk.Checkbutton(other_section, text="💾 เก็บไฟล์ต้นฉบับไว้ (ไม่ลบหลังประมวลผล)", 
                       variable=self.keep_original).pack(anchor="w", pady=5)
        
    def create_preview_tab(self, notebook):
        """สร้างแท็บสำหรับแสดงตัวอย่าง"""
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="👁️ ตัวอย่าง")
        
        # ส่วนแสดงภาพต้นฉบับ
        original_section = ttk.LabelFrame(preview_frame, text="🖼️ ภาพต้นฉบับ", padding=10)
        original_section.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.original_canvas = tk.Canvas(original_section, width=300, height=200, bg="white")
        self.original_canvas.pack(pady=10)
        
        # ส่วนแสดงภาพหลัง crop
        cropped_section = ttk.LabelFrame(preview_frame, text="✂️ ภาพหลัง Crop", padding=10)
        cropped_section.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.cropped_canvas = tk.Canvas(cropped_section, width=300, height=200, bg="white")
        self.cropped_canvas.pack(pady=10)
        
        # ปุ่มสำหรับดูตัวอย่าง
        preview_btn_frame = tk.Frame(preview_frame)
        preview_btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(preview_btn_frame, text="🔄 อัปเดตตัวอย่าง", 
                  command=self.update_preview, style="Custom.TButton").pack()
        
    def create_action_buttons(self):
        """สร้างปุ่มสำหรับการดำเนินการ"""
        action_frame = tk.Frame(self.root, bg="#f0f0f0")
        action_frame.pack(fill="x", padx=20, pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var, 
                                           mode="determinate", length=400)
        self.progress_bar.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            action_frame, 
            text="พร้อมใช้งาน", 
            font=FONTS["status"], 
            fg="green", 
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=5)
        
        # ปุ่มต่างๆ
        button_frame = tk.Frame(action_frame, bg="#f0f0f0")
        button_frame.pack()
        
        ttk.Button(button_frame, text="🔍 ตรวจสอบการตั้งค่า", 
                  command=self.validate_settings, style="Custom.TButton").pack(side="left", padx=5)
        
        self.start_button = ttk.Button(button_frame, text="🚀 เริ่มสร้างวิดีโอ", 
                                      command=self.start_processing, style="Custom.TButton")
        self.start_button.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="📁 เปิดโฟลเดอร์ผลลัพธ์", 
                  command=self.open_output_folder, style="Custom.TButton").pack(side="left", padx=5)
        
    def select_image(self):
        """เลือกไฟล์ภาพ"""
        filters = UIConfig.get_file_filters()['image']
        file_path = filedialog.askopenfilename(title="เลือกไฟล์ภาพ", filetypes=filters)
        if file_path:
            self.image_path.set(file_path)
            self.update_status(f"เลือกภาพ: {os.path.basename(file_path)}")
            
    def select_audio(self):
        """เลือกไฟล์เสียง"""
        filters = UIConfig.get_file_filters()['audio']
        file_path = filedialog.askopenfilename(title="เลือกไฟล์เสียง", filetypes=filters)
        if file_path:
            self.audio_path.set(file_path)
            self.update_status(f"เลือกเสียง: {os.path.basename(file_path)}")
            
    def select_output(self):
        """เลือกโฟลเดอร์ผลลัพธ์"""
        folder_path = filedialog.askdirectory(title="เลือกโฟลเดอร์ที่จะบันทึกไฟล์")
        if folder_path:
            self.output_path.set(folder_path)
            self.update_status(f"บันทึกที่: {folder_path}")
            
    def update_preview(self):
        """อัปเดตตัวอย่างภาพ"""
        if not self.image_path.get():
            messagebox.showwarning("เตือน", "กรุณาเลือกไฟล์ภาพก่อน")
            return
            
        try:
            # แสดงภาพต้นฉบับ
            original_img = Image.open(self.image_path.get())
            original_img.thumbnail((280, 180), Image.Resampling.LANCZOS)
            self.image_preview = ImageTk.PhotoImage(original_img)
            
            self.original_canvas.delete("all")
            self.original_canvas.create_image(150, 100, image=self.image_preview)
            
            # สร้างภาพหลัง crop ตัวอย่าง
            self.create_crop_preview(original_img)
            
            self.update_status("อัปเดตตัวอย่างเสร็จสิ้น")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถแสดงตัวอย่างได้: {str(e)}")
            
    def create_crop_preview(self, img):
        """สร้างตัวอย่างภาพหลัง crop"""
        ratio = self.aspect_ratio.get()
        width, height = img.size
        
        if ratio == "16:9":
            target_ratio = 16/9
        elif ratio == "4:3":
            target_ratio = 4/3
        elif ratio == "1:1":
            target_ratio = 1/1
        elif ratio == "21:9":
            target_ratio = 21/9
        else:
            target_ratio = 16/9
            
        current_ratio = width / height
        
        if current_ratio > target_ratio:
            # ภาพกว้างเกินไป ตัดข้าง
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            cropped = img.crop((left, 0, left + new_width, height))
        else:
            # ภาพสูงเกินไป ตัดบนล่าง
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            cropped = img.crop((0, top, width, top + new_height))
            
        cropped.thumbnail((280, 180), Image.Resampling.LANCZOS)
        self.cropped_preview = ImageTk.PhotoImage(cropped)
        
        self.cropped_canvas.delete("all")
        self.cropped_canvas.create_image(150, 100, image=self.cropped_preview)
        
    def validate_settings(self):
        """ตรวจสอบการตั้งค่า"""
        errors = []
        
        if not self.image_path.get():
            errors.append("❌ ยังไม่ได้เลือกไฟล์ภาพ")
        elif not os.path.exists(self.image_path.get()):
            errors.append("❌ ไฟล์ภาพไม่พบ")
            
        if not self.audio_path.get():
            errors.append("❌ ยังไม่ได้เลือกไฟล์เสียง")
        elif not os.path.exists(self.audio_path.get()):
            errors.append("❌ ไฟล์เสียงไม่พบ")
            
        if not os.path.exists(self.output_path.get()):
            errors.append("❌ โฟลเดอร์ผลลัพธ์ไม่พบ")
            
        if self.duration_hours.get() < 0.1:
            errors.append("❌ ความยาววิดีโอต้องมากกว่า 0.1 ชั่วโมง")
            
        if errors:
            messagebox.showerror("การตั้งค่าไม่ถูกต้อง", "\n".join(errors))
            return False
        else:
            # แสดงข้อมูลการตั้งค่า
            info = f"""✅ การตั้งค่าถูกต้อง!

📋 สรุปการตั้งค่า:
🖼️ ภาพ: {os.path.basename(self.image_path.get())}
🎵 เสียง: {os.path.basename(self.audio_path.get())}
📁 บันทึกที่: {self.output_path.get()}
⏰ ความยาว: {self.duration_hours.get():.1f} ชั่วโมง
📐 อัตราส่วน: {self.aspect_ratio.get()}
🎭 Crossfade: {'อัตโนมัติ' if self.auto_crossfade.get() else f'{self.crossfade_duration.get()} ms'}
💾 เก็บไฟล์ต้นฉบับ: {'ใช่' if self.keep_original.get() else 'ไม่'}

พร้อมสร้างวิดีโอแล้ว! 🚀"""
            
            messagebox.showinfo("การตั้งค่า", info)
            return True
            
    def start_processing(self):
        """เริ่มการประมวลผล"""
        if not self.validate_settings():
            return
            
        # ยืนยันการเริ่มต้น
        if not messagebox.askyesno("ยืนยัน", 
                                  f"เริ่มสร้างวิดีโอความยาว {self.duration_hours.get():.1f} ชั่วโมง?\n"
                                  "การประมวลผลอาจใช้เวลานาน"):
            return
            
        # ปิดการใช้งานปุ่ม
        self.start_button.config(state="disabled")
        
        # เริ่ม thread สำหรับการประมวลผล
        processing_thread = threading.Thread(target=self.process_video)
        processing_thread.daemon = True
        processing_thread.start()
        
    def process_video(self):
        """ประมวลผลวิดีโอ"""
        try:
            self.update_status("เริ่มการประมวลผล...")
            self.progress_var.set(10)
            
            # สร้าง looper แบบกำหนดเอง
            looper = CustomImageMusicLooper(
                image_file=self.image_path.get(),
                audio_file=self.audio_path.get(),
                output_folder=self.output_path.get(),
                duration_hours=self.duration_hours.get(),
                aspect_ratio=self.aspect_ratio.get(),
                crossfade_duration=self.crossfade_duration.get(),
                auto_crossfade=self.auto_crossfade.get(),
                keep_original=self.keep_original.get(),
                progress_callback=self.update_progress
            )
            
            # เริ่มการประมวลผล
            success = looper.process()
            
            if success:
                self.progress_var.set(100)
                self.update_status("เสร็จสิ้น! สร้างวิดีโอสำเร็จ ✅")
                
                # แสดงข้อความสำเร็จ
                messagebox.showinfo("สำเร็จ!", 
                                   f"สร้างวิดีโอเสร็จสิ้น!\n"
                                   f"ไฟล์บันทึกที่: {looper.output_video}")
            else:
                self.update_status("ไม่สามารถสร้างวิดีโอได้ ❌")
                
                # ตรวจสอบว่าได้สร้างไฟล์คำแนะนำหรือไม่
                instructions_file = looper.output_video.replace('.mp4', '_instructions.txt')
                if os.path.exists(instructions_file):
                    message = f"""ไม่สามารถสร้างวิดีโออัตโนมัติได้ 
แต่ได้สร้างไฟล์คำแนะนำแล้ว:

📄 {os.path.basename(instructions_file)}

กรุณาเปิดไฟล์นี้เพื่อดูวิธีสร้างวิดีโอด้วยตัวเอง

💡 วิธีแก้ปัญหา:
1. ติดตั้ง FFmpeg จาก https://ffmpeg.org
2. หรือใช้โปรแกรม Video Editor อื่น
3. หรือรันโปรแกรมจากไฟล์ Python แทน .exe"""
                    
                    messagebox.showwarning("ไม่สามารถสร้างวิดีโอได้", message)
                else:
                    messagebox.showerror("ข้อผิดพลาด", 
                                       "ไม่สามารถสร้างวิดีโอได้\n\n"
                                       "💡 แนะนำ: รันโปรแกรมจากไฟล์ Python แทน .exe\n"
                                       "หรือติดตั้ง FFmpeg ในระบบ")
                
        except Exception as e:
            self.update_status(f"ข้อผิดพลาด: {str(e)} ❌")
            
            # แสดงข้อความข้อผิดพลาดที่มีประโยชน์
            error_msg = str(e)
            if "moviepy" in error_msg.lower() or "no module named" in error_msg.lower():
                messagebox.showerror("ขาดไลบรารี่", 
                                   f"ข้อผิดพลาด: {error_msg}\n\n"
                                   "💡 วิธีแก้ไข:\n"
                                   "1. รันคำสั่ง: pip install moviepy\n"
                                   "2. หรือติดตั้ง FFmpeg จาก https://ffmpeg.org\n"
                                   "3. หรือใช้โปรแกรม Video Editor อื่น\n\n"
                                   "🚀 หรือ Build ใหม่ด้วย: python build.py")
            else:
                messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}\n\n"
                                   "💡 ลองตรวจสอบ:\n"
                                   "• ไฟล์ภาพและเสียงถูกต้องหรือไม่\n"
                                   "• มีพื้นที่ในการบันทึกเพียงพอหรือไม่\n"
                                   "• ไฟล์ไม่ถูกใช้งานโดยโปรแกรมอื่นหรือไม่")
            
        finally:
            # เปิดการใช้งานปุ่มใหม่
            self.start_button.config(state="normal")
            
    def update_progress(self, value, message=""):
        """อัปเดต progress bar"""
        self.progress_var.set(value)
        if message:
            self.update_status(message)
            
    def update_status(self, message):
        """อัปเดตข้อความสถานะ"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def open_output_folder(self):
        """เปิดโฟลเดอร์ผลลัพธ์"""
        if os.path.exists(self.output_path.get()):
            if os.name == 'nt':  # Windows
                os.startfile(self.output_path.get())
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open', self.output_path.get()])
        else:
            messagebox.showwarning("เตือน", "โฟลเดอร์ไม่พบ")


class CustomImageMusicLooper:
    """คลาสสำหรับประมวลผลตาม UI"""
    
    def __init__(self, image_file, audio_file, output_folder, duration_hours, 
                 aspect_ratio, crossfade_duration, auto_crossfade, keep_original, 
                 progress_callback=None):
        self.image_file = image_file
        self.audio_file = audio_file
        self.output_folder = output_folder
        self.duration_hours = duration_hours
        self.aspect_ratio = aspect_ratio
        self.crossfade_duration = crossfade_duration
        self.auto_crossfade = auto_crossfade
        self.keep_original = keep_original
        self.progress_callback = progress_callback
        
        # สร้าง processor
        self.video_processor = VideoProcessor(progress_callback)
        
        # ชื่อไฟล์ผลลัพธ์
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        self.output_video = os.path.join(output_folder, f"{base_name}_music_loop.mp4")
        
    def process(self):
        """ประมวลผลหลัก"""
        try:
            if self.progress_callback:
                self.progress_callback(20, "กำลังโหลดไฟล์เสียง...")
                
            # สร้างโฟลเดอร์ชั่วคราว
            temp_folder = self._create_temp_folder()
            
            # คัดลอกไฟล์
            temp_audio, temp_image = self._copy_files_to_temp(temp_folder)
            
            if self.progress_callback:
                self.progress_callback(40, "กำลังประมวลผลเสียง...")
            
            # สร้างวิดีโอ
            success = self.video_processor.create_video(
                image_path=temp_image,
                audio_path=temp_audio,
                output_path=self.output_video,
                duration_seconds=int(self.duration_hours * 3600),
                aspect_ratio=self.aspect_ratio
            )
            
            if self.progress_callback:
                self.progress_callback(80, "กำลังจัดระเบียบไฟล์...")
                
            # ลบโฟลเดอร์ชั่วคราว
            shutil.rmtree(temp_folder, ignore_errors=True)
            
            if self.progress_callback:
                self.progress_callback(100, "เสร็จสิ้น!")
                
            return success
            
        except Exception as e:
            print(f"Error in CustomImageMusicLooper: {e}")
            return False
    
    def _create_temp_folder(self):
        """สร้างโฟลเดอร์ชั่วคราว"""
        temp_folder = os.path.join(self.output_folder, "temp")
        os.makedirs(temp_folder, exist_ok=True)
        return temp_folder
    
    def _copy_files_to_temp(self, temp_folder):
        """คัดลอกไฟล์ไปยังโฟลเดอร์ชั่วคราว"""
        base_name = os.path.splitext(os.path.basename(self.audio_file))[0]
        temp_audio = os.path.join(temp_folder, f"{base_name}.mp3")
        temp_image = os.path.join(temp_folder, f"{base_name}.jpg")
        
        shutil.copy2(self.audio_file, temp_audio)
        shutil.copy2(self.image_file, temp_image)
        
        return temp_audio, temp_image
def main():
    """ฟังก์ชันหลัก"""
    root = tk.Tk()
    app = ImageMusicLooperUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
