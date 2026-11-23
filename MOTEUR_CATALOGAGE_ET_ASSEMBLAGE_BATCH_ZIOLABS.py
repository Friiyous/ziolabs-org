# ==============================================================================
# 🎬 ZIOLABS WEB TV — MOTEUR INDUSTRIEL DE CATALOGAGE & ASSEMBLAGE PAR LOTS
# PROJET : Bible Audiovisuelle & Générateur Automatique d'Épisodes et Shorts
# COMPATIBILITÉ : Google Colab (GPU T4 / CPU) & Local Mac/Linux
# ==============================================================================

import os
import sys
import json
import time
import shutil
import threading
import subprocess
from pathlib import Path

# ==============================================================================
# 1. INITIALISATION & DÉTECTION INTELLIGENTE DU DRIVE
# ==============================================================================
print("🚀 [1/5] Connexion & Détection de l'arborescence Google Drive...")

try:
    from google.colab import drive
    if not os.path.exists('/content/drive/MyDrive'):
        drive.mount('/content/drive', force_remount=False)
    DRIVE_ROOT = Path('/content/drive/MyDrive')
    IS_COLAB = True
    print("✅ Google Drive monté avec succès dans Colab.")
except Exception:
    DRIVE_ROOT = Path.home() / "Google Drive"
    if not DRIVE_ROOT.exists():
        DRIVE_ROOT = Path("/Users/apple/Desktop") # Fallback local
    IS_COLAB = False
    print(f"ℹ️ Exécution hors-Colab. Racine : {DRIVE_ROOT}")

# Détection intelligente du dossier de clips (tolérance aux variantes de noms)
CANDIDATE_DIRS = [
    DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV',
    DRIVE_ROOT / 'Ziolabs_Clips',
    DRIVE_ROOT / 'ZIOLABS_CLIPS',
    DRIVE_ROOT / 'Clips',
    DRIVE_ROOT / 'Videos'
]

ASSETS_DIR = None
for c in CANDIDATE_DIRS:
    if c.exists():
        ASSETS_DIR = c
        break

if ASSETS_DIR is None:
    # Recherche automatique du premier dossier contenant des vidéos
    print("🔍 Recherche automatique d'un dossier de clips dans MyDrive...")
    for root, dirs, files in os.walk(DRIVE_ROOT):
        if any(f.lower().endswith(('.mp4', '.mov', '.mkv', '.webm')) for f in files):
            ASSETS_DIR = Path(root)
            print(f"🎯 Dossier source détecté automatiquement : {ASSETS_DIR}")
            break

if ASSETS_DIR is None:
    ASSETS_DIR = DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV'
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Dossier créé par défaut : {ASSETS_DIR}")

OUTPUT_DIR = DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV' / '00_EXPORTS_FINAUX'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BIBLE_FILE = DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV' / 'bible_ziolabs_catalog.json'

print(f"📂 Dossier Source : {ASSETS_DIR}")
print(f"📁 Dossier Sortie : {OUTPUT_DIR}")
print(f"📖 Fichier Bible : {BIBLE_FILE}")

# Sentinelle anti-veille pour les longs batchs
def sentinel_heartbeat():
    hb_file = OUTPUT_DIR / ".batch_heartbeat.txt"
    while True:
        try:
            with open(hb_file, "w") as f:
                f.write(f"ZioLabs Batch Assembly Active: {time.time()}\n")
        except: pass
        time.sleep(30)

t = threading.Thread(target=sentinel_heartbeat, daemon=True)
t.start()
print("🛡️ Sentinelle anti-veille activée.")


