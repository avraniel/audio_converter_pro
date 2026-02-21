#!/usr/bin/env python3
"""
Audio Converter Pro - Complete Audio Conversion Tool
Convert between all major audio formats with advanced features
"""

import sys
import os
from pathlib import Path

# ========== AUTO-DEPENDENCY INSTALLATION ==========

REQUIRED_PACKAGES = [
    'customtkinter>=5.2.2',
    'pillow>=10.2.0',
    'mutagen>=1.47.0',
]

def check_and_install_dependencies():
    """Check if all dependencies are installed, install if missing"""
    print("🔍 Checking dependencies...")
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        package_name = package.split('>=')[0] if '>=' in package else package
        if not is_package_installed(package_name):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", package])
                print(f"✅ Installed: {package}")
            except:
                print(f"⚠️ Failed to install {package}")
    
    check_ffmpeg()

def is_package_installed(package_name):
    """Check if a package is installed"""
    return importlib.util.find_spec(package_name) is not None

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg found")
        return True
    except:
        print("⚠️ FFmpeg not found - conversion will be limited")
        return False

# Run dependency check
import subprocess
import importlib.util
check_and_install_dependencies()

# ========== IMPORTS ==========
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import subprocess
import shutil
from pathlib import Path
import time
from datetime import datetime
import json
import pickle
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.id3 import ID3, TIT2, TPE1, TALB
import webbrowser

# ========== THEME CONFIGURATION ==========

class ThemeManager:
    """Manages application themes and colors"""
    
    THEMES = {
        "dark": {
            "name": "Dark",
            "ctk_theme": "dark",
            "colors": {
                'primary': '#FF4444',
                'primary_hover': '#FF6666',
                'secondary': '#3EA6FF',
                'secondary_hover': '#5FB4FF',
                'success': '#4CAF50',
                'success_hover': '#66BB6A',
                'warning': '#FFC107',
                'warning_hover': '#FFCA28',
                'error': '#F44336',
                'error_hover': '#EF5350',
                'surface': '#1E1E1E',
                'surface_light': '#2D2D2D',
                'surface_dark': '#121212',
                'text': '#FFFFFF',
                'text_secondary': '#AAAAAA',
                'border': '#333333',
                'card': '#252525',
                'input_bg': '#333333',
                'input_fg': '#FFFFFF',
                'disabled': '#666666',
            }
        },
        "light": {
            "name": "Light",
            "ctk_theme": "light",
            "colors": {
                'primary': '#FF4444',
                'primary_hover': '#FF6666',
                'secondary': '#3EA6FF',
                'secondary_hover': '#5FB4FF',
                'success': '#4CAF50',
                'success_hover': '#66BB6A',
                'warning': '#FFC107',
                'warning_hover': '#FFCA28',
                'error': '#F44336',
                'error_hover': '#EF5350',
                'surface': '#F5F5F5',
                'surface_light': '#FFFFFF',
                'surface_dark': '#E0E0E0',
                'text': '#000000',
                'text_secondary': '#666666',
                'border': '#CCCCCC',
                'card': '#FFFFFF',
                'input_bg': '#FFFFFF',
                'input_fg': '#000000',
                'disabled': '#999999',
            }
        },
        "system": {
            "name": "System",
            "ctk_theme": "system",
            "colors": {}  # Will be determined at runtime
        }
    }
    
    FORMAT_COLORS = {
        'mp3': '#FF4444',
        'flac': '#9C27B0',
        'ogg': '#00BCD4',
        'wav': '#FF9800',
        'm4a': '#795548',
        'opus': '#607D8B'
    }
    
    def __init__(self):
        self.current_theme = "dark"
        self.colors = self.THEMES["dark"]["colors"].copy()
    
    def get_theme_colors(self, theme_name=None):
        """Get colors for specified theme"""
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name == "system":
            # Detect system theme
            import platform
            if platform.system() == "Darwin":  # macOS
                # Try to detect macOS dark mode
                try:
                    result = subprocess.run(
                        ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                        capture_output=True, text=True
                    )
                    is_dark = result.returncode == 0 and "Dark" in result.stdout
                except:
                    is_dark = False
            elif platform.system() == "Windows":
                # Try to detect Windows dark mode
                try:
                    import winreg
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                    )
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    is_dark = value == 0
                except:
                    is_dark = False
            else:  # Linux
                # Default to dark on Linux
                is_dark = True
            
            theme_name = "dark" if is_dark else "light"
        
        return self.THEMES[theme_name]["colors"].copy()
    
    def apply_theme(self, theme_name, app_instance):
        """Apply theme to application"""
        self.current_theme = theme_name
        self.colors = self.get_theme_colors(theme_name)
        
        # Set CTk theme
        ctk.set_appearance_mode(self.THEMES[theme_name]["ctk_theme"])
        
        # Update app colors
        app_instance.colors = self.colors
        
        # Force UI update
        app_instance.update_theme()
    
    def get_format_color(self, format_name):
        """Get color for specific format"""
        return self.FORMAT_COLORS.get(format_name, self.colors['secondary'])


# ========== CONFIGURATION ==========

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_NAME = "Audio Converter Pro"
APP_VERSION = "2.0"

