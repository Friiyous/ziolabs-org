# ==============================================================================
# 🎬 ZIOLABS WEB TV — PIPELINE INDUSTRIEL DE NUIT (MASS PRODUCTION)
# OBJECTIF : Traitement Nocturne Continu basé à 100% sur vos Assets du Google Drive
# FONCTIONNALITÉS : 
#   1. Scan et Indexation Complète de 300+ clips dans la Bible JSON
#   2. Tri intelligent automatique : Format 16:9 (Longs) vs Format 9:16 (Shorts)
#   3. Normalisation vidéo anti-crash FFmpeg (30fps CFR, échelle, audio de secours)
#   4. Habillage officiel ZioLabs Web TV (Bandeaux V003, Or #FFD700, Pétrole #09262F)
#   5. Master acoustique broadcast EBU R128 (-14 LUFS)
#   6. Double sentinelle anti-veille Colab (Tourne toute la nuit sans coupure)
#   7. Sauvegarde sécurisée étape par étape dans 00_EXPORTS_FINAUX (Zéro perte)
#   8. Lecteurs vidéo interactifs en direct dans le navigateur
# ==============================================================================

# ==============================================================================
# CELLULE 1 : CONNEXION DRIVE & DOUBLE GARDIEN ANTI-VEILLE NOCTURNE
# ==============================================================================
#@title 1. Initialisation, Double Sentinelle Anti-Veille & Montage Drive
import os, sys, time, json, shutil, threading, subprocess, glob, base64
from pathlib import Path
from IPython.display import Javascript, display, HTML

print("🚀 [1/4] Connexion au Google Drive et activation du gardien nocturne...")

try:
    from google.colab import drive
    if not os.path.exists('/content/drive/MyDrive'):
        drive.mount('/content/drive', force_remount=False)
    DRIVE_ROOT = Path('/content/drive/MyDrive')
    print("✅ Google Drive connecté avec succès !")
except Exception:
    DRIVE_ROOT = Path.home() / "Google Drive"
    print(f"ℹ️ Exécution locale. Racine : {DRIVE_ROOT}")

# Détection intelligente des dossiers
CANDIDATE_DIRS = [
    DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV',
    DRIVE_ROOT / 'Ziolabs_Clips',
    DRIVE_ROOT / 'ZIOLABS_CLIPS',
    DRIVE_ROOT / 'Clips',
    DRIVE_ROOT / 'Videos'
]

ASSETS_DIR = next((c for c in CANDIDATE_DIRS if c.exists()), None)
if ASSETS_DIR is None:
    for root, _, files in os.walk(DRIVE_ROOT):
        if any(f.lower().endswith(('.mp4', '.mov', '.mkv', '.webm')) for f in files):
            ASSETS_DIR = Path(root)
            break

if ASSETS_DIR is None:
    ASSETS_DIR = DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV'
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV' / '00_EXPORTS_FINAUX'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BIBLE_FILE = DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV' / 'bible_ziolabs_catalog.json'

print(f"📂 Dossier Source des Clips : {ASSETS_DIR}")
print(f"📁 Dossier de Sortie Exports : {OUTPUT_DIR}")
print(f"📖 Fichier Bible JSON       : {BIBLE_FILE}")

