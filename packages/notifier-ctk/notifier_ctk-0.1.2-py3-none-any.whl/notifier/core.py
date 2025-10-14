import os, platform, subprocess, threading, time, shutil, regex, requests, tempfile
from io import BytesIO
from PIL import Image
from importlib import resources
import customtkinter as ctk
from customtkinter import CTkImage
import screeninfo


# -----------------------------
# Sound Player
# -----------------------------
class SoundPlayer:
    """Cross-platform asynchronous sound player."""

    @staticmethod
    def play(path: str):
        system = platform.system()
        try:
            if system == "Windows":
                import winsound
                winsound.PlaySound(os.path.normpath(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            elif system == "Darwin":
                subprocess.Popen(["afplay", path])
            elif system == "Linux":
                for player in ("paplay", "aplay", "ffplay"):
                    if shutil.which(player):
                        cmd = [player, path] if player != "ffplay" else ["ffplay", "-nodisp", "-autoexit", path]
                        subprocess.Popen(cmd)
                        return
                print("❌ No compatible audio player found on Linux.")
            else:
                print(f"❌ Unsupported platform: {system}")
        except Exception as e:
            print(f"Sound playback failed: {e}")

    @classmethod
    def play_async(cls, path: str):
        threading.Thread(target=cls.play, args=(path,), daemon=True).start()


# -----------------------------
# Emoji Loader
# -----------------------------
class EmojiLoader:
    """Handles emoji-to-image fetching and caching."""
    CACHE_DIR = "emoji_cache"

    @staticmethod
    def extract_cluster(text):
        match = regex.match(r'\X', text)
        return match.group(0) if match else text[0]

    @staticmethod
    def to_codepoints(emoji, strip_fe0f=True):
        cps = [f"{ord(c):x}" for c in emoji if not (strip_fe0f and ord(c) == 0xfe0f)]
        return "_".join(cps)

    @classmethod
    def get_image(cls, emoji, size=24):
        emoji = cls.extract_cluster(emoji)
        cps = cls.to_codepoints(emoji)
        local = os.path.join(cls.CACHE_DIR, f"{cps}.png")
        url = f"https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/128/emoji_u{cps}.png"

        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        try:
            if os.path.exists(local):
                img = Image.open(local).convert("RGBA").resize((size, size), Image.LANCZOS)
                return CTkImage(light_image=img, size=(size, size))
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content)).convert("RGBA")
            img.save(local)
            img = img.resize((size, size), Image.LANCZOS)
            return CTkImage(light_image=img, size=(size, size))
        except Exception as e:
            print(f"❌ Failed to load emoji '{emoji}': {e}")
            return None


# -----------------------------
# Helper: read packaged resource into a temporary file
# -----------------------------
def _get_resource_temp(package: str, *parts, suffix=""):
    """Read a packaged resource (e.g. wav/gif) to a temp file and return its path."""
    try:
        data = resources.files(package).joinpath(*parts).read_bytes()
        fd, tmp = tempfile.mkstemp(suffix=suffix)
        os.write(fd, data)
        os.close(fd)
        return tmp
    except Exception as e:
        print(f"❌ Failed to read resource {parts}: {e}")
        return None