class AudioConverterPro(ctk.CTk):
    """Complete Audio Converter Application with All Features"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title(f"🎵 {APP_NAME} v{APP_VERSION}")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.colors
        
        # Core variables
        self.input_files = []
        self.output_folder = str(Path.home() / "Downloads" / "Converted Audio")
        self.conversion_history = []
        self.quality_warnings = []
        self.is_converting = False
        self.total_files = 0
        self.completed_files = 0
        self.failed_files = []
        self.batch_queue = []
        self.recent_files = []
        self.ogg_optimization = True
        self.preserve_tags = True
        self.normalize = False
        self.ffmpeg_available = check_ffmpeg()
        
        # Format support
        self.input_formats = {
            'Video': ['mp4', 'mkv', 'avi', 'mov', 'webm', 'flv', 'wmv', 'mpg', 'm4v'],
            'Audio': ['mp3', 'flac', 'wav', 'ogg', 'm4a', 'aac', 'opus', 'ac3', 'dts'],
            'Lossless': ['flac', 'wav', 'aiff', 'ape', 'wv'],
        }
        
        self.output_formats = {
            'MP3 (Compressed)': {
                'format': 'mp3',
                'bitrates': ['128k', '192k', '256k', '320k', 'V0', 'V2'],
                'color': '#FF4444'
            },
            'FLAC (Lossless)': {
                'format': 'flac',
                'compression': ['0 (Fastest)', '5 (Default)', '8 (Best)'],
                'color': '#9C27B0'
            },
            'OGG Vorbis': {
                'format': 'ogg',
                'quality': ['-1 (Lowest)', '0', '3', '5', '7', '10 (Highest)'],
                'color': '#00BCD4'
            },
            'WAV (Uncompressed)': {
                'format': 'wav',
                'options': ['16-bit PCM', '24-bit PCM', '32-bit PCM'],
                'color': '#FF9800'
            },
            'AAC (Apple)': {
                'format': 'm4a',
                'bitrates': ['128k', '192k', '256k', '320k'],
                'color': '#795548'
            },
            'Opus (Modern)': {
                'format': 'opus',
                'bitrates': ['64k', '96k', '128k', '160k', '192k'],
                'color': '#607D8B'
            }
        }
        
        # Presets
        self.presets = {
            "Podcast": {
                "format": "mp3",
                "options": {"bitrate": "128k", "stereo": "Mono"},
                "icon": "🎙️"
            },
            "High Quality Music": {
                "format": "flac",
                "options": {"compression": "8", "metadata": True},
                "icon": "🎵"
            },
            "Mobile Device": {
                "format": "aac",
                "options": {"bitrate": "128k"},
                "icon": "📱"
            },
            "Archive": {
                "format": "wav",
                "options": {"bitdepth": "24-bit PCM"},
                "icon": "💾"
            },
            "OGG → MP3 (High)": {
                "format": "mp3",
                "options": {"bitrate": "256k", "optimize_ogg": True},
                "icon": "🔄"
            }
        }
        
        # UI Elements dictionary for theme updates
        self.ui_elements = {
            'headers': [],
            'cards': [],
            'buttons': [],
            'labels': [],
            'frames': [],
            'format_buttons': {}
        }
        
        # Create output folder
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Build UI
        self.setup_ui()
        
        # Load history
        self.load_history()
        self.load_theme_preference()
        
        # Setup shortcuts
        self.setup_shortcuts()
        
        # Try to add drag-drop
        self.try_add_drag_drop()

    # ========== THEME MANAGEMENT ==========

    def load_theme_preference(self):
        """Load saved theme preference"""
        try:
            config_file = Path.home() / '.audio_converter_config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    theme = config.get('theme', 'dark')
                    self.theme_manager.apply_theme(theme, self)
        except:
            pass

    def save_theme_preference(self, theme):
        """Save theme preference"""
        try:
            config_file = Path.home() / '.audio_converter_config.json'
            config = {}
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
            config['theme'] = theme
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass

    def change_theme(self, theme_name):
        """Change application theme"""
        self.theme_manager.apply_theme(theme_name, self)
        self.save_theme_preference(theme_name)

    def update_theme(self):
        """Update all UI elements with new theme colors"""
        # Update headers
        for widget in self.ui_elements['headers']:
            if widget.winfo_exists():
                widget.configure(text_color=self.colors['text'])
        
        # Update cards
        for widget in self.ui_elements['cards']:
            if widget.winfo_exists():
                widget.configure(fg_color=self.colors['card'])
        
        # Update buttons (excluding format buttons which have their own colors)
        for widget in self.ui_elements['buttons']:
            if widget.winfo_exists() and widget not in self.ui_elements['format_buttons'].values():
                current_fg = widget.cget('fg_color')
                # Only update if it's using theme colors (not format colors)
                if current_fg in ['#FF4444', '#3EA6FF', '#4CAF50', '#FFC107', '#F44336']:
                    widget.configure(
                        fg_color=self.colors['primary'],
                        hover_color=self.colors['primary_hover']
                    )
        
        # Update labels
        for widget in self.ui_elements['labels']:
            if widget.winfo_exists():
                current_color = widget.cget('text_color')
                if current_color not in ['#FF4444', '#9C27B0', '#00BCD4', '#FF9800', '#795548', '#607D8B']:
                    widget.configure(text_color=self.colors['text'])
        
        # Update frames
        for widget in self.ui_elements['frames']:
            if widget.winfo_exists():
                current_fg = widget.cget('fg_color')
                if current_fg in ['#1E1E1E', '#2D2D2D', '#121212', '#F5F5F5', '#FFFFFF', '#E0E0E0']:
                    widget.configure(fg_color=self.colors['surface'])
        
        # Update status bar
        if hasattr(self, 'status_label'):
            self.status_label.configure(text_color=self.colors['text_secondary'])
        
        if hasattr(self, 'file_count_label'):
            self.file_count_label.configure(text_color=self.colors['text_secondary'])
        
        # Update info text
        if hasattr(self, 'info_text'):
            self.info_text.configure(
                fg_color=self.colors['input_bg'],
                text_color=self.colors['text']
            )
        
        # Update progress label
        if hasattr(self, 'progress_label'):
            self.progress_label.configure(text_color=self.colors['text_secondary'])
        
        # Update format buttons (keep their specific colors)
        for fmt, btn in self.ui_elements['format_buttons'].items():
            if btn.winfo_exists():
                color = self.theme_manager.get_format_color(fmt)
                if self.output_format_var.get() == fmt:
                    btn.configure(fg_color=color)
                else:
                    btn.configure(fg_color=self.colors['surface_light'])

    # ========== UI SETUP ==========

    def setup_ui(self):
        """Build the complete interface"""
        self.create_header()
        self.create_main_content()
        self.create_status_bar()

    def create_header(self):
        """Create app header with presets and theme selector"""
        header = ctk.CTkFrame(self, height=120, fg_color=self.colors['surface'])
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 0))
        header.grid_columnconfigure(1, weight=1)
        self.ui_elements['frames'].append(header)
        
        # Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.ui_elements['frames'].append(title_frame)
        
        title_icon = ctk.CTkLabel(
            title_frame,
            text="🎵",
            font=ctk.CTkFont(size=32)
        )
        title_icon.pack(side="left", padx=(0, 10))
        self.ui_elements['labels'].append(title_icon)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.pack(side="left")
        self.ui_elements['labels'].append(title_label)
        self.ui_elements['headers'].append(title_label)
        
        version_label = ctk.CTkLabel(
            title_frame,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['surface_light'],
            corner_radius=10,
            padx=8,
            pady=2,
            text_color=self.colors['text_secondary']
        )
        version_label.pack(side="left", padx=10)
        self.ui_elements['labels'].append(version_label)
        
        # Theme selector
        theme_frame = ctk.CTkFrame(header, fg_color="transparent")
        theme_frame.grid(row=0, column=1, padx=10)
        self.ui_elements['frames'].append(theme_frame)
        
        ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        ).pack(side="left", padx=5)
        
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=lambda t: self.change_theme(t.lower()),
            width=100,
            fg_color=self.colors['surface_light'],
            button_color=self.colors['secondary'],
            button_hover_color=self.colors['secondary_hover'],
            text_color=self.colors['text']
        )
        theme_menu.pack(side="left", padx=5)
        theme_menu.set(self.theme_manager.current_theme.capitalize())
        self.ui_elements['buttons'].append(theme_menu)
        
        # Presets
        preset_frame = ctk.CTkFrame(header, fg_color="transparent")
        preset_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.ui_elements['frames'].append(preset_frame)
        
        ctk.CTkLabel(
            preset_frame,
            text="Presets:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text']
        ).pack(side="left", padx=5)
        
        for name, preset in self.presets.items():
            btn = ctk.CTkButton(
                preset_frame,
                text=f"{preset['icon']} {name}",
                width=100,
                height=30,
                font=ctk.CTkFont(size=10),
                fg_color=self.colors['surface_light'],
                hover_color=self.colors['secondary'],
                text_color=self.colors['text'],
                command=lambda p=preset: self.apply_preset(p)
            )
            btn.pack(side="left", padx=2)
            self.ui_elements['buttons'].append(btn)
        
        # FFmpeg status
        self.ffmpeg_status = ctk.CTkLabel(
            header,
            text="🎵 FFmpeg: ✓ Ready" if self.ffmpeg_available else "🎵 FFmpeg: ⚠️ Not Found",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['success'] if self.ffmpeg_available else self.colors['warning'],
            corner_radius=10,
            padx=10,
            text_color='#000000'  # Always dark text on colored background
        )
        self.ffmpeg_status.place(relx=0.98, rely=0.15, anchor="ne")

    def create_main_content(self):
        """Create main content area with tabs and info panel"""
        # Left side - Tabs
        self.main_tabview = ctk.CTkTabview(self, fg_color=self.colors['surface'])
        self.main_tabview.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        self.ui_elements['frames'].append(self.main_tabview)
        
        # Configure tab colors
        self.main_tabview.configure(
            segmented_button_fg_color=self.colors['surface_light'],
            segmented_button_selected_color=self.colors['primary'],
            segmented_button_selected_hover_color=self.colors['primary_hover'],
            text_color=self.colors['text']
        )
        
        self.main_tabview.add("🔄 Converter")
        self.main_tabview.add("📋 Batch")
        self.main_tabview.add("📊 History")
        self.main_tabview.add("⚙️ Settings")
        
        self.setup_converter_tab()
        self.setup_batch_tab()
        self.setup_history_tab()
        self.setup_settings_tab()
        
        # Right side - Info Panel
        self.setup_info_panel()

    def setup_converter_tab(self):
        """Setup the main converter tab"""
        tab = self.main_tabview.tab("🔄 Converter")
        tab.grid_columnconfigure(0, weight=1)
        self.ui_elements['frames'].append(tab)
        
        # Input section
        input_card = ctk.CTkFrame(tab, fg_color=self.colors['card'])
        input_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.ui_elements['cards'].append(input_card)
        
        input_label = ctk.CTkLabel(
            input_card,
            text="📂 Input Files",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text']
        )
        input_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.ui_elements['labels'].append(input_label)
        
        # File list
        self.file_list_frame = ctk.CTkScrollableFrame(input_card, height=150, fg_color="transparent")
        self.file_list_frame.pack(fill="x", padx=15, pady=5)
        self.ui_elements['frames'].append(self.file_list_frame)
        
        # Buttons
        btn_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)
        self.ui_elements['frames'].append(btn_frame)
        
        add_files_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Add Files",
            command=self.add_files,
            width=120,
            fg_color=self.colors['secondary'],
            hover_color=self.colors['secondary_hover'],
            text_color='#000000'
        )
        add_files_btn.pack(side="left", padx=5)
        self.ui_elements['buttons'].append(add_files_btn)
        
        add_folder_btn = ctk.CTkButton(
            btn_frame,
            text="📁 Add Folder",
            command=self.add_folder,
            width=120,
            fg_color=self.colors['secondary'],
            hover_color=self.colors['secondary_hover'],
            text_color='#000000'
        )
        add_folder_btn.pack(side="left", padx=5)
        self.ui_elements['buttons'].append(add_folder_btn)
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear All",
            command=self.clear_files,
            width=100,
            fg_color=self.colors['error'],
            hover_color=self.colors['error_hover'],
            text_color='#000000'
        )
        clear_btn.pack(side="right", padx=5)
        self.ui_elements['buttons'].append(clear_btn)
        
        # Format selection
        format_card = ctk.CTkFrame(tab, fg_color=self.colors['card'])
        format_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.ui_elements['cards'].append(format_card)
        
        format_label = ctk.CTkLabel(
            format_card,
            text="⚙️ Output Format",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text']
        )
        format_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.ui_elements['labels'].append(format_label)
        
        format_frame = ctk.CTkFrame(format_card, fg_color="transparent")
        format_frame.pack(fill="x", padx=15, pady=5)
        self.ui_elements['frames'].append(format_frame)
        
        # Format selection buttons
        self.output_format_var = ctk.StringVar(value="mp3")
        self.format_buttons = {}
        
        for i, (name, info) in enumerate(self.output_formats.items()):
            color = info['color']
            btn = ctk.CTkButton(
                format_frame,
                text=name,
                width=130,
                height=40,
                fg_color=self.colors['surface_light'] if self.output_format_var.get() != info['format'] else color,
                hover_color=color,
                text_color='#000000',
                command=lambda f=info['format'], c=color: self.select_output_format(f, c)
            )
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.format_buttons[info['format']] = btn
            self.ui_elements['buttons'].append(btn)
            self.ui_elements['format_buttons'][info['format']] = btn
        
        # Format-specific options
        self.options_frame = ctk.CTkFrame(format_card, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=15, pady=10)
        self.ui_elements['frames'].append(self.options_frame)
        
        self.create_format_options()
        
        # MP3 source options
        self.mp3_options_frame = ctk.CTkFrame(format_card, fg_color="transparent")
        self.mp3_options_frame.pack(fill="x", padx=15, pady=5)
        self.ui_elements['frames'].append(self.mp3_options_frame)
        self.create_mp3_options()
        
        # Output folder
        output_card = ctk.CTkFrame(tab, fg_color=self.colors['card'])
        output_card.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.ui_elements['cards'].append(output_card)
        
        output_label = ctk.CTkLabel(
            output_card,
            text="💾 Output Folder",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text']
        )
        output_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.ui_elements['labels'].append(output_label)
        
        out_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        out_frame.pack(fill="x", padx=15, pady=10)
        self.ui_elements['frames'].append(out_frame)
        
        self.output_folder_var = ctk.StringVar(value=self.output_folder)
        out_entry = ctk.CTkEntry(
            out_frame,
            textvariable=self.output_folder_var,
            height=35,
            fg_color=self.colors['input_bg'],
            text_color=self.colors['text'],
            border_color=self.colors['border']
        )
        out_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            out_frame,
            text="Browse",
            width=100,
            command=self.browse_output,
            fg_color=self.colors['secondary'],
            hover_color=self.colors['secondary_hover'],
            text_color='#000000'
        )
        browse_btn.pack(side="right")
        self.ui_elements['buttons'].append(browse_btn)
        
        # Convert and Cancel buttons
        button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", pady=10)
        button_frame.grid_columnconfigure(0, weight=3)
        button_frame.grid_columnconfigure(1, weight=1)
        self.ui_elements['frames'].append(button_frame)
        
        self.convert_btn = ctk.CTkButton(
            button_frame,
            text="🎵 START CONVERSION",
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.start_conversion,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            text_color='#000000'
        )
        self.convert_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.ui_elements['buttons'].append(self.convert_btn)
        
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="⏹️ Cancel",
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.cancel_conversion,
            fg_color=self.colors['error'],
            hover_color=self.colors['error_hover'],
            text_color='#000000',
            state="disabled"
        )
        self.cancel_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.ui_elements['buttons'].append(self.cancel_btn)
        
        # Progress
        self.progress_bar = ctk.CTkProgressBar(tab, height=15, progress_color=self.colors['primary'])
        self.progress_bar.grid(row=4, column=0, sticky="ew", pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            tab,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.progress_label.grid(row=5, column=0)

    def create_format_options(self):
        """Create format-specific options"""
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        current_format = self.output_format_var.get()
        
        if current_format == 'mp3':
            label = ctk.CTkLabel(
                self.options_frame,
                text="Bitrate:",
                text_color=self.colors['text']
            )
            label.pack(side="left", padx=5)
            self.ui_elements['labels'].append(label)
            
            self.mp3_bitrate = ctk.CTkOptionMenu(
                self.options_frame,
                values=['128k', '192k', '256k', '320k', 'V0', 'V2'],
                width=100,
                fg_color=self.colors['input_bg'],
                button_color=self.colors['secondary'],
                button_hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text']
            )
            self.mp3_bitrate.pack(side="left", padx=5)
            self.mp3_bitrate.set('192k')
            self.ui_elements['buttons'].append(self.mp3_bitrate)
            
            stereo_label = ctk.CTkLabel(
                self.options_frame,
                text="Stereo Mode:",
                text_color=self.colors['text']
            )
            stereo_label.pack(side="left", padx=(20, 5))
            self.ui_elements['labels'].append(stereo_label)
            
            self.mp3_stereo = ctk.CTkOptionMenu(
                self.options_frame,
                values=['Joint Stereo', 'Stereo', 'Mono'],
                width=100,
                fg_color=self.colors['input_bg'],
                button_color=self.colors['secondary'],
                button_hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text']
            )
            self.mp3_stereo.pack(side="left", padx=5)
            self.mp3_stereo.set('Joint Stereo')
            self.ui_elements['buttons'].append(self.mp3_stereo)
        
        elif current_format == 'flac':
            label = ctk.CTkLabel(
                self.options_frame,
                text="Compression:",
                text_color=self.colors['text']
            )
            label.pack(side="left", padx=5)
            self.ui_elements['labels'].append(label)
            
            self.flac_compression = ctk.CTkOptionMenu(
                self.options_frame,
                values=['0 (Fastest)', '5 (Default)', '8 (Best)'],
                width=120,
                fg_color=self.colors['input_bg'],
                button_color=self.colors['secondary'],
                button_hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text']
            )
            self.flac_compression.pack(side="left", padx=5)
            self.flac_compression.set('5 (Default)')
            self.ui_elements['buttons'].append(self.flac_compression)
            
            self.flac_meta = ctk.CTkCheckBox(
                self.options_frame,
                text="Copy Metadata",
                fg_color=self.colors['secondary'],
                hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text']
            )
            self.flac_meta.pack(side="left", padx=20)
            self.flac_meta.select()
        
        elif current_format == 'ogg':
            label = ctk.CTkLabel(
                self.options_frame,
                text="Quality:",
                text_color=self.colors['text']
            )
            label.pack(side="left", padx=5)
            self.ui_elements['labels'].append(label)
            
            self.ogg_quality = ctk.CTkOptionMenu(
                self.options_frame,
                values=['-1 (Lowest)', '0', '3', '5', '7', '10 (Highest)'],
                width=120,
                fg_color=self.colors['input_bg'],
                button_color=self.colors['secondary'],
                button_hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text']
            )
            self.ogg_quality.pack(side="left", padx=5)
            self.ogg_quality.set('5')
            self.ui_elements['buttons'].append(self.ogg_quality)
        
        elif current_format == 'wav':
            label = ctk.CTkLabel(
                self.options_frame,
                text="Bit Depth:",
                text_color=self.colors['text']
            )
            label.pack(side="left", padx=5)
            self.ui_elements['labels'].append(label)
            
            self.wav_depth = ctk.CTkOptionMenu(
                self.options_frame,
                values=['16-bit PCM', '24-bit PCM', '32-bit PCM'],
                width=120,
                fg_color=self.colors['input_bg'],
                button_color=self.colors['secondary'],
                button_hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text']
            )
            self.wav_depth.pack(side="left", padx=5)
            self.wav_depth.set('16-bit PCM')
            self.ui_elements['buttons'].append(self.wav_depth)
        
        elif current_format == 'm4a':
            label = ctk.CTkLabel(
                self.options_frame,
                text="Bitrate:",
                text_color=self.colors['text']
            )
            label.pack(side="left", padx=5)
            self.ui_elements['labels'].append(label)
            
            self.aac_bitrate = ctk.CTkOptionMenu(
                self.options_frame,
                values=['128k', '192k', '256k', '320k'],
                width=100,
                fg_color=self.colors['input_bg'],
                button_color=self.colors['secondary'],
                button_hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text']
            )
            self.aac_bitrate.pack(side="left", padx=5)
            self.aac_bitrate.set('192k')
            self.ui_elements['buttons'].append(self.aac_bitrate)
        
        elif current_format == 'opus':
            label = ctk.CTkLabel(
                self.options_frame,
                text="Bitrate:",
                text_color=self.colors['text']
            )
            label.pack(side="left", padx=5)
            self.ui_elements['labels'].append(label)
            
            self.opus_bitrate = ctk.CTkOptionMenu(
                self.options_frame,
                values=['64k', '96k', '128k', '160k', '192k'],
                width=100,
                fg_color=self.colors['input_bg'],
                button_color=self.colors['secondary'],
                button_hover_color=self.colors['secondary_hover'],
                text_color=self.colors['text']
            )
            self.opus_bitrate.pack(side="left", padx=5)
            self.opus_bitrate.set('128k')
            self.ui_elements['buttons'].append(self.opus_bitrate)

    def create_mp3_options(self):
        """Create MP3 source options"""
        for widget in self.mp3_options_frame.winfo_children():
            widget.destroy()
        
        self.ogg_optimize_cb = ctk.CTkCheckBox(
            self.mp3_options_frame,
            text="Optimize OGG to MP3",
            fg_color=self.colors['secondary'],
            hover_color=self.colors['secondary_hover'],
            text_color=self.colors['text'],
            command=lambda: setattr(self, 'ogg_optimization', self.ogg_optimize_cb.get() == 1)
        )
        self.ogg_optimize_cb.pack(side="left", padx=5)
        self.ogg_optimize_cb.select()
        
        self.preserve_tags_cb = ctk.CTkCheckBox(
            self.mp3_options_frame,
            text="Preserve Metadata",
            fg_color=self.colors['secondary'],
            hover_color=self.colors['secondary_hover'],
            text_color=self.colors['text'],
            command=lambda: setattr(self, 'preserve_tags', self.preserve_tags_cb.get() == 1)
        )
        self.preserve_tags_cb.pack(side="left", padx=20)
        self.preserve_tags_cb.select()
        
        self.normalize_cb = ctk.CTkCheckBox(
            self.mp3_options_frame,
            text="Normalize Volume",
            fg_color=self.colors['secondary'],
            hover_color=self.colors['secondary_hover'],
            text_color=self.colors['text'],
            command=lambda: setattr(self, 'normalize', self.normalize_cb.get() == 1)
        )
        self.normalize_cb.pack(side="left", padx=20)

    def setup_info_panel(self):
        """Setup file information panel"""
        info_frame = ctk.CTkFrame(self, fg_color=self.colors['card'])
        info_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        self.ui_elements['cards'].append(info_frame)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="📊 File Information",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text']
        )
        info_label.pack(padx=10, pady=10)
        self.ui_elements['labels'].append(info_label)
        
        self.info_text = ctk.CTkTextbox(
            info_frame,
            width=250,
            height=500,
            wrap="word",
            fg_color=self.colors['input_bg'],
            text_color=self.colors['text'],
            border_color=self.colors['border']
        )
        self.info_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Initial message
        self.info_text.insert("1.0", "Select files to view information")

    def setup_batch_tab(self):
        """Setup batch conversion tab"""
        tab = self.main_tabview.tab("📋 Batch")
        
        # Queue controls
        control_frame = ctk.CTkFrame(tab, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=10)
        self.ui_elements['frames'].append(control_frame)
        
        queue_label = ctk.CTkLabel(
            control_frame,
            text="Batch Queue",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['text']
        )
        queue_label.pack(side="left")
        self.ui_elements['labels'].append(queue_label)
        
        add_btn = ctk.CTkButton(
            control_frame,
            text="➕ Add to Queue",
            command=self.add_to_batch,
            width=120,
            fg_color=self.colors['secondary'],
            hover_color=self.colors['secondary_hover'],
            text_color='#000000'
        )
        add_btn.pack(side="right", padx=5)
        self.ui_elements['buttons'].append(add_btn)
        
        process_btn = ctk.CTkButton(
            control_frame,
            text="▶️ Process Queue",
            command=self.process_batch,
            width=120,
            fg_color=self.colors['success'],
            hover_color=self.colors['success_hover'],
            text_color='#000000'
        )
        process_btn.pack(side="right", padx=5)
        self.ui_elements['buttons'].append(process_btn)
        
        clear_btn = ctk.CTkButton(
            control_frame,
            text="🗑️ Clear Queue",
            command=self.clear_batch,
            width=120,
            fg_color=self.colors['error'],
            hover_color=self.colors['error_hover'],
            text_color='#000000'
        )
        clear_btn.pack(side="right", padx=5)
        self.ui_elements['buttons'].append(clear_btn)
        
        # Queue display
        self.batch_frame = ctk.CTkScrollableFrame(tab, height=400, fg_color=self.colors['surface'])
        self.batch_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.ui_elements['frames'].append(self.batch_frame)

    def setup_history_tab(self):
        """Setup conversion history tab"""
        tab = self.main_tabview.tab("📊 History")
        
        # Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        self.ui_elements['frames'].append(header)
        
        history_label = ctk.CTkLabel(
            header,
            text="Conversion History",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['text']
        )
        history_label.pack(side="left")
        self.ui_elements['labels'].append(history_label)
        
        clear_btn = ctk.CTkButton(
            header,
            text="🗑️ Clear",
            width=100,
            command=self.clear_history,
            fg_color=self.colors['error'],
            hover_color=self.colors['error_hover'],
            text_color='#000000'
        )
        clear_btn.pack(side="right")
        self.ui_elements['buttons'].append(clear_btn)
        
        # History list
        self.history_frame = ctk.CTkScrollableFrame(tab, height=500, fg_color=self.colors['surface'])
        self.history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.ui_elements['frames'].append(self.history_frame)
        
        self.refresh_history()

    def setup_settings_tab(self):
        """Setup settings tab"""
        tab = self.main_tabview.tab("⚙️ Settings")
        
        # General settings
        general = ctk.CTkFrame(tab, fg_color=self.colors['card'])
        general.pack(fill="x", padx=20, pady=10)
        self.ui_elements['cards'].append(general)
        
        general_label = ctk.CTkLabel(
            general,
            text="General Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text']
        )
        general_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.ui_elements['labels'].append(general_label)
        
        # Theme (already in header, but show current)
        theme_frame = ctk.CTkFrame(general, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=5)
        self.ui_elements['frames'].append(theme_frame)
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Current Theme:",
            text_color=self.colors['text']
        )
        theme_label.pack(side="left")
        self.ui_elements['labels'].append(theme_label)
        
        theme_display = ctk.CTkLabel(
            theme_frame,
            text=self.theme_manager.current_theme.capitalize(),
            font=ctk.CTkFont(weight="bold"),
            text_color=self.colors['primary']
        )
        theme_display.pack(side="left", padx=10)
        self.ui_elements['labels'].append(theme_display)
        
        # Default output
        default_frame = ctk.CTkFrame(general, fg_color="transparent")
        default_frame.pack(fill="x", padx=15, pady=5)
        self.ui_elements['frames'].append(default_frame)
        
        default_label = ctk.CTkLabel(
            default_frame,
            text="Default Format:",
            text_color=self.colors['text']
        )
        default_label.pack(side="left")
        self.ui_elements['labels'].append(default_label)
        
        default_format = ctk.CTkOptionMenu(
            default_frame,
            values=list(self.output_formats.keys()),
            width=150,
            fg_color=self.colors['input_bg'],
            button_color=self.colors['secondary'],
            button_hover_color=self.colors['secondary_hover'],
            text_color=self.colors['text']
        )
        default_format.pack(side="left", padx=10)
        default_format.set("MP3 (Compressed)")
        self.ui_elements['buttons'].append(default_format)
        
        # FFmpeg info
        ffmpeg = ctk.CTkFrame(tab, fg_color=self.colors['card'])
        ffmpeg.pack(fill="x", padx=20, pady=10)
        self.ui_elements['cards'].append(ffmpeg)
        
        ffmpeg_label = ctk.CTkLabel(
            ffmpeg,
            text="FFmpeg Status",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text']
        )
        ffmpeg_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.ui_elements['labels'].append(ffmpeg_label)
        
        status_text = "✅ FFmpeg is installed and ready!" if self.ffmpeg_available else "❌ FFmpeg not found. Download from: https://ffmpeg.org"
        status_color = self.colors['success'] if self.ffmpeg_available else self.colors['error']
        
        status_label = ctk.CTkLabel(
            ffmpeg,
            text=status_text,
            text_color=status_color
        )
        status_label.pack(anchor="w", padx=15, pady=5)
        self.ui_elements['labels'].append(status_label)
        
        if not self.ffmpeg_available:
            download_btn = ctk.CTkButton(
                ffmpeg,
                text="Download FFmpeg",
                command=lambda: webbrowser.open("https://ffmpeg.org/download.html"),
                fg_color=self.colors['secondary'],
                hover_color=self.colors['secondary_hover'],
                text_color='#000000'
            )
            download_btn.pack(anchor="w", padx=15, pady=10)
            self.ui_elements['buttons'].append(download_btn)
        
        # Test button
        test_frame = ctk.CTkFrame(tab, fg_color=self.colors['card'])
        test_frame.pack(fill="x", padx=20, pady=10)
        self.ui_elements['cards'].append(test_frame)
        
        test_label = ctk.CTkLabel(
            test_frame,
            text="Testing",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text']
        )
        test_label.pack(anchor="w", padx=15, pady=(10, 5))
        self.ui_elements['labels'].append(test_label)
        
        test_btn = ctk.CTkButton(
            test_frame,
            text="🎵 Test OGG to MP3",
            command=self.test_ogg_conversion,
            fg_color=self.colors['secondary'],
            hover_color=self.colors['secondary_hover'],
            text_color='#000000'
        )
        test_btn.pack(anchor="w", padx=15, pady=10)
        self.ui_elements['buttons'].append(test_btn)

    def create_status_bar(self):
        """Create status bar"""
        status = ctk.CTkFrame(self, height=25, fg_color=self.colors['surface_dark'])
        status.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        self.ui_elements['frames'].append(status)
        
        self.status_label = ctk.CTkLabel(
            status,
            text="✅ Ready",
            font=ctk.CTkFont(size=11),
            anchor="w",
            text_color=self.colors['text_secondary']
        )
        self.status_label.pack(side="left", padx=10)
        self.ui_elements['labels'].append(self.status_label)
        
        self.file_count_label = ctk.CTkLabel(
            status,
            text="0 files",
            font=ctk.CTkFont(size=11),
            anchor="e",
            text_color=self.colors['text_secondary']
        )
        self.file_count_label.pack(side="right", padx=10)
        self.ui_elements['labels'].append(self.file_count_label)

    # ========== FILE MANAGEMENT ==========

    def add_files(self):
        """Add files to conversion list"""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("All Audio", "*.mp3 *.flac *.wav *.ogg *.m4a *.aac *.opus *.wma"),
                ("MP3 files", "*.mp3"),
                ("FLAC files", "*.flac"),
                ("WAV files", "*.wav"),
                ("OGG files", "*.ogg"),
                ("All files", "*.*")
            ]
        )
        
        for file in files:
            self.add_single_file(file)

    def add_folder(self):
        """Add all audio files from a folder"""
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.add_folder_path(folder)

    def add_folder_path(self, folder):
        """Add all audio files from folder path"""
        audio_extensions = ['.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.opus', '.wma']
        folder_path = Path(folder)
        
        for ext in audio_extensions:
            for file in folder_path.rglob(f"*{ext}"):
                self.add_single_file(str(file))

    def add_single_file(self, file_path):
        """Add single file to list"""
        if file_path not in self.input_files:
            self.input_files.append(file_path)
            self.update_file_list()
            self.show_file_info(file_path)

    def clear_files(self):
        """Clear all files from list"""
        self.input_files = []
        self.update_file_list()
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", "No files selected")

    def update_file_list(self):
        """Update the file list display"""
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        
        for file in self.input_files:
            frame = ctk.CTkFrame(self.file_list_frame, fg_color="transparent")
            frame.pack(fill="x", pady=1)
            
            # File icon based on extension
            ext = Path(file).suffix.lower()
            icon = "🎵" if ext in ['.mp3', '.flac', '.wav'] else "📹"
            
            file_label = ctk.CTkLabel(
                frame,
                text=f"{icon} {Path(file).name}",
                anchor="w",
                text_color=self.colors['text']
            )
            file_label.pack(side="left", padx=5)
            self.ui_elements['labels'].append(file_label)
            
            # File size
            size = os.path.getsize(file) / 1024 / 1024
            size_label = ctk.CTkLabel(
                frame,
                text=f"{size:.1f} MB",
                font=ctk.CTkFont(size=10),
                text_color=self.colors['text_secondary']
            )
            size_label.pack(side="right", padx=5)
            self.ui_elements['labels'].append(size_label)
        
        self.file_count_label.configure(text=f"{len(self.input_files)} files")

    def browse_output(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_folder_var.set(folder)

    def select_output_format(self, format_name, color):
        """Select output format"""
        self.output_format_var.set(format_name)
        
        # Update button colors
        for fmt, btn in self.format_buttons.items():
            if fmt == format_name:
                btn.configure(fg_color=color)
            else:
                btn.configure(fg_color=self.colors['surface_light'])
        
        # Update format options
        self.create_format_options()

    def apply_preset(self, preset):
        """Apply preset settings"""
        color = self.theme_manager.get_format_color(preset['format'])
        self.select_output_format(preset['format'], color)
        
        # Apply format-specific options
        for key, value in preset['options'].items():
            widget_name = f"{preset['format']}_{key}"
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)
                if hasattr(widget, 'set'):
                    widget.set(value)
        
        self.status_label.configure(text=f"✅ Applied {preset['icon']} preset")

    # ========== CONVERSION LOGIC ==========

    def start_conversion(self):
        """Start the conversion process"""
        if not self.input_files:
            messagebox.showwarning("No Files", "Please add files to convert first!")
            return
        
        if not self.ffmpeg_available:
            response = messagebox.askyesno(
                "FFmpeg Missing",
                "FFmpeg is required for audio conversion. Would you like to download it now?"
            )
            if response:
                webbrowser.open("https://ffmpeg.org/download.html")
            return
        
        # Check disk space
        if not self.check_disk_space():
            return
        
        # Show stats for MP3 to lossless
        if not self.show_conversion_stats():
            return
        
        # Disable UI
        self.convert_btn.configure(state="disabled", text="⏳ CONVERTING...", fg_color=self.colors['warning'])
        self.cancel_btn.configure(state="normal")
        self.is_converting = True
        self.total_files = len(self.input_files)
        self.completed_files = 0
        self.failed_files = []
        
        # Reset progress
        self.progress_bar.set(0)
        self.progress_label.configure(text=f"Starting conversion of {self.total_files} files...")
        
        # Start conversion thread
        thread = threading.Thread(target=self.conversion_thread, daemon=True)
        thread.start()
        
        # Start progress monitoring
        self.monitor_progress()

    def conversion_thread(self):
        """Main conversion thread"""
        output_format = self.output_format_var.get()
        output_folder = Path(self.output_folder_var.get())
        
        for idx, input_file in enumerate(self.input_files):
            if not self.is_converting:
                break
            
            try:
                self.after(0, self.update_status, f"Converting: {Path(input_file).name}")
                
                # Check for MP3 source warning
                if input_file.lower().endswith('.mp3') and output_format in ['flac', 'wav']:
                    warning = self.check_mp3_source(input_file)
                    if warning:
                        self.after(0, lambda w=warning: self.show_quality_warning(w))
                
                # Generate output filename
                input_path = Path(input_file)
                output_file = output_folder / f"{input_path.stem}.{output_format}"
                
                # Handle duplicates
                counter = 1
                while output_file.exists():
                    output_file = output_folder / f"{input_path.stem} ({counter}).{output_format}"
                    counter += 1
                
                # Build and run command
                cmd = self.build_ffmpeg_command(input_file, output_file, output_format)
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if process.returncode == 0:
                    self.completed_files += 1
                    
                    # Copy metadata if desired
                    if self.preserve_tags and output_format in ['mp3', 'flac', 'ogg', 'm4a']:
                        self.copy_metadata(input_file, output_file)
                    
                    self.after(0, self.add_to_history, input_file, output_file)
                else:
                    self.failed_files.append((input_file, process.stderr))
                
            except subprocess.TimeoutExpired:
                self.failed_files.append((input_file, "Timeout - conversion took too long"))
            except Exception as e:
                self.failed_files.append((input_file, str(e)))
            
            # Update progress
            progress = (idx + 1) / self.total_files
            self.after(0, self.update_progress, progress, idx + 1)
        
        self.after(0, self.conversion_finished)

    def build_ffmpeg_command(self, input_file, output_file, output_format):
        """Build FFmpeg command based on format and source"""
        cmd = ['ffmpeg', '-i', str(input_file), '-y']
        
        # Check for special cases
        is_mp3_source = str(input_file).lower().endswith('.mp3')
        is_ogg_source = str(input_file).lower().endswith('.ogg')
        
        # Handle MP3 to lossless
        if is_mp3_source and output_format in ['flac', 'wav']:
            return self.build_mp3_to_lossless_cmd(input_file, output_file, output_format)
        
        # Handle OGG to MP3 with optimization
        if is_ogg_source and output_format == 'mp3' and self.ogg_optimization:
            optimized = self.build_ogg_to_mp3_cmd(input_file, output_file)
            if optimized:
                return optimized
        
        # Standard command building
        cmd.extend(['-map_metadata', '0', '-id3v2_version', '3'])
        
        # Format-specific options
        if output_format == 'mp3':
            bitrate = getattr(self, 'mp3_bitrate', None)
            cmd.extend(['-b:a', bitrate.get() if bitrate else '192k'])
            
            if hasattr(self, 'mp3_stereo'):
                mode = self.mp3_stereo.get()
                if mode == 'Mono':
                    cmd.extend(['-ac', '1'])
                elif mode == 'Stereo':
                    cmd.extend(['-ac', '2'])
                else:
                    cmd.extend(['-ac', '2', '-joint_stereo', '1'])
            
            cmd.extend(['-write_id3v1', '1', '-write_id3v2', '1'])
        
        elif output_format == 'flac':
            cmd.extend(['-c:a', 'flac'])
            if hasattr(self, 'flac_compression'):
                level = self.flac_compression.get().split()[0]
                cmd.extend(['-compression_level', level])
        
        elif output_format == 'ogg':
            cmd.extend(['-c:a', 'libvorbis'])
            if hasattr(self, 'ogg_quality'):
                q = self.ogg_quality.get().split()[0]
                if q == '-1':
                    q = '0'
                cmd.extend(['-q:a', q])
        
        elif output_format == 'wav':
            if hasattr(self, 'wav_depth'):
                depth = self.wav_depth.get()
                if '24' in depth:
                    cmd.extend(['-c:a', 'pcm_s24le'])
                elif '32' in depth:
                    cmd.extend(['-c:a', 'pcm_s32le'])
                else:
                    cmd.extend(['-c:a', 'pcm_s16le'])
        
        elif output_format == 'm4a':
            cmd.extend(['-c:a', 'aac', '-movflags', '+faststart'])
            if hasattr(self, 'aac_bitrate'):
                cmd.extend(['-b:a', self.aac_bitrate.get()])
        
        elif output_format == 'opus':
            cmd.extend(['-c:a', 'libopus', '-application', 'audio'])
            if hasattr(self, 'opus_bitrate'):
                cmd.extend(['-b:a', self.opus_bitrate.get()])
        
        # Add normalization if enabled
        if self.normalize:
            cmd.extend(['-af', 'loudnorm=I=-16:LRA=11:TP=-1.5'])
        
        cmd.append(str(output_file))
        return cmd

    def build_mp3_to_lossless_cmd(self, input_file, output_file, output_format):
        """Build optimized command for MP3 to lossless conversion"""
        try:
            audio = MP3(input_file)
            sample_rate = audio.info.sample_rate
            channels = audio.info.channels
            
            cmd = ['ffmpeg', '-i', str(input_file), '-y', '-map_metadata', '0']
            
            if output_format == 'flac':
                cmd.extend(['-c:a', 'flac', '-compression_level', '8'])
            else:  # wav
                # Choose bit depth based on source quality
                if audio.info.bitrate > 256000:
                    cmd.extend(['-c:a', 'pcm_s24le'])
                else:
                    cmd.extend(['-c:a', 'pcm_s16le'])
            
            cmd.extend(['-ar', str(sample_rate), '-ac', str(channels)])
            cmd.append(str(output_file))
            
            return cmd
        except:
            # Fallback
            return ['ffmpeg', '-i', str(input_file), '-y', '-c:a', 'flac' if output_format == 'flac' else 'pcm_s16le', str(output_file)]

    def build_ogg_to_mp3_cmd(self, input_file, output_file):
        """Build optimized command for OGG to MP3"""
        try:
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', str(input_file)]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            info = json.loads(result.stdout)
            
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    sample_rate = int(stream.get('sample_rate', 44100))
                    channels = int(stream.get('channels', 2))
                    
                    cmd = ['ffmpeg', '-i', str(input_file), '-y', '-map_metadata', '0']
                    
                    # Handle sample rate
                    if sample_rate > 48000:
                        cmd.extend(['-ar', '48000'])
                    elif sample_rate < 32000:
                        cmd.extend(['-ar', '44100'])
                    
                    # Handle channels
                    if channels > 2:
                        cmd.extend(['-ac', '2'])
                    
                    # MP3 settings
                    cmd.extend([
                        '-c:a', 'libmp3lame',
                        '-b:a', '192k',
                        '-q:a', '2',
                        '-joint_stereo', '1',
                    ])
                    
                    cmd.append(str(output_file))
                    return cmd
        except:
            pass
        return None

    def check_mp3_source(self, input_file):
        """Check if source is MP3 and return warning"""
        try:
            audio = MP3(input_file)
            bitrate = audio.info.bitrate // 1000
            
            return (
                f"⚠️ MP3 to Lossless Conversion Notice\n\n"
                f"Source MP3: {bitrate} kbps\n\n"
                f"Converting MP3 to FLAC/WAV will NOT improve quality!\n"
                f"The resulting file will be larger but have the same audio quality.\n\n"
                f"Continue with conversion?"
            )
        except:
            return None

    def check_disk_space(self):
        """Check if enough disk space available"""
        try:
            total_size = sum(os.path.getsize(f) for f in self.input_files)
            output_format = self.output_format_var.get()
            
            if output_format in ['wav', 'flac']:
                estimated = total_size * 10  # Lossless is much larger
            else:
                estimated = total_size * 0.8  # Compressed is slightly smaller
            
            free_space = shutil.disk_usage(self.output_folder_var.get()).free
            
            if estimated > free_space:
                return messagebox.askyesno(
                    "Low Disk Space",
                    f"Need ~{estimated/1e9:.1f}GB but only {free_space/1e9:.1f}GB free.\nContinue?"
                )
            return True
        except:
            return True

    def show_conversion_stats(self):
        """Show conversion statistics for MP3 to lossless"""
        mp3_files = [f for f in self.input_files if f.lower().endswith('.mp3')]
        
        if mp3_files and self.output_format_var.get() in ['flac', 'wav']:
            total_mp3 = sum(os.path.getsize(f) for f in mp3_files) / 1024 / 1024
            
            msg = (
                f"📊 Conversion Impact\n\n"
                f"MP3 Files: {len(mp3_files)}\n"
                f"Total MP3 Size: {total_mp3:.1f} MB\n\n"
                f"Estimated Output:\n"
                f"• FLAC: {total_mp3*10:.1f} MB\n"
                f"• WAV:  {total_mp3*12:.1f} MB\n\n"
                f"⚠️ Note: Audio quality will NOT improve!"
            )
            
            return messagebox.askyesno("Space Impact", msg, icon='warning')
        return True

    def update_progress(self, progress, current):
        """Update progress bar"""
        self.progress_bar.set(progress)
        self.progress_label.configure(
            text=f"Progress: {current}/{self.total_files} • ✓ {self.completed_files} • ✗ {len(self.failed_files)}"
        )

    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)

    def monitor_progress(self):
        """Monitor conversion progress"""
        if self.is_converting:
            self.after(100, self.monitor_progress)

    def conversion_finished(self):
        """Handle conversion completion"""
        self.is_converting = False
        self.convert_btn.configure(state="normal", text="🎵 START CONVERSION", fg_color=self.colors['primary'])
        self.cancel_btn.configure(state="disabled")
        
        success = self.completed_files
        failed = len(self.failed_files)
        
        if failed == 0:
            messagebox.showinfo(
                "Complete",
                f"✅ Successfully converted {success} files!\n\n📁 {self.output_folder_var.get()}"
            )
        else:
            error_msg = f"⚠️ Converted {success}/{self.total_files}\n\nFailed:\n"
            for f, e in self.failed_files[:3]:
                error_msg += f"• {Path(f).name}: {e[:50]}...\n"
            messagebox.showwarning("Completed with Errors", error_msg)

    def cancel_conversion(self):
        """Cancel ongoing conversion"""
        if self.is_converting and messagebox.askyesno("Cancel", "Stop conversion?"):
            self.is_converting = False
            self.status_label.configure(text="⏹️ Cancelled")

    def copy_metadata(self, source, dest):
        """Copy metadata from source to destination"""
        try:
            if dest.suffix.lower() == '.mp3':
                audio = MP3(dest, ID3=ID3)
                if source.lower().endswith('.mp3'):
                    src = MP3(source, ID3=ID3)
                    for tag in src.tags.values():
                        audio.tags.add(tag)
                audio.save()
        except:
            pass

    # ========== BATCH PROCESSING ==========

    def add_to_batch(self):
        """Add current files to batch queue"""
        if not self.input_files:
            return
        
        job = {
            'id': len(self.batch_queue) + 1,
            'files': self.input_files.copy(),
            'format': self.output_format_var.get(),
            'output': self.output_folder_var.get(),
            'options': self.get_current_options()
        }
        
        self.batch_queue.append(job)
        self.update_batch_display()
        self.clear_files()
        self.status_label.configure(text=f"📋 Added job #{job['id']} to queue")

    def process_batch(self):
        """Process all queued jobs"""
        if not self.batch_queue:
            messagebox.showinfo("Empty", "No jobs in queue")
            return
        
        for job in self.batch_queue:
            self.input_files = job['files']
            self.output_format_var.set(job['format'])
            self.output_folder_var.set(job['output'])
            self.start_conversion()
            
            # Wait for completion (simplified)
            while self.is_converting:
                time.sleep(0.1)
        
        self.batch_queue.clear()
        self.update_batch_display()
        messagebox.showinfo("Complete", "✅ All batch jobs finished!")

    def clear_batch(self):
        """Clear batch queue"""
        self.batch_queue = []
        self.update_batch_display()

    def update_batch_display(self):
        """Update batch queue display"""
        for widget in self.batch_frame.winfo_children():
            widget.destroy()
        
        if not self.batch_queue:
            empty_label = ctk.CTkLabel(
                self.batch_frame,
                text="Queue is empty",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            empty_label.pack(pady=50)
            self.ui_elements['labels'].append(empty_label)
            return
        
        for job in self.batch_queue:
            frame = ctk.CTkFrame(self.batch_frame, fg_color=self.colors['surface_light'])
            frame.pack(fill="x", padx=5, pady=2)
            self.ui_elements['frames'].append(frame)
            
            job_label = ctk.CTkLabel(
                frame,
                text=f"Job #{job['id']}: {len(job['files'])} files → {job['format'].upper()}",
                anchor="w",
                text_color=self.colors['text']
            )
            job_label.pack(padx=10, pady=5)
            self.ui_elements['labels'].append(job_label)

    def get_current_options(self):
        """Get current format options"""
        options = {}
        fmt = self.output_format_var.get()
        
        if fmt == 'mp3' and hasattr(self, 'mp3_bitrate'):
            options['bitrate'] = self.mp3_bitrate.get()
        elif fmt == 'flac' and hasattr(self, 'flac_compression'):
            options['compression'] = self.flac_compression.get()
        
        return options

    # ========== HISTORY MANAGEMENT ==========

    def add_to_history(self, input_file, output_file):
        """Add conversion to history"""
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'input': str(input_file),
            'output': str(output_file),
            'format': self.output_format_var.get()
        }
        
        self.conversion_history.append(entry)
        
        if len(self.conversion_history) > 50:
            self.conversion_history = self.conversion_history[-50:]
        
        self.save_history()
        self.refresh_history()

    def save_history(self):
        """Save history to file"""
        try:
            with open(Path.home() / '.audio_converter_history.json', 'w') as f:
                json.dump(self.conversion_history, f, indent=2)
        except:
            pass

    def load_history(self):
        """Load history from file"""
        try:
            hist_file = Path.home() / '.audio_converter_history.json'
            if hist_file.exists():
                with open(hist_file, 'r') as f:
                    self.conversion_history = json.load(f)
        except:
            self.conversion_history = []

    def refresh_history(self):
        """Refresh history display"""
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        if not self.conversion_history:
            empty_label = ctk.CTkLabel(
                self.history_frame,
                text="No conversion history",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            empty_label.pack(pady=50)
            self.ui_elements['labels'].append(empty_label)
            return
        
        for entry in reversed(self.conversion_history[-20:]):
            frame = ctk.CTkFrame(self.history_frame, fg_color=self.colors['surface_light'])
            frame.pack(fill="x", padx=5, pady=2)
            self.ui_elements['frames'].append(frame)
            
            time_label = ctk.CTkLabel(
                frame,
                text=entry['timestamp'],
                font=ctk.CTkFont(size=10),
                text_color=self.colors['text_secondary']
            )
            time_label.pack(anchor="w", padx=10, pady=(5, 0))
            self.ui_elements['labels'].append(time_label)
            
            file_label = ctk.CTkLabel(
                frame,
                text=f"📁 {Path(entry['input']).name} → {Path(entry['output']).name}",
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=self.colors['text']
            )
            file_label.pack(fill="x", padx=10, pady=(0, 5))
            self.ui_elements['labels'].append(file_label)

    def clear_history(self):
        """Clear conversion history"""
        if messagebox.askyesno("Clear", "Clear all history?"):
            self.conversion_history = []
            self.save_history()
            self.refresh_history()

    # ========== FILE INFORMATION ==========

    def show_file_info(self, file_path):
        """Display file information"""
        self.info_text.delete("1.0", "end")
        
        ext = Path(file_path).suffix.lower()
        size = os.path.getsize(file_path) / 1024 / 1024
        
        info = f"📁 File: {Path(file_path).name}\n"
        info += f"📏 Size: {size:.2f} MB\n"
        
        # Format-specific analysis
        if ext == '.mp3':
            info += self.analyze_mp3(file_path)
        elif ext == '.ogg':
            info += self.analyze_ogg(file_path)
        else:
            try:
                audio = File(file_path)
                if audio and hasattr(audio.info, 'length'):
                    info += f"⏱️ Duration: {int(audio.info.length // 60)}:{int(audio.info.length % 60):02d}\n"
                if hasattr(audio.info, 'bitrate'):
                    info += f"🎚️ Bitrate: {audio.info.bitrate // 1000} kbps\n"
            except:
                info += "⚠️ Could not read audio info\n"
        
        self.info_text.insert("1.0", info)

    def analyze_mp3(self, file_path):
        """Analyze MP3 file"""
        try:
            audio = MP3(file_path)
            bitrate = audio.info.bitrate // 1000
            size = os.path.getsize(file_path) / 1024 / 1024
            
            info = f"🎚️ Bitrate: {bitrate} kbps\n"
            info += f"🔊 Sample Rate: {audio.info.sample_rate} Hz\n"
            info += f"🎼 Channels: {audio.info.channels}\n"
            info += f"⏱️ Duration: {int(audio.info.length // 60)}:{int(audio.info.length % 60):02d}\n\n"
            
            # Conversion recommendations
            info += "📊 Conversion Options:\n"
            info += f"→ To FLAC: {self.estimate_lossless_size(audio.info.length, 'flac'):.1f} MB\n"
            info += f"→ To WAV:  {self.estimate_lossless_size(audio.info.length, 'wav'):.1f} MB\n\n"
            
            if bitrate < 192:
                info += "⚠️ Low quality source - lossless conversion not recommended\n"
            
            return info
        except:
            return ""

    def analyze_ogg(self, file_path):
        """Analyze OGG file"""
        try:
            audio = OggVorbis(file_path)
            
            info = f"🎚️ Bitrate: {audio.info.bitrate // 1000} kbps\n"
            info += f"🔊 Sample Rate: {audio.info.sample_rate} Hz\n"
            info += f"🎼 Channels: {audio.info.channels}\n"
            info += f"⏱️ Duration: {int(audio.info.length // 60)}:{int(audio.info.length % 60):02d}\n\n"
            
            # OGG to MP3 recommendation
            info += "📊 To MP3:\n"
            info += f"→ Estimated size: {self.estimate_mp3_size(audio.info.length):.1f} MB\n"
            info += "→ Recommended: 192kbps for good quality\n"
            
            return info
        except:
            return ""

    def estimate_lossless_size(self, duration_seconds, format):
        """Estimate lossless file size"""
        if format == 'wav':
            return (1411 * duration_seconds) / 8 / 1024
        else:  # flac
            wav_size = (1411 * duration_seconds) / 8 / 1024
            return wav_size * 0.6

    def estimate_mp3_size(self, duration_seconds):
        """Estimate MP3 file size"""
        return (192 * duration_seconds) / 8 / 1024

    def show_quality_warning(self, warning):
        """Show quality warning"""
        messagebox.showwarning("Quality Notice", warning)

    def test_ogg_conversion(self):
        """Test OGG to MP3 conversion"""
        ogg_files = [f for f in self.input_files if f.lower().endswith('.ogg')]
        
        if not ogg_files:
            messagebox.showinfo("No OGG", "Please add OGG files first")
            return
        
        self.output_format_var.set('mp3')
        color = self.theme_manager.get_format_color('mp3')
        self.select_output_format('mp3', color)
        
        messagebox.showinfo(
            "Test Ready",
            f"Found {len(ogg_files)} OGG file(s)\nClick START CONVERSION to begin"
        )

    # ========== UTILITIES ==========

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.bind('<Control-o>', lambda e: self.add_files())
        self.bind('<Control-v>', lambda e: self.add_folder())
        self.bind('<Control-space>', lambda e: self.start_conversion())
        self.bind('<Escape>', lambda e: self.cancel_conversion())
        self.bind('<Control-t>', lambda e: self.cycle_theme())

    def cycle_theme(self):
        """Cycle through themes with keyboard shortcut"""
        themes = ["dark", "light", "system"]
        current = themes.index(self.theme_manager.current_theme)
        next_theme = themes[(current + 1) % len(themes)]
        self.change_theme(next_theme)

    def try_add_drag_drop(self):
        """Try to add drag and drop support"""
        try:
            self.drop_target_register('*')
            self.dnd_bind('<<Drop>>', self.on_drop)
        except:
            pass

    def on_drop(self, event):
        """Handle dropped files"""
        files = self.tk.splitlist(event.data)
        for file in files:
            file = file.strip('{}').strip('"')
            if os.path.isfile(file):
                self.add_single_file(file)
            elif os.path.isdir(file):
                self.add_folder_path(file)


# ========== MAIN ==========

if __name__ == "__main__":
    app = AudioConverterPro()
    app.mainloop()