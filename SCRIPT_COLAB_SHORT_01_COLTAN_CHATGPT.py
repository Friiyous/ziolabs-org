# ==============================================================================
# 🎬 ZIOLABS WEB TV — PIPELINE OFFICIEL COLAB : SHORT 01 (FORMAT 9:16)
# Sujet : « Pourquoi ChatGPT et ton iPhone mourraient sans le Coltan de RDC »
# Spécifications : 1080x1920 (9:16) | 30 fps | EBU R128 (-14 LUFS) | Sous-titres Or #FFD700
# 100% Documentaire Cinématographique (SANS ANIMATEUR)
# ==============================================================================

# --- ÉTAPE 1 : INSTALLATION DES PACKAGES & MONTAGE SÉCURISÉ DRIVE ---
print("📦 Installation des dépendances optimisées (sans conflit de version)...")
!pip install -q --no-warn-conflicts faster-whisper gTTS

import os, sys, time, gc, threading, subprocess, shutil
import torch

# Montage sécurisé de Google Drive (Gestion anti-crash si déjà monté)
if os.path.exists('/content/drive/MyDrive'):
    print("✅ Google Drive est déjà monté et prêt.")
else:
    print("📂 Connexion à Google Drive...")
    from google.colab import drive
    try:
        drive.mount('/content/drive', force_remount=False)
    except Exception as e:
        print(f"⚠️ Remontage forcé de Google Drive suite à : {e}")
        drive.mount('/content/drive', force_remount=True)

# Définition des répertoires de production
BASE_DIR = "/content/drive/MyDrive/PATRIMOINE_ZIOLABS_WEBTV/THEME_01_COLTAN_LITHIUM/SHORT_01"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
EXPORT_DIR = "/content/drive/MyDrive/PATRIMOINE_ZIOLABS_WEBTV/00_EXPORTS_FINAUX"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# Thread Heartbeat Anti-Veille Drive
def heartbeat():
    hb_file = os.path.join(EXPORT_DIR, ".colab_heartbeat.txt")
    while True:
        try:
            with open(hb_file, "w") as f:
                f.write(f"ZioLabs Short 01 Heartbeat: {time.time()}\n")
        except: pass
        time.sleep(30)

t = threading.Thread(target=heartbeat, daemon=True)
t.start()
print("🛡️ Verrou anti-veille et répertoires de production initialisés sur Google Drive.")

# Patch de compatibilité PyAV / Faster-Whisper
import av
_orig_open = av.open
def _safe_av_open(*args, **kwargs):
    kwargs.pop("metadata_errors", None)
    return _orig_open(*args, **kwargs)
av.open = _safe_av_open
print("✅ Étape 1 validée : Environnement & Drive 100% opérationnels.")


# --- ÉTAPE 2 : GÉNÉRATION & NORMALISATION AUDIO BROADCAST (EBU R128) ---
from gtts import gTTS

TEXT_SHORT_01 = (
    "Tu penses que ton smartphone et ChatGPT fonctionnent grâce à la magie de la Silicon Valley ? "
    "Regarde de plus près. À l'intérieur de chaque puce, il y a du coltan. "
    "Et 70 % du coltan mondial vient d'un seul endroit : la République Démocratique du Congo. "
    "Sans ce minerai unique, aucune puce ne peut gérer l'électricité sans fondre. "
    "Chaque fois que tu lances une recherche ou que tu génères une image par IA, "
    "c'est la terre africaine qui travaille sous tes doigts. "
    "L'Afrique n'est pas en retard sur le monde numérique : "
    "c'est le monde numérique qui dépend entièrement de l'Afrique. "
    "Abonne-toi pour découvrir la vérité que les géants de la tech ne te disent jamais."
)

raw_audio_path = os.path.join(AUDIO_DIR, "short01_raw.mp3")
master_audio_path = os.path.join(AUDIO_DIR, "short01_master_ebur128.wav")

if not os.path.exists(master_audio_path) or os.path.getsize(master_audio_path) < 10000:
    print("🎙️ Synthèse vocale de haute qualité pour Short 01...")
    tts = gTTS(text=TEXT_SHORT_01, lang='fr', slow=False)
    tts.save(raw_audio_path)
    
    # Normalisation Broadcast EBU R128 (-14 LUFS, TP -1.5 dB)
    cmd_audio = [
        "ffmpeg", "-y", "-i", raw_audio_path,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,highpass=f=75,equalizer=f=3200:t=q:w=1.2:g=2.2",
        "-ar", "44100", "-ac", "2",
        master_audio_path
    ]
    subprocess.run(cmd_audio, check=True)
    if os.path.exists(raw_audio_path): os.remove(raw_audio_path)
    print(f"✅ Voix Master Broadcast prête : {master_audio_path}")
