import tkinter as tk
from tkinter import messagebox
import threading
import queue
import time
import json
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import os
import platform


class VoiceSubtitleApp:
    def __init__(self, root):
        self.root = root
        self.select_language_mode()
        if not hasattr(self, 'language_mode'):
            self.root.destroy()
            return
            
        self.setup_window()
        self.initialize_variables()
        self.setup_ui()
        self.initialize_model()
        
    def select_language_mode(self):
        """Select language mode"""
        try:
            print("Creating language selection window...")  # Debug info
            
            # Create selection window
            select_window = tk.Toplevel(self.root)
            select_window.title("Select Language Mode | 选择语言模式")
            select_window.geometry("600x400")
            
            # Center the window on the screen
            screen_width = select_window.winfo_screenwidth()
            screen_height = select_window.winfo_screenheight()
            x = (screen_width - 600) // 2
            y = (screen_height - 400) // 2
            select_window.geometry(f"600x400+{x}+{y}")
            
            # Ensure the window is on top
            select_window.lift()
            select_window.focus_force()
            
            print("Setting up language selection buttons...")  # Debug info
            
            label = tk.Label(select_window, 
                            text="Please select language mode\n请选择语言模式",
                            font=("Arial", 14))
            label.pack(pady=20)
            
            def set_mode(mode):
                print(f"Language mode selected: {mode}")  # Debug info
                self.language_mode = mode
                select_window.destroy()
            
            # Add buttons
            tk.Button(select_window, 
                     text="Chinese Mode | 中文模式",
                     command=lambda: set_mode('zh'),
                     font=("Arial", 12)).pack(pady=5)
                     
            tk.Button(select_window, 
                     text="English Mode | 英文模式",
                     command=lambda: set_mode('en'),
                     font=("Arial", 12)).pack(pady=5)
                     
            tk.Button(select_window, 
                     text="Bilingual Mode | 双语模式",
                     command=lambda: set_mode('mix'),
                     font=("Arial", 12)).pack(pady=5)
            
            print("Language selection window created")  # Debug info
            
            # Wait for the window to close
            self.root.wait_window(select_window)
            print("Language selection completed")  # Debug info
            
        except Exception as e:
            print(f"Error in language selection: {str(e)}")  # Debug info

    def setup_window(self):
        """Set up the main window"""
        title_map = {
            'zh': "Real-time Speech Subtitles",
            'en': "Real-time Speech Subtitles",
            'mix': "CN-EN Real-time Subtitles | 中英文实时语音字幕"
        }
        self.root.title(title_map[self.language_mode])

        # Set window properties
        if platform.system() == 'Darwin':  # macOS
            self.root.attributes('-topmost', 1)
            self.root.attributes('-alpha', 1.0)
            self.root.attributes('-transparent', True)
            self.root.configure(bg='black')
            self.root.wm_attributes('-transparent', True)
            self.root.update_idletasks()
            self.root.lift()
        else:  # Windows and other systems
            self.root.attributes('-topmost', True)
            self.root.attributes('-alpha', 1.0)
            self.root.configure(bg='black')

        self.root.overrideredirect(True)

        # Set window size and position
        self.window_width = 800
        self.window_height = 100
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = screen_height - self.window_height - 100
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def initialize_variables(self):
        """Initialize variables"""
        self.start_time = time.time()
        self.word_count = 0
        self.recognition_results = []
        self.is_running = True
        self.audio_queue = queue.Queue()
        self.partial_result = ""
        self.last_voice_time = time.time()
        
        # Use the results folder in the parent directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.results_dir = os.path.join(current_dir, "..", "results")
        print(f"Using results directory at: {os.path.abspath(self.results_dir)}")
        
        # Create output files
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        mode_suffix = {'zh': 'cn', 'en': 'en', 'mix': 'mix'}[self.language_mode]
        self.output_file = os.path.join(self.results_dir, f"recognition_{mode_suffix}_{timestamp}.txt")
        self.output_md = os.path.join(self.results_dir, f"recognition_{mode_suffix}_{timestamp}.md")

    def setup_ui(self):
        """Set up the user interface"""
        # Create text label
        self.text_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 24, "bold"),
            fg="white",
            bg='black',
            wraplength=780,
            highlightthickness=0,
            borderwidth=0
        )
        self.text_label.pack(expand=True, fill='both', padx=10)

        # Add hint label
        hint_text = {
            'zh': "Listening...",
            'en': "Listening...",
            'mix': "Listening... | 正在听..."
        }[self.language_mode]
        
        self.hint_label = tk.Label(
            self.root,
            text=hint_text,
            font=("Arial", 12),
            fg="#00FF00",
            bg='black',
            wraplength=780,
            highlightthickness=0,
            borderwidth=0
        )
        self.hint_label.pack(side='bottom', pady=5)

        # Add language switch button for bilingual mode
        if self.language_mode == 'mix':
            self.current_language = 'zh'  # Default to Chinese
            self.lang_button = tk.Button(
                self.root,
                text="Switch Language/切换语言",
                command=self.switch_language,
                bg='black',
                fg='white',
                activebackground='gray',
                activeforeground='white',
                bd=0
            )
            self.lang_button.pack(side='bottom', pady=5)

        # Add drag functionality
        self.text_label.bind('<Button-1>', self.start_move)
        self.text_label.bind('<B1-Motion>', self.on_move)
        self.text_label.bind('<Button-3>', lambda e: self.on_closing())

    def initialize_model(self):
        """Initialize speech recognition model"""
        try:
            print("\nLoading speech recognition model...")
            loading_window = tk.Toplevel(self.root)
            loading_window.title("Loading")
            loading_window.geometry("300x100")
            loading_window.transient(self.root)
            
            loading_label = tk.Label(
                loading_window, 
                text="Loading speech model, please wait...",
                font=("Arial", 12)
            )
            loading_label.pack(pady=20)
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            if self.language_mode == 'zh':
                model_path = os.path.join(current_dir, "..", "vosk-model-cn-0.22")
                print(f"Loading Chinese model from: {os.path.abspath(model_path)}")
                if not os.path.exists(model_path):
                    raise Exception(f"Chinese model not found at: {os.path.abspath(model_path)}")
                loading_label.config(text="Loading Chinese model...")
                self.model = Model(model_path)
                self.recognizer = KaldiRecognizer(self.model, 16000)
            elif self.language_mode == 'en':
                model_path = os.path.join(current_dir, "..", "vosk-model-en-us-0.22")
                print(f"Loading English model from: {os.path.abspath(model_path)}")
                if not os.path.exists(model_path):
                    raise Exception(f"English model not found at: {os.path.abspath(model_path)}")
                loading_label.config(text="Loading English model...")
                self.model = Model(model_path)
                self.recognizer = KaldiRecognizer(self.model, 16000)
            else:  # Bilingual mode
                self.cn_model_path = os.path.join(current_dir, "..", "vosk-model-cn-0.22")
                self.en_model_path = os.path.join(current_dir, "..", "vosk-model-en-us-0.22")
                
                print(f"Loading Chinese model from: {os.path.abspath(self.cn_model_path)}")
                print(f"Loading English model from: {os.path.abspath(self.en_model_path)}")
                
                if not os.path.exists(self.cn_model_path):
                    raise Exception(f"Chinese model not found at: {os.path.abspath(self.cn_model_path)}")
                if not os.path.exists(self.en_model_path):
                    raise Exception(f"English model not found at: {os.path.abspath(self.en_model_path)}")
                
                loading_label.config(text="Loading Chinese model...")
                self.cn_model = Model(self.cn_model_path)
                
                loading_label.config(text="Loading English model...")
                self.en_model = Model(self.en_model_path)
                
                self.recognizer = KaldiRecognizer(self.cn_model, 16000)

            if not hasattr(self, 'recognizer'):
                raise Exception(f"Failed to initialize recognizer")

            self.recognizer.SetMaxAlternatives(0)
            self.recognizer.SetWords(True)
            
            loading_label.config(text="Model loaded successfully!")
            loading_window.after(1000, loading_window.destroy)
            
            print("Model loaded successfully")

            print("Starting audio thread...")
            self.audio_thread = threading.Thread(target=self.process_audio)
            self.audio_thread.daemon = True
            self.audio_thread.start()

            print("Starting recognition thread...")
            self.recognition_thread = threading.Thread(target=self.recognize_speech)
            self.recognition_thread.daemon = True
            self.recognition_thread.start()

        except Exception as e:
            error_msg = f"Initialization error: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            self.root.destroy()

    def switch_language(self):
        """Switch recognition language (only for bilingual mode)"""
        if not hasattr(self, 'current_language'):
            return
            
        if self.current_language == 'zh':
            self.current_language = 'en'
            self.recognizer = KaldiRecognizer(self.en_model, 16000)
            self.hint_label.config(text="Current: English")
        else:
            self.current_language = 'zh'
            self.recognizer = KaldiRecognizer(self.cn_model, 16000)
            self.hint_label.config(text="Current: Chinese")
        
        self.recognizer.SetMaxAlternatives(0)
        self.recognizer.SetWords(True)

    def start_move(self, event):
        """Start moving the window"""
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        """Handle window movement"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def audio_callback(self, indata, frames, time, status):
        """Audio callback function"""
        if status:
            print(status)
        self.audio_queue.put(bytes(indata))

    def process_audio(self):
        """Process audio input"""
        try:
            with sd.RawInputStream(samplerate=16000, channels=1, dtype='int16',
                                   blocksize=4000,
                                   device=None,
                                   callback=self.audio_callback):
                print("Starting recording...")
                while self.is_running:
                    time.sleep(0.05)
                    self.root.after(0, self.fade_out_text)
        except Exception as e:
            print(f"Audio processing error: {str(e)}")
            self.root.after(0, self.update_subtitle, f"Audio processing error: {str(e)}")

    def recognize_speech(self):
        """Speech recognition processing"""
        print("\n=== Starting Speech Recognition ===")
        print("Listening for voice input...\n")

        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=0.5)
                if len(audio_data) == 0:
                    continue

                if self.recognizer.AcceptWaveform(audio_data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        current_time = time.strftime('%H:%M:%S')
                        print(f"[{current_time}] {text}")
                        
                        self.recognition_results.append({
                            'time': current_time,
                            'text': text
                        })
                        
                        self.last_voice_time = time.time()
                        self.root.after(0, self.update_subtitle, text)
                        self.save_results()
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get("partial", "").strip()
                    if partial_text and partial_text != self.partial_result:
                        self.partial_result = partial_text
                        self.last_voice_time = time.time()
                        self.root.after(0, self.update_subtitle, f"{partial_text}...")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Recognition error: {str(e)}")
                time.sleep(0.1)

    def save_results(self):
        """Save recognition results to files"""
        try:
            duration = time.time() - self.start_time
            
            # Save TXT file
            content = f"""Speech Recognition Record

Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}
Duration: {duration:.2f} seconds
Total Words: {self.word_count}
Average Speed: {self.word_count/duration:.2f} words/second

