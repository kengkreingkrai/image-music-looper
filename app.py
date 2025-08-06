import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from PIL import Image, ImageTk
import subprocess

class ImageMusicLooperUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Image Music Looper - สร้างวิดีโอเพลงแบบลูป")
        self.root.geometry("800x900")
        self.root.configure(bg="#f0f0f0")
        
        # ตัวแปรสำหรับเก็บข้อมูล
        self.image_path = tk.StringVar()
        self.audio_path = tk.StringVar()
        self.output_path = tk.StringVar(value=os.getcwd())
        self.duration_hours = tk.DoubleVar(value=4.0)
        self.crossfade_duration = tk.IntVar(value=3000)
        self.auto_crossfade = tk.BooleanVar(value=True)
        self.aspect_ratio = tk.StringVar(value="16:9")
        self.keep_original = tk.BooleanVar(value=False)
        
        # สร้าง UI
        self.create_ui()
        
        # ตัวแปรสำหรับ preview
        self.image_preview = None
        self.cropped_preview = None
        
    def create_ui(self):
        """สร้าง UI ทั้งหมด"""
        # หัวข้อหลัก
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill="x", padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🎵 Image Music Looper",
                              font=("Arial", 20, "bold"),
                              fg="white", bg="#2c3e50")
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(title_frame,
                                 text="สร้างวิดีโอเพลงแบบลูปอย่างง่าย",
                                 font=("Arial", 12),
                                 fg="#ecf0f1", bg="#2c3e50")
        subtitle_label.pack()
        
        # สร้าง Notebook สำหรับแท็บต่างๆ
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # แท็บที่ 1: การตั้งค่าไฟล์
        self.create_file_tab(notebook)
        
        # แท็บที่ 2: การตั้งค่าขั้นสูง
        self.create_advanced_tab(notebook)
        
        # แท็บที่ 3: ดูผลลัพธ์
        self.create_preview_tab(notebook)
        
        # ปุ่มสำหรับการดำเนินการ
        self.create_action_buttons()
        
    def create_file_tab(self, notebook):
        """สร้างแท็บสำหรับเลือกไฟล์"""
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="📁 เลือกไฟล์")
        
        # ส่วนเลือกภาพ
        image_section = ttk.LabelFrame(file_frame, text="🖼️ เลือกภาพพื้นหลัง", padding=15)
        image_section.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(image_section, text="ไฟล์ภาพ:").pack(anchor="w")
        image_frame = tk.Frame(image_section)
        image_frame.pack(fill="x", pady=5)
        
        ttk.Entry(image_frame, textvariable=self.image_path, width=60).pack(side="left", fill="x", expand=True)
        ttk.Button(image_frame, text="เลือก", command=self.select_image).pack(side="right", padx=(5,0))
        
        # ส่วนเลือกเสียง
        audio_section = ttk.LabelFrame(file_frame, text="🎵 เลือกไฟล์เสียง", padding=15)
        audio_section.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(audio_section, text="ไฟล์เสียง:").pack(anchor="w")
        audio_frame = tk.Frame(audio_section)
        audio_frame.pack(fill="x", pady=5)
        
        ttk.Entry(audio_frame, textvariable=self.audio_path, width=60).pack(side="left", fill="x", expand=True)
        ttk.Button(audio_frame, text="เลือก", command=self.select_audio).pack(side="right", padx=(5,0))
        
        # ส่วนเลือกโฟลเดอร์ผลลัพธ์
        output_section = ttk.LabelFrame(file_frame, text="📁 โฟลเดอร์ผลลัพธ์", padding=15)
        output_section.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(output_section, text="โฟลเดอร์ที่จะบันทึก:").pack(anchor="w")
        output_frame = tk.Frame(output_section)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=60).pack(side="left", fill="x", expand=True)
        ttk.Button(output_frame, text="เลือก", command=self.select_output).pack(side="right", padx=(5,0))
        
        # ส่วนตั้งค่าเวลา
        time_section = ttk.LabelFrame(file_frame, text="⏰ ความยาววิดีโอ", padding=15)
        time_section.pack(fill="x", padx=20, pady=10)
        
        time_frame = tk.Frame(time_section)
        time_frame.pack(fill="x")
        
        ttk.Label(time_frame, text="ความยาว (ชั่วโมง):").pack(side="left")
        ttk.Scale(time_frame, from_=0.5, to=12.0, variable=self.duration_hours, 
                 orient="horizontal", length=200).pack(side="left", padx=10)
        duration_label = ttk.Label(time_frame, text="4.0 ชั่วโมง")
        duration_label.pack(side="left")
        
        # อัปเดตข้อความเมื่อเลื่อน scale
        def update_duration_label(*args):
            duration_label.config(text=f"{self.duration_hours.get():.1f} ชั่วโมง")
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
        
        ttk.Label(ratio_frame, text="เลือกอัตราส่วน:").pack(side="left")
        ratio_combo = ttk.Combobox(ratio_frame, textvariable=self.aspect_ratio, 
                                  values=["16:9", "4:3", "1:1", "21:9"], state="readonly", width=10)
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
                                       textvariable=self.crossfade_duration, width=10)
        crossfade_spinbox.pack(side="left", padx=10)
        ttk.Label(manual_frame, text="มิลลิวินาที").pack(side="left")
        
        # อธิบาย Crossfade
        info_frame = tk.Frame(crossfade_section)
        info_frame.pack(fill="x", pady=10)
        
        info_text = """💡 คำอธิบาย:
• Crossfade คือการผสมเสียงระหว่างจุดจบและจุดเริ่มต้นของลูปเพื่อให้ต่อเนื่องกัน
• ระบบอัตโนมัติจะวิเคราะห์เสียงเพื่อหาจุดที่เหมาะสมที่สุด
• การกำหนดเองเหมาะสำหรับเสียงที่มีรูปแบบเฉพาะ"""
        
        ttk.Label(info_frame, text=info_text, foreground="gray").pack(anchor="w")
        
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
                  command=self.update_preview).pack()
        
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
        self.status_label = tk.Label(action_frame, text="พร้อมใช้งาน", 
                                    font=("Arial", 10), fg="green", bg="#f0f0f0")
        self.status_label.pack(pady=5)
        
        # ปุ่มต่างๆ
        button_frame = tk.Frame(action_frame, bg="#f0f0f0")
        button_frame.pack()
        
        ttk.Button(button_frame, text="🔍 ตรวจสอบการตั้งค่า", 
                  command=self.validate_settings).pack(side="left", padx=5)
        
        self.start_button = ttk.Button(button_frame, text="🚀 เริ่มสร้างวิดีโอ", 
                                      command=self.start_processing)
        self.start_button.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="📁 เปิดโฟลเดอร์ผลลัพธ์", 
                  command=self.open_output_folder).pack(side="left", padx=5)
        
    def select_image(self):
        """เลือกไฟล์ภาพ"""
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์ภาพ",
            filetypes=[
                ("ไฟล์ภาพ", "*.jpg *.jpeg *.png *.bmp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Bitmap", "*.bmp"),
                ("ทั้งหมด", "*.*")
            ]
        )
        if file_path:
            self.image_path.set(file_path)
            self.update_status(f"เลือกภาพ: {os.path.basename(file_path)}")
            
    def select_audio(self):
        """เลือกไฟล์เสียง"""
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์เสียง",
            filetypes=[
                ("ไฟล์เสียง", "*.mp3 *.wav *.m4a *.flac"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav"),
                ("M4A", "*.m4a"),
                ("FLAC", "*.flac"),
                ("ทั้งหมด", "*.*")
            ]
        )
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
                self.update_status("เกิดข้อผิดพลาด ❌")
                messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถสร้างวิดีโอได้")
                
        except Exception as e:
            self.update_status(f"ข้อผิดพลาด: {str(e)} ❌")
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
            
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
        
        # ชื่อไฟล์ผลลัพธ์
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        self.output_video = os.path.join(output_folder, f"{base_name}_music_loop.mp4")
        
    def process(self):
        """ประมวลผลหลัก"""
        try:
            # ใช้ LullaboyLooper จาก app.py แต่ปรับแต่งการทำงาน
            if self.progress_callback:
                self.progress_callback(20, "กำลังโหลดไฟล์เสียง...")
                
            # สร้าง looper โดยใช้โฟลเดอร์ชั่วคราว
            temp_folder = os.path.join(self.output_folder, "temp")
            os.makedirs(temp_folder, exist_ok=True)
            
            # คัดลอกไฟล์ไปยังโฟลเดอร์ชั่วคราว
            import shutil
            base_name = os.path.splitext(os.path.basename(self.audio_file))[0]
            temp_audio = os.path.join(temp_folder, f"{base_name}.mp3")
            temp_image = os.path.join(temp_folder, f"{base_name}.jpg")
            
            shutil.copy2(self.audio_file, temp_audio)
            shutil.copy2(self.image_file, temp_image)
            
            # สร้าง looper
            target_duration_ms = int(self.duration_hours * 60 * 60 * 1000)
            crossfade_ms = self.crossfade_duration if not self.auto_crossfade else 3000
            
            looper = LullaboyLooper(
                folder_path=temp_folder,
                crossfade_duration=crossfade_ms,
                remove_audio=not self.keep_original
            )
            
            # แก้ไข target duration
            looper.target_duration = target_duration_ms
            
            if self.progress_callback:
                self.progress_callback(40, "กำลังประมวลผลเสียง...")
                
            # ประมวลผล
            looper.process()
            
            if self.progress_callback:
                self.progress_callback(80, "กำลังจัดระเบียบไฟล์...")
                
            # ย้ายไฟล์ผลลัพธ์
            temp_output = os.path.join(temp_folder, f"{base_name}.mp4")
            if os.path.exists(temp_output):
                shutil.move(temp_output, self.output_video)
                
            # ลบโฟลเดอร์ชั่วคราว
            shutil.rmtree(temp_folder, ignore_errors=True)
            
            if self.progress_callback:
                self.progress_callback(100, "เสร็จสิ้น!")
                
            return True
            
        except Exception as e:
            print(f"Error in CustomImageMusicLooper: {e}")
            return False


def main():
    """ฟังก์ชันหลัก"""
    root = tk.Tk()
    app = ImageMusicLooperUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