# Sentinelle Serveur Nocturne (Écrit toutes les 25 secondes)
START_TIME = time.time()
def night_watchdog():
    hb_file = OUTPUT_DIR / ".night_batch_heartbeat.txt"
    counter = 0
    while True:
        try:
            now = time.time()
            el_m = int((now - START_TIME) // 60)
            el_s = int((now - START_TIME) % 60)
            with open(hb_file, "w") as f:
                f.write(f"ZioLabs Night Engine Active | Elapsed: {el_m:02d}m{el_s:02d}s | Time: {now}\n")
            if counter % 12 == 0 and counter > 0:
                print(f"🛡️ [GARDIEN NOCTURNE ACTIF] Traitement en cours depuis {el_m}m {el_s}s — Serveur éveillé.")
            counter += 1
        except: pass
        time.sleep(25)

threading.Thread(target=night_watchdog, daemon=True).start()
print("🛡️ Sentinelle d'arrière-plan activée (Le serveur ne s'arrêtera pas de la nuit).")

# Sentinelle Navigateur (Empêche l'onglet de geler)
display(Javascript('''
function KeepColabAwakeAllNight() {
    console.log("🛡️ [ZioLabs Night Ping] Maintien actif onglet : " + new Date().toLocaleTimeString());
    let btn = document.querySelector("colab-connect-button") || document.querySelector("#connect");
    if (btn) { btn.click(); }
}
setInterval(KeepColabAwakeAllNight, 25000);
'''))
print("⚡ Injection Keep-Alive navigateur effectuée !")


# ==============================================================================
# CELLULE 2 : SCAN COMPLET DES 300+ ASSETS & GÉNÉRATION DE LA BIBLE JSON
# ==============================================================================
#@title 2. Scan & Indexation des Assets dans la Bible ZioLabs
def get_video_info(filepath):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=width,height,codec_name,codec_type",
        "-of", "json", str(filepath)
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            dur = float(data.get('format', {}).get('duration', 0))
            streams = data.get('streams', [])
            v = next((s for s in streams if s.get('codec_type') == 'video'), {})
            a = next((s for s in streams if s.get('codec_type') == 'audio'), None)
            w, h = v.get('width', 0), v.get('height', 0)
            aspect = "16:9" if (w > 0 and w >= h) else "9:16"
            return {"duration": round(dur, 2), "width": w, "height": h, "aspect": aspect, "has_audio": (a is not None)}
    except: pass
    return {"duration": 0, "width": 0, "height": 0, "aspect": "unknown", "has_audio": False}

print("\n🔍 [2/4] Scan approfondi de tous les clips présents sur Google Drive...")
catalog = []
extensions = {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'}

for root, _, files in os.walk(ASSETS_DIR):
    if "00_EXPORTS_FINAUX" in root or "Ziolabs_Outputs" in root: continue
    for file in sorted(files):
        if Path(file).suffix.lower() in extensions and not file.startswith('.'):
            fp = Path(root) / file
            info = get_video_info(fp)
            if info["duration"] <= 0.5: continue
            
            category = fp.parent.name if fp.parent != ASSETS_DIR else "patrimoine"
            try: rel = str(fp.relative_to(DRIVE_ROOT))
            except: rel = str(fp)
            
            catalog.append({
                "filename": file,
                "relative_path": rel,
                "full_path": str(fp),
                "category": category,
                "duration": info["duration"],
                "resolution": f"{info['width']}x{info['height']}",
                "aspect": info["aspect"],
                "has_audio": info["has_audio"],
                "used_count": 0
            })

with open(BIBLE_FILE, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=4, ensure_ascii=False)

clips_16x9 = [c for c in catalog if c["aspect"] == "16:9"]
clips_9x16 = [c for c in catalog if c["aspect"] == "9:16"]

total_hours = sum(c["duration"] for c in catalog) / 3600
print(f"✅ BIBLE ZIOLABS VALIDÉE : {len(catalog)} assets indexés ({total_hours:.1f} heures de contenu au total) !")
print(f"   📺 Clips Format 16:9 (Paysage / Documentaire) : {len(clips_16x9)}")
print(f"   📱 Clips Format 9:16  (Vertical / Shorts Viraux): {len(clips_9x16)}")
print(f"💾 Sauvegarde effectuée dans : {BIBLE_FILE.name}")


# ==============================================================================
# CELLULE 3 : MOTEUR DE PRODUCTION PAR LOTS (NORMALISATION & MONTAGE)
# ==============================================================================
#@title 3. Moteur d'Assemblage Sécurisé & Habillage TV ZioLabs
def normalize_clip(clip, target_aspect="16:9", idx=0):
    """Garantit qu'aucun clip ne fera planter FFmpeg (30fps CFR, échelle, son de secours)."""
    tmp_dir = Path("/tmp/ziolabs_batch_norm")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_file = tmp_dir / f"norm_{idx:03d}.mp4"
    
    tw, th = (1920, 1080) if target_aspect == "16:9" else (1080, 1920)
    vf = f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30"
    
    cmd = ["ffmpeg", "-y", "-i", clip["full_path"]]
    if not clip["has_audio"]:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    else:
        cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2"]
    
    cmd.append(str(out_file))
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_file


def display_player(video_path, width=480, title="Production ZioLabs"):
    """Lecteur vidéo HTML5 intégré dans le notebook Colab pour voir la vidéo immédiatement."""
    try:
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        filename = os.path.basename(video_path)
        
        # Encodage base64 pour affichage direct dans l'onglet
        if size_mb <= 35:
            with open(video_path, "rb") as f: data = base64.b64encode(f.read()).decode()
            src = f"data:video/mp4;base64,{data}"
        else:
            teaser_path = f"/tmp/teaser_{filename}"
            subprocess.run(["ffmpeg", "-y", "-ss", "00:00:00", "-i", video_path, "-t", "40", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24", "-c:a", "aac", teaser_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with open(teaser_path, "rb") as f: data = base64.b64encode(f.read()).decode()
            if os.path.exists(teaser_path): os.remove(teaser_path)
            src = f"data:video/mp4;base64,{data}"

        html = f"""
        <div style="background-color: #09262F; border: 2px solid #FFD700; border-radius: 12px; padding: 15px; margin: 15px 0; max-width: {width}px; font-family: Trebuchet MS, sans-serif; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #103C46; padding-bottom: 6px;">
                <h4 style="color: #FFD700; margin: 0; font-size: 16px;">🎬 {title}</h4>
                <span style="background: #103C46; color: #FAF7F0; padding: 2px 8px; border-radius: 15px; font-size: 11px; border: 1px solid #D08A26;">{size_mb:.1f} MB</span>
            </div>
            <video width="100%" controls autoplay muted loop style="border-radius: 6px; background: #000; max-height: 420px;">
                <source src="{src}" type="video/mp4">
            </video>
            <div style="margin-top: 8px; font-size: 12px; color: #FAF7F0;">
                📁 Enregistré dans : <code>00_EXPORTS_FINAUX/{filename}</code>
            </div>
        </div>
        """
        display(HTML(html))
    except Exception as e:
        print(f"ℹ️ Vidéo prête : {video_path}")


def assemble_batch(clips, output_filename, aspect="16:9", title_banner="ZIOLABS WEB TV"):
    out_path = OUTPUT_DIR / output_filename
    if out_path.exists() and out_path.stat().st_size > 1000000:
        print(f"⏩ Déjà produit précédemment : {output_filename}")
        return
        
    print(f"🎬 Assemblage du lot ({len(clips)} clips en {aspect}) ➔ {output_filename}...")
    norm_files = [normalize_clip(c, target_aspect=aspect, idx=i) for i, c in enumerate(clips)]
    
    list_txt = Path("/tmp/concat_list.txt")
    with open(list_txt, "w", encoding="utf-8") as f:
        for nf in norm_files: f.write(f"file '{nf}'\n")
        
    raw_merged = Path("/tmp/raw_merged.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_txt), "-c", "copy", str(raw_merged)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Habillage officiel ZioLabs Web TV & Normalisation sonore EBU R128 (-14 LUFS)
    if aspect == "16:9":
        vf_overlay = f"drawbox=y=0:h=90:color=0x09262F@0.85:t=fill,drawtext=text='ZIOLABS WEB TV  |  {title_banner}':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=28:x=60:y=32"
        w_player = 680
    else:
        vf_overlay = f"drawbox=y=130:h=120:color=0x09262F@0.9:t=fill,drawtext=text='{title_banner}':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=34:x=(w-text_w)/2:y=172"
        w_player = 360
        
    cmd_final = [
        "ffmpeg", "-y", "-i", str(raw_merged),
        "-vf", vf_overlay,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Nettoyage /tmp pour ne jamais saturer l'espace disque de Colab pendant la nuit
    shutil.rmtree("/tmp/ziolabs_batch_norm", ignore_errors=True)
    if raw_merged.exists(): raw_merged.unlink()
    if list_txt.exists(): list_txt.unlink()
    
    # Affichage du lecteur vidéo interactif en direct
    display_player(out_path, width=w_player, title=f"{title_banner} ({output_filename})")
    print(f"🏆 ÉPISODE FINALISÉ ➔ {out_path.name}")


# ==============================================================================
# CELLULE 4 : PRODUCTION NOCTURNE MASSIVE (16:9 & 9:16)
# ==============================================================================
#@title 4. Lancement de la Production Nocturne Massive Continue
print("\n" + "="*80)
print("🌙 DÉMARRAGE DE LA PRODUCTION NOCTURNE CONTINUE ZIOLABS WEB TV")
print("="*80)

# 1. Traitement des Grands Formats 16:9 (par lots de 5 clips)
LOT_SIZE_16x9 = 5
total_batches_16x9 = (len(clips_16x9) + LOT_SIZE_16x9 - 1) // LOT_SIZE_16x9

print(f"\n📺 Production des Épisodes 16:9 ({total_batches_16x9} lots prévus)...")
for i in range(0, len(clips_16x9), LOT_SIZE_16x9):
    batch = clips_16x9[i:i+LOT_SIZE_16x9]
    if len(batch) >= 2:
        num = (i // LOT_SIZE_16x9) + 1
        cat = batch[0].get("category", "HISTOIRE & TECH").upper()
        out_name = f"ZIOLABS_GRAND_RECUT_EP_{num:03d}_16x9.mp4"
        assemble_batch(batch, out_name, aspect="16:9", title_banner=f"{cat} — LOT #{num}")
        print(f"⏳ Avancement 16:9 : Lot {num}/{total_batches_16x9} terminé.")

# 2. Traitement des Shorts Viraux 9:16 (par lots de 3 clips)
LOT_SIZE_9x16 = 3
total_batches_9x16 = (len(clips_9x16) + LOT_SIZE_9x16 - 1) // LOT_SIZE_9x16

print(f"\n📱 Production des Shorts Viraux 9:16 ({total_batches_9x16} lots prévus)...")
for i in range(0, len(clips_9x16), LOT_SIZE_9x16):
    batch = clips_9x16[i:i+LOT_SIZE_9x16]
    if len(batch) >= 2:
        num = (i // LOT_SIZE_9x16) + 1
        out_name = f"ZIOLABS_SHORT_COMPIL_EP_{num:03d}_9x16.mp4"
        assemble_batch(batch, out_name, aspect="9:16", title_banner="ZIOLABS VIRAL SHORTS")
        print(f"⏳ Avancement 9:16 : Lot {num}/{total_batches_9x16} terminé.")

print("\n" + "="*80)
print("🎉 TOUTE LA PRODUCTION DE NUIT S'EST ACHEVÉE AVEC SUCCÈS !")
print(f"📁 Toutes vos vidéos vous attendent sur Google Drive dans :")
print(f"👉 {OUTPUT_DIR}")
print("="*80)