Recognition Content:
"""
            for result in self.recognition_results:
                content += f"[{result['time']}] {result['text']}\n"

            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Save Markdown file
            md_content = f"""# Speech Recognition Record

## Basic Information

- **Start Time**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}
- **Duration**: {duration:.2f} seconds
- **Total Words**: {self.word_count}
- **Average Speed**: {self.word_count/duration:.2f} words/second

## Recognition Content

| Time | Content |
|------|---------|
"""
            for result in self.recognition_results:
                md_content += f"| {result['time']} | {result['text']} |\n"

            with open(self.output_md, 'w', encoding='utf-8') as f:
                f.write(md_content)

        except Exception as e:
            print(f"Error saving results: {str(e)}")

    def fade_out_text(self):
        """Text fade-out effect"""
        try:
            if time.time() - self.last_voice_time > 3:  # Start fading after 3 seconds of no input
                current_color = self.text_label.cget('fg')
                if current_color == 'white':  # If fully opaque
                    self.text_label.configure(fg='#FFFFFF')  # Set initial color
                else:
                    # Extract current color value
                    color = current_color.lstrip('#')
                    if len(color) == 6:  # Ensure valid color value
                        # Reduce opacity
                        new_alpha = max(0, int(color[0:2], 16) - 15)
                        if new_alpha > 0:  # If not fully transparent yet
                            new_color = f'#{new_alpha:02x}{new_alpha:02x}{new_alpha:02x}'
                            self.text_label.configure(fg=new_color)
                            self.root.after(50, self.fade_out_text)  # Continue fading
                        else:
                            # Clear text when fully transparent
                            self.text_label.config(text="")
                            self.text_label.update()
        except Exception as e:
            print(f"Fade-out effect error: {str(e)}")

    def update_subtitle(self, text):
        """Update subtitle text"""
        if not text:
            return
        self.text_label.config(text=text)
        self.text_label.configure(fg='white')
        self.text_label.update()
        self.last_voice_time = time.time()
        
        # Update word count
        self.word_count += len(text)

    def on_closing(self):
        self.is_running = False
        self.root.destroy()


if __name__ == "__main__":
    try:
        print("Starting application...")
        root = tk.Tk()
        print("Root window created")
        
        # Set initial position of the root window (center of the screen)
        root.geometry("1x1+{}+{}".format(
            root.winfo_screenwidth()//2,
            root.winfo_screenheight()//2
        ))
        
        root.withdraw()
        print("Root window hidden")
        
        # Ensure the root window is ready
        root.update()
        
        print("Initializing VoiceSubtitleApp...")
        app = VoiceSubtitleApp(root)
        print("VoiceSubtitleApp initialized")
        
        if hasattr(app, 'language_mode'):
            root.deiconify()
            print("Root window shown")
            print("Starting main event loop...")
            root.mainloop()
        else:
            print("No language mode selected, closing application...")
            root.destroy()
            
    except Exception as e:
        print(f"Error in main: {str(e)}")