else:
    print(f"⏩ Audio Master déjà existant : {master_audio_path}")


# --- ÉTAPE 3 : GÉNÉRATION DES SOUS-TITRES DYNAMIQUES OR #FFD700 ---
from faster_whisper import WhisperModel

# Détection robuste du GPU (CUDA)
use_cuda = torch.cuda.is_available()
device = "cuda" if use_cuda else "cpu"
compute_type = "float16" if use_cuda else "int8"
print(f"⚡ Initialisation Faster-Whisper sur périphérique : {device.upper()} ({compute_type})...")

model = WhisperModel("small", device=device, compute_type=compute_type)
segments, info = model.transcribe(master_audio_path, language="fr", word_timestamps=True)

ass_path = os.path.join(BASE_DIR, "subtitles_short01.ass")

# Style ZioLabs : Police système robuste, Or pur #FFD700 (&H0000D7FF), Contour Pétrole Sombre (&H002F2609)
ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,62,&H0000D7FF,&H000000FF,&H002F2609,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,2,70,70,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def format_ass_time(sec):
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100: cs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"

events, words_buffer = [], []
for seg in segments:
    for w in seg.words:
        clean_word = w.word.strip()
        words_buffer.append((clean_word, w.start, w.end))
        if len(words_buffer) >= 3 or clean_word.endswith(('.', '?', '!', ':')):
            st_str = format_ass_time(words_buffer[0][1])
            en_str = format_ass_time(words_buffer[-1][2])
            text_str = " ".join([wb[0] for wb in words_buffer])
            
            # Surlignage Cyan lumineux pour les mots-clés d'impact
            for kw in ["ChatGPT", "Silicon Valley", "coltan", "Congo", "IA", "Afrique", "Abonne-toi"]:
                text_str = text_str.replace(kw, f"{{\\c&H00FFFF00\\b1}}{kw}{{\\c&H0000D7FF\\b0}}")
                
            events.append(f"Dialogue: 0,{st_str},{en_str},Default,,0,0,0,,{text_str}")
            words_buffer = []

if words_buffer:
    st_str = format_ass_time(words_buffer[0][1])
    en_str = format_ass_time(words_buffer[-1][2])
    text_str = " ".join([wb[0] for wb in words_buffer])
    events.append(f"Dialogue: 0,{st_str},{en_str},Default,,0,0,0,,{text_str}")

with open(ass_path, "w", encoding="utf-8") as f:
    f.write(ass_header + "\n".join(events))

# Copie locale temporaire pour éviter toute friction de chemin FUSE dans FFmpeg
local_ass = "/tmp/short01_subtitles.ass"
shutil.copy(ass_path, local_ass)
print(f"✅ Fichier de sous-titres or généré et synchronisé : {ass_path}")


# --- ÉTAPE 4 : MONTAGE CINÉMATIQUE & EXPORT FINAL MP4 9:16 ---
output_short01 = os.path.join(EXPORT_DIR, "SHORT_01_COLTAN_CHATGPT_9x16.mp4")
probe_cmd = f"ffprobe -i '{master_audio_path}' -show_entries format=duration -v quiet -of csv='p=0'"
duration_sec = float(subprocess.check_output(probe_cmd, shell=True).decode().strip())

print(f"🎬 Encodage cinématique du Short 01 ({duration_sec:.1f}s) en 1080x1920...")

# Habillage ZioLabs Web TV : Bandeau supérieur officiel + sous-titrage or incrusté
vf_filter = (
    f"subtitles={local_ass},"
    f"drawbox=y=130:h=120:color=0x09262F@0.9:t=fill,"
    f"drawtext=text='COLTAN & CHATGPT : LE SECRET DU CONGO':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=34:x=(w-text_w)/2:y=172"
)

cmd_render = [
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", f"color=c=0x09262F:s=1080x1920:d={duration_sec}:r=30",
    "-i", master_audio_path,
    "-vf", vf_filter,
    "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    output_short01
]
subprocess.run(cmd_render, check=True)

# Vérification finale
if os.path.exists(output_short01):
    size_mb = os.path.getsize(output_short01) / (1024 * 1024)
    print("\n" + "="*70)
    print(f"🏆 MASTER FINAL DISPONIBLE SUR GOOGLE DRIVE ({size_mb:.1f} MB) :")
    print(f"👉 {output_short01}")
    print("="*70)