# ==============================================================================
# 2. INSPECTION TECHNIQUE PRÉCISE VIA FFPROBE
# ==============================================================================
def get_video_info(filepath):
    """Extrait les métadonnées techniques complètes (résolution, ratio, audio, fps, durée)."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=width,height,codec_name,codec_type,r_frame_rate",
        "-of", "json", str(filepath)
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data.get('format', {}).get('duration', 0))
            streams = data.get('streams', [])
            
            v_stream = next((s for s in streams if s.get('codec_type') == 'video'), {})
            a_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)
            
            w = v_stream.get('width', 0)
            h = v_stream.get('height', 0)
            codec = v_stream.get('codec_name', 'unknown')
            
            # Détection de l'orientation
            if w > 0 and h > 0:
                aspect = "16:9" if w >= h else "9:16"
            else:
                aspect = "unknown"
                
            has_audio = (a_stream is not None)
            
            return {
                "duration": round(duration, 2),
                "width": w,
                "height": h,
                "aspect": aspect,
                "codec": codec,
                "has_audio": has_audio
            }
    except Exception as e:
        pass
    return {"duration": 0, "width": 0, "height": 0, "aspect": "unknown", "codec": "unknown", "has_audio": False}


# ==============================================================================
# 3. SCAN ET INDEXATION DE LA BIBLE AUDIOVISUELLE ZIOLABS
# ==============================================================================
print("\n🔍 [2/5] Scan & Indexation des assets dans la Bible ZioLabs...")
catalog = []
video_extensions = {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'}

for root, _, files in os.walk(ASSETS_DIR):
    # Ignorer le dossier d'export pour éviter les boucles infinies
    if "00_EXPORTS_FINAUX" in root or "Ziolabs_Outputs" in root:
        continue
    for file in sorted(files):
        ext = os.path.splitext(file)[1].lower()
        if ext in video_extensions and not file.startswith('.'):
            file_path = Path(root) / file
            info = get_video_info(file_path)
            
            if info["duration"] <= 0.5:
                continue # Ignorer les fichiers corrompus ou vides
                
            category = file_path.parent.name if file_path.parent != ASSETS_DIR else "general"
            
            try:
                rel_path = str(file_path.relative_to(DRIVE_ROOT))
            except Exception:
                rel_path = str(file_path)
                
            catalog.append({
                "filename": file,
                "relative_path": rel_path,
                "full_path": str(file_path),
                "category": category,
                "duration": info["duration"],
                "resolution": f"{info['width']}x{info['height']}",
                "aspect": info["aspect"],
                "has_audio": info["has_audio"],
                "used_count": 0
            })

# Sauvegarde de la Bible JSON
with open(BIBLE_FILE, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=4, ensure_ascii=False)

clips_16x9 = [c for c in catalog if c["aspect"] == "16:9"]
clips_9x16 = [c for c in catalog if c["aspect"] == "9:16"]

print(f"✅ Bible ZioLabs mise à jour : {len(catalog)} assets répertoriés !")
print(f"   📺 Formats Paysage (16:9) : {len(clips_16x9)} clips")
print(f"   📱 Formats Shorts  (9:16) : {len(clips_9x16)} clips")
print(f"📁 Fichier Bible sauvegardé dans : {BIBLE_FILE}")


# ==============================================================================
# 4. MOTEUR INDUSTRIEL DE NORMALISATION & ASSEMBLAGE SÉCURISÉ
# ==============================================================================
def normalize_clip(clip_meta, target_aspect="16:9", temp_index=0):
    """Normalise un clip en résolution standardisée, 30fps CFR et audio stéréo 44.1kHz."""
    temp_dir = Path("/tmp/ziolabs_norm")
    temp_dir.mkdir(parents=True, exist_ok=True)
    norm_path = temp_dir / f"norm_clip_{temp_index:03d}.mp4"
    
    in_file = clip_meta["full_path"]
    
    if target_aspect == "16:9":
        target_w, target_h = 1920, 1080
    else:
        target_w, target_h = 1080, 1920
        
    vf = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30"
    
    cmd = ["ffmpeg", "-y"]
    cmd += ["-i", in_file]
    
    # Si le clip n'a pas de piste audio, on génère un flux silencieux pour éviter les désynchronisations concat
    if not clip_meta["has_audio"]:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        cmd += ["-vf", vf]
        cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p"]
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    else:
        cmd += ["-vf", vf]
        cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p"]
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2"]
        
    cmd.append(str(norm_path))
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return norm_path


def assemble_batch(clips_to_merge, output_filename, aspect="16:9", title_banner="ZIOLABS WEB TV"):
    """Assemble une série de clips avec habillage ZioLabs officiel et audio EBU R128."""
    out_path = OUTPUT_DIR / output_filename
    if out_path.exists() and out_path.stat().st_size > 1000000:
        print(f"⏩ Épisode déjà généré : {output_filename}")
        return
        
    print(f"🎬 Assemblage sécurisé ({len(clips_to_merge)} clips en {aspect}) ➔ {output_filename}...")
    
    # 1. Normalisation de chaque clip dans un conteneur temporaire
    temp_norm_files = []
    for idx, c in enumerate(clips_to_merge):
        try:
            n_file = normalize_clip(c, target_aspect=aspect, temp_index=idx)
            temp_norm_files.append(n_file)
        except Exception as e:
            print(f"⚠️ Erreur normalisation sur {c['filename']} ({e}), clip ignoré.")
            
    if not temp_norm_files:
        print("❌ Aucun clip n'a pu être normalisé pour ce lot.")
        return
        
    # 2. Concaténation ultra-rapide des clips normalisés identiques
    concat_list = Path("/tmp/ziolabs_concat_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for nf in temp_norm_files:
            f.write(f"file '{nf}'\n")
            
    temp_merged = Path("/tmp/temp_merged_raw.mp4")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(temp_merged)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # 3. Application de l'habillage officiel ZioLabs Web TV & Normalisation EBU R128
    if aspect == "16:9":
        vf_overlay = (
            f"drawbox=y=0:h=90:color=0x09262F@0.85:t=fill,"
            f"drawtext=text='ZIOLABS WEB TV  |  {title_banner}':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=28:x=60:y=32"
        )
    else:
        vf_overlay = (
            f"drawbox=y=130:h=120:color=0x09262F@0.9:t=fill,"
            f"drawtext=text='{title_banner}':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=34:x=(w-text_w)/2:y=172"
        )
        
    cmd_final = [
        "ffmpeg", "-y", "-i", str(temp_merged),
        "-vf", vf_overlay,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Nettoyage temporaire
    shutil.rmtree("/tmp/ziolabs_norm", ignore_errors=True)
    if temp_merged.exists(): temp_merged.unlink()
    
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"🏆 ÉPISODE FINALISÉ ({size_mb:.1f} MB) ➔ {out_path.name}")


# ==============================================================================
# 5. EXÉCUTION DU BATCH PAR LOTS THÉMATIQUES
# ==============================================================================
LOT_SIZE = 5

print("\n🚀 [4/5] Production des Épisodes Grands Formats (16:9)...")
if clips_16x9:
    for i in range(0, len(clips_16x9), LOT_SIZE):
        batch = clips_16x9[i:i+LOT_SIZE]
        if len(batch) >= 2:
            ep_num = (i // LOT_SIZE) + 1
            cat_name = batch[0].get("category", "HISTOIRE & TECH").upper()
            ep_name = f"ZIOLABS_GRAND_RECUT_EP_{ep_num:03d}_16x9.mp4"
            assemble_batch(batch, ep_name, aspect="16:9", title_banner=f"SÉLECTION OFFICIELLE — LOT {ep_num}")
else:
    print("ℹ️ Aucun clip 16:9 identifié pour l'assemblage long.")

print("\n🚀 [5/5] Production des Shorts Viraux (9:16)...")
if clips_9x16:
    for i in range(0, len(clips_9x16), 3):
        batch = clips_9x16[i:i+3]
        if len(batch) >= 2:
            short_num = (i // 3) + 1
            short_name = f"ZIOLABS_SHORT_COMPIL_EP_{short_num:03d}_9x16.mp4"
            assemble_batch(batch, short_name, aspect="9:16", title_banner="ZIOLABS SHORTS VIRAL")
else:
    print("ℹ️ Aucun clip 9:16 identifié pour l'assemblage court.")

print("\n" + "="*80)
print(f"🏁 TRAITEMENT INDUSTRIEL ACHEVÉ ! TOUS LES EXPORTS SONT DANS :")
print(f"👉 {OUTPUT_DIR}")
print("="*80)