# -----------------------------
# Notifier
# -----------------------------
class Notifier:
    """CustomTkinter animated notification window."""

    def __init__(self,
                 title="🧪 make magic potion",
                 message="+1 focus — 3h",
                 button="🧠 Brain leveled up",
                 gif_path=None,
                 intro_sound=None,
                 click_sound=None,
                 pitch_sound=None,
                 beep=False):
        self.title_text = title
        self.message = message
        self.button_text = button

        # Load defaults from packaged resources if not provided
        # or _get_resource_temp("notifier", "emojis", "magic.gif", suffix=".gif")
        self.gif_path = gif_path or None
        self.intro_sound = intro_sound or _get_resource_temp("notifier", "sound", "intro.wav", suffix=".wav")
        self.click_sound = click_sound or _get_resource_temp("notifier", "sound", "pop.wav", suffix=".wav")
        self.pitch_sound = pitch_sound or _get_resource_temp("notifier", "sound", "pitch.wav", suffix=".wav")

        self.beep = beep
        self._stop_sound = False
        self._init_ui_constants()

    def _init_ui_constants(self):
        self.WIDTH, self.HEIGHT = 360, 140
        self.ICON_SIZE = 48
        self.BG = "#222226"
        self.FG = "white"
        self.FG2 = "#c9c9c9"
        self.BTN_BG = "#2f2f32"
        self.BTN_HOVER = "#343435"
        self.BORDER_COLOR = "#434343"
        self.BORDER_WIDTH = 1
        self.TRANSPARENT = "#123456"

    def _init_window(self):
        screen = screeninfo.get_monitors()[0]
        self.final_x = screen.width - self.WIDTH - 15
        self.final_y = screen.height - self.HEIGHT - 15
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(fg_color=self.TRANSPARENT)
        self.root.wm_attributes("-transparentcolor", self.TRANSPARENT)
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{self.final_x+30}+{self.final_y+30}")

        self.frame = ctk.CTkFrame(
            self.root,
            fg_color=self.BG,
            corner_radius=11,
            width=self.WIDTH - 2 * self.BORDER_WIDTH,
            height=self.HEIGHT - 2 * self.BORDER_WIDTH,
            border_width=self.BORDER_WIDTH,
            border_color=self.BORDER_COLOR
        )
        self.frame.place(x=self.BORDER_WIDTH, y=self.BORDER_WIDTH)

    def _load_media(self):
        """Load either a GIF (animated), static image, or nothing."""
        if not self.gif_path or not os.path.exists(self.gif_path):
            return None, None

        try:
            img = Image.open(self.gif_path)
            if getattr(img, "is_animated", False):
                # Animated GIF
                frames = []
                try:
                    while True:
                        frame = img.copy().resize((self.ICON_SIZE, self.ICON_SIZE), Image.LANCZOS)
                        frames.append(CTkImage(light_image=frame, size=(self.ICON_SIZE, self.ICON_SIZE)))
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass
                return "gif", frames
            else:
                # Static image
                static_img = img.resize((self.ICON_SIZE, self.ICON_SIZE), Image.LANCZOS)
                return "static", CTkImage(light_image=static_img, size=(self.ICON_SIZE, self.ICON_SIZE))
        except Exception as e:
            print(f"❌ Failed to load media: {e}")
            return None, None

    def _load_gif_frames(self):
        gif = Image.open(self.gif_path)
        frames = []
        try:
            while True:
                img = gif.copy().resize((self.ICON_SIZE, self.ICON_SIZE), Image.LANCZOS)
                frames.append(CTkImage(light_image=img, size=(self.ICON_SIZE, self.ICON_SIZE)))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        return frames

    def _sound_loop(self):
        def loop():
            max_times = 4 if self.beep else 6
            delay = 10 if self.beep else 20
            for i in range(max_times):
                if self._stop_sound:
                    return
                sound = self.pitch_sound if self.beep and (i == max_times - 2) else self.intro_sound
                SoundPlayer.play_async(sound)
                if i < max_times - 1:
                    for _ in range(delay * 10):
                        if self._stop_sound:
                            return
                        time.sleep(0.1)
            if self.beep and not self._stop_sound:
                self.root.after(0, self._slide_out)
        threading.Thread(target=loop, daemon=True).start()

    def _slide_in(self):
        steps = 30
        delay = 300 // steps
        out_distance = 180
        start_x = self.final_x + out_distance
        end_x = self.final_x

        def animate(step=0):
            if step <= steps:
                t = step / steps
                eased = 1 - (1 - t) ** 2
                new_x = start_x + (end_x - start_x) * eased
                self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{int(new_x)}+{self.final_y}")
                self.root.after(delay, animate, step + 1)
            else:
                self._sound_loop()

        animate()

    def _slide_out(self):
        snap_distance, snap_steps, snap_delay = -15, 4, 15
        snap_x = self.final_x + snap_distance

        def snap_back(step=0):
            if step <= snap_steps:
                t = step / snap_steps
                eased = t * t
                new_x = self.final_x + eased * snap_distance
                self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{int(new_x)}+{self.final_y}")
                self.root.after(snap_delay, snap_back, step + 1)
            else:
                self.root.after(300, slide_forward)

        def slide_forward():
            out_distance, out_steps, out_delay = 500, 30, 14
            def animate(step=0):
                if step <= out_steps:
                    t = step / out_steps
                    eased = 1 - (1 - t) ** 2
                    new_x = snap_x + eased * out_distance
                    self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{int(new_x)}+{self.final_y}")
                    self.root.after(out_delay, animate, step + 1)
                else:
                    self.root.destroy()
            animate()

        snap_back()

    def _on_click(self, *_):
        self._stop_sound = True
        SoundPlayer.play_async(self.click_sound)
        self._slide_out()

    def show(self):
        self._init_window()
        media_type, media_data = self._load_media()
        title_img = EmojiLoader.get_image(self.title_text, 24)
        button_img = EmojiLoader.get_image(self.button_text, 20)

        has_media = media_type is not None

        # Layout coordinates depending on presence of image
        left_pad = 20 if has_media else 0
        text_x = 80 if has_media else 20

        if has_media:
            icon_label = ctk.CTkLabel(self.frame, text="", fg_color=self.BG)
            icon_label.place(x=left_pad, y=25)

            if media_type == "gif":
                frames = media_data
                def animate_gif(idx=0):
                    icon_label.configure(image=frames[idx])
                    self.root.after(100, animate_gif, (idx + 1) % len(frames))
                animate_gif()
            else:
                icon_label.configure(image=media_data)

        # Emoji-less text function
        def remove_emoji(text):
            cluster = EmojiLoader.extract_cluster(text)
            return text[len(cluster):]

        title_label = ctk.CTkLabel(
            self.frame,
            text=remove_emoji(self.title_text),
            image=title_img,
            compound="left",
            fg_color=self.BG,
            text_color=self.FG,
            font=ctk.CTkFont(family="Segoe UI", size=15)
        )
        title_label.place(x=text_x, y=20)

        msg_label = ctk.CTkLabel(
            self.frame,
            text=self.message,
            fg_color=self.BG,
            text_color=self.FG2,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        msg_label.place(x=text_x, y=45)

        # Button area
        button_frame = ctk.CTkFrame(
            self.frame,
            fg_color=self.BORDER_COLOR,
            corner_radius=6,
            width=self.WIDTH - 40,
            height=28
        )
        button_frame.place(relx=0.5, y=90, anchor="n")

        button_label = ctk.CTkLabel(
            button_frame,
            text=remove_emoji(self.button_text),
            image=button_img,
            compound="left",
            fg_color=self.BTN_BG,
            text_color=self.FG,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=6,
            width=self.WIDTH - 40 - 2 * self.BORDER_WIDTH,
            height=28 - 2 * self.BORDER_WIDTH
        )
        button_label.place(x=self.BORDER_WIDTH, y=self.BORDER_WIDTH)

        button_label.bind("<Enter>", lambda e: button_label.configure(fg_color=self.BTN_HOVER))
        button_label.bind("<Leave>", lambda e: button_label.configure(fg_color=self.BTN_BG))
        button_label.bind("<Button-1>", self._on_click)

        self._slide_in()
        self.root.mainloop()
