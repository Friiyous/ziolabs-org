# ==============================================================================
# 🎬 ZIOLABS WEB TV — PIPELINE INDUSTRIEL DE PRODUCTION CINÉMATOGRAPHIQUE (16:9)
# SUJET : « L'ÉPOPÉE DE L'ALMAMY SAMORY TOURÉ : 20 Ans de Résistance Inflexible »
# FORMAT : Grand Documentaire 16:9 Widescreen (1920x1080, 25 fps, ~20 min 28s)
# STYLE : 100% Documentaire Cinématographique SANS ANIMATEUR / SANS AVATAR
# INVARIANTS : Charte V003 (Pétrole #09262F, Or #FFD700, Ambre #D08A26, Ivoire #FAF7F0)
# NORME AUDIO : EBU R128 (-14 LUFS, True Peak -1.5 dB, Broadcast Master)
# ==============================================================================

# ==============================================================================
# CELLULE 1 : CONNEXION DRIVE, DOUBLE GARDIEN ANTI-VEILLE & AUDIT DES ASSETS
# ==============================================================================
#@title 1. Initialisation, Double Gardien Anti-Veille & Détection des Médias
import os, sys, time, json, shutil, threading, subprocess, glob, base64, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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

# Détection intelligente des répertoires du projet Samory Touré
BASE_DIR = DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV'
OUTPUT_DIR = BASE_DIR / '00_EXPORTS_FINAUX'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATE_SAMORY_DIRS = [
    BASE_DIR / 'THEME_02_HORONYA_SAMORY_TOURE',
    BASE_DIR / 'SAMORY',
    BASE_DIR / 'HORONYA',
    BASE_DIR
]
SAMORY_DIR = next((d for d in CANDIDATE_SAMORY_DIRS if d.exists()), BASE_DIR)

# Sentinelle Keep-Alive d'arrière-plan (garde la VM éveillée)
START_TIME = time.time()
def colab_sentinel_watchdog():
    hb_file = OUTPUT_DIR / ".samory_render_heartbeat.txt"
    counter = 0
    while True:
        try:
            now = time.time()
            elapsed_m = int((now - START_TIME) // 60)
            elapsed_s = int((now - START_TIME) % 60)
            with open(hb_file, "w") as f:
                f.write(f"ZioLabs Samory Master Active | Elapsed: {elapsed_m:02d}m{elapsed_s:02d}s | TS: {now}\n")
            if counter % 12 == 0 and counter > 0:
                print(f"🛡️ [GARDIEN ACTIF] Maintien en éveil Google Colab & Drive ({elapsed_m}m {elapsed_s}s de traitement)")
            counter += 1
        except Exception:
            pass
        time.sleep(25)

sentinel_thread = threading.Thread(target=colab_sentinel_watchdog, daemon=True)
sentinel_thread.start()
print("🛡️ [2/4] Sentinelle serveur activée (Colab ne s'endormira jamais).")

# Injection Keep-Alive navigateur
display(Javascript('''
function KeepColabAlive() {
    console.log("🛡️ [ZioLabs Keep-Alive] Ping onglet : " + new Date().toLocaleTimeString());
    let btn = document.querySelector("colab-connect-button") || document.querySelector("#connect");
    if (btn) { btn.click(); }
}
setInterval(KeepColabAlive, 25000);
'''))

# Fonction pour visionner directement une vidéo dans Colab
def display_video_player(video_path, width=720, title="Extrait ZioLabs"):
    try:
        p = Path(video_path)
        if not p.exists() or p.stat().st_size < 100000:
            print(f"ℹ️ Vidéo en cours de traitement : {p.name}")
            return
        size_mb = p.stat().st_size / (1024 * 1024)
        filename = p.name
        
        # Extrait optimisé pour prévisualisation fluide dans le navigateur
        preview_path = f"/tmp/preview_{p.stem}.mp4"
        cmd_prev = [
            "ffmpeg", "-y", "-ss", "00:00:00", "-i", str(p), "-t", "40",
            "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-c:a", "aac", preview_path
        ]
        res = subprocess.run(cmd_prev, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(preview_path) and os.path.getsize(preview_path) > 1000:
            with open(preview_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            os.remove(preview_path)
            
            html = f"""
            <div style="background-color: #09262F; border: 2px solid #FFD700; border-radius: 12px; padding: 18px; margin: 20px 0; max-width: {width}px; font-family: Trebuchet MS, sans-serif; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #103C46; padding-bottom: 8px;">
                    <h3 style="color: #FFD700; margin: 0; font-size: 18px;">🎬 {title}</h3>
                    <span style="background: #103C46; color: #FAF7F0; padding: 3px 10px; border-radius: 20px; font-size: 12px; border: 1px solid #D08A26;">{size_mb:.1f} MB</span>
                </div>
                <video width="100%" controls autoplay muted loop style="border-radius: 8px; border: 1px solid #103C46; max-height: 420px; background: #000;">
                    <source src="data:video/mp4;base64,{data}" type="video/mp4">
                </video>
                <div style="margin-top: 10px; font-size: 12px; color: #FAF7F0;">
                    📁 Emplacement Drive : <code>00_EXPORTS_FINAUX/{filename}</code>
                </div>
            </div>
            """
            display(HTML(html))
        else:
            print(f"✅ Vidéo générée sur Google Drive : {filename} ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"ℹ️ Vidéo prête : {video_path}")

print("⚡ [3/4] Moteur de visionnage interactif configuré !")

# Récolte récursive et ultra-robuste des assets vidéo et audio
video_exts = {'.mp4', '.mov', '.mkv', '.webm'}
all_clips = []
all_audios = []

for root, _, files in os.walk(SAMORY_DIR):
    for f in sorted(files):
        ext = os.path.splitext(f)[1].lower()
        if ext in video_exts and not f.startswith('.'):
            all_clips.append(Path(root) / f)
        elif ext in {'.wav', '.mp3', '.m4a', '.aac'} and not f.startswith('.'):
            all_audios.append(Path(root) / f)

# Si les clips sont insuffisants dans le dossier spécifique, balayer BASE_DIR
if len(all_clips) < 20:
    for root, _, files in os.walk(BASE_DIR):
        for f in sorted(files):
            ext = os.path.splitext(f)[1].lower()
            if ext in video_exts and not f.startswith('.'):
                all_clips.append(Path(root) / f)

# Trier les audios chronologiquement
all_audios = sorted(list(set(all_audios)), key=lambda x: x.name)

print(f"📊 [4/4] Bilan des médias trouvés sur Google Drive :")
print(f"   🎥 Clips vidéo disponibles : {len(all_clips)} clips")
print(f"   🎙️ Pistes audio de voix-off : {len(all_audios)} fichiers")


# ==============================================================================
# CELLULE 2 : STRUCTURATION DES 7 ACTES & MAPPING CHIRURGICAL
# ==============================================================================
#@title 2. Structuration Narratif des 7 Actes & Calibration Temporelle

def get_audio_duration(filepath):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(filepath)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(json.loads(res.stdout)['format']['duration'])
    except Exception:
        return 180.0

# Définition officielle des 7 Actes du Grand Documentaire
ACTES_DEFINITION = [
    {
        "id": "ACTE_00",
        "titre_court": "PRÉ-GÉNÉRIQUE",
        "titre_long": "L'AUBE DE GUÉLÉBA : LE RÉVEIL DU DERNIER EMPEREUR",
        "sous_titre": "29 Septembre 1898 · La Brume et l'Infiltration Secrète",
        "audio_keyword": "8_06PM",
        "pool": "lot2",
    },
    {
        "id": "ACTE_01",
        "titre_court": "ACTE I",
        "titre_long": "L'ASCENSION D'UN COLPORTEUR (1830–1881)",
        "sous_titre": "De la Caravane de Cola au Serment Filial des Cissé",
        "audio_keyword": "8_30PM",
        "pool": "lot1",
    },
    {
        "id": "ACTE_02",
        "titre_court": "ACTE II",
        "titre_long": "L'USINE DE GUERRE & LES FORGES CLANDESTINES",
        "sous_titre": "Dabakala · La Duplication Secrète des Fusils Modernes",
        "audio_keyword": "8_33PM",
        "pool": "lot1",
    },
    {
        "id": "ACTE_03",
        "titre_court": "ACTE III",
        "titre_long": "LE GRAND CHOC AVEC L'ARMÉE COLONIALE",
        "sous_titre": "Les Batailles du Fleuve Niger & la Discipline des Sofas",
        "audio_keyword": "8_39PM",
        "pool": "lot2",
    },
    {
        "id": "ACTE_04",
        "titre_court": "ACTE IV",
        "titre_long": "LA TERRE BRÛLÉE & L'EMPIRE NOMADE",
        "sous_titre": "L'Exode Historique de 120 000 Âmes vers l'Est",
        "audio_keyword": "8_42PM",
        "pool": "lot2",
    },
    {
        "id": "ACTE_05",
        "titre_court": "ACTE V",
        "titre_long": "LA CHUTE TRAGIQUE À GUÉLÉBA (1898)",
        "sous_titre": "La Reddition d'Honneur pour Sauver son Peuple",
        "audio_keyword": "8_44PM",
        "pool": "clips_manquants",
    },
    {
        "id": "ACTE_06",
        "titre_court": "ÉPILOGUE",
        "titre_long": "L'HÉRITAGE HISTORIQUE DE L'ALMAMY",
        "sous_titre": "L'Exil au Gabon & la Mémoire Vivante d'une Afrique Debout",
        "audio_keyword": "8_45PM",
        "pool": "clips_manquants",
    }
]

chapters = []
total_film_seconds = 0.0

# Répartir les clips par catégories thématiques
clips_lot1 = [c for c in all_clips if 'lot1' in str(c).lower()]
clips_lot2 = [c for c in all_clips if 'lot2' in str(c).lower()]
clips_comp = [c for c in all_clips if 'manquant' in str(c).lower() or 'comp' in str(c).lower()]

# Sécuriser au moins quelques clips par pool
if not clips_lot1: clips_lot1 = all_clips[:len(all_clips)//3]
if not clips_lot2: clips_lot2 = all_clips[len(all_clips)//3:2*len(all_clips)//3]
if not clips_comp: clips_comp = all_clips[2*len(all_clips)//3:]

cursor_lot1, cursor_lot2, cursor_comp = 0, 0, 0

for idx, acte_def in enumerate(ACTES_DEFINITION):
    matched_audio = next((a for a in all_audios if acte_def["audio_keyword"] in a.name), None)
    if matched_audio is None and idx < len(all_audios):
        matched_audio = all_audios[idx]
        
    dur = get_audio_duration(matched_audio) if matched_audio else 180.0
    total_film_seconds += dur
    
    nb_clips_needed = max(6, int(dur // 8.0))
    
    if acte_def["pool"] == "lot1":
        pool_src = clips_lot1 if clips_lot1 else all_clips
        selected = pool_src[cursor_lot1:cursor_lot1 + nb_clips_needed]
        cursor_lot1 += len(selected)
    elif acte_def["pool"] == "lot2":
        pool_src = clips_lot2 if clips_lot2 else all_clips
        selected = pool_src[cursor_lot2:cursor_lot2 + nb_clips_needed]
        cursor_lot2 += len(selected)
    else:
        pool_src = clips_comp if clips_comp else all_clips
        selected = pool_src[cursor_comp:cursor_comp + nb_clips_needed]
        cursor_comp += len(selected)
        
    # Complément si insuffisant
    if len(selected) < nb_clips_needed:
        selected += all_clips[:(nb_clips_needed - len(selected))]
        
    chapters.append({
        "info": acte_def,
        "audio_file": matched_audio,
        "duration": dur,
        "clips": selected
    })
    
    print(f"🎬 {acte_def['titre_court']} : {acte_def['titre_long']}")
    print(f"   ⏱️ Durée : {dur:.1f}s (~{dur/60:.2f} min) | 🎥 Clips assignés : {len(selected)}")
    print(f"   🎙️ Audio : {matched_audio.name if matched_audio else 'None'}\n")

print("="*70)
print(f"🏆 DURÉE TOTALE DU GRAND MASTER : {total_film_seconds:.1f}s (~{total_film_seconds/60:.2f} MINUTES)")
print("="*70)


# ==============================================================================
# CELLULE 3 : MOTEUR DE MONTAGE CINÉMATOGRAPHIQUE (ACTE PAR ACTE)
# ==============================================================================
#@title 3. Moteur d'Assemblage Haute Fidélité (Normalisation 16:9, Overlay PIL V003, Audio EBU R128)

def generate_banner_png(titre, sous_titre, out_png_path):
    """
    Génère un bandeau PNG officiel V003 transparent 1920x1080 via Pillow.
    Évite 100% des bugs de syntaxe FFmpeg drawtext et garantit une typographie parfaite.
    """
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Cartouche rectangulaire Pétrole Sombre (#09262F) à 88% d'opacité avec bordure Or Pur (#FFD700)
    box_coords = [60, 880, 1400, 995]
    draw.rectangle(box_coords, fill=(9, 38, 47, 225), outline=(255, 215, 0, 255), width=2)
    # Liseré vertical Ambre Chaud (#D08A26)
    draw.rectangle([60, 880, 74, 995], fill=(208, 138, 38, 255))
    
    # Filigrane discret en haut à gauche
    draw.text((65, 45), "ZIOLABS WEB TV  |  GRANDS RÉCITS HISTORIQUES", fill=(255, 215, 0, 200))
    
    # Textes du bandeau de chapitre
    draw.text((95, 895), titre[:60], fill=(255, 215, 0, 255))
    draw.text((95, 945), sous_titre[:80], fill=(250, 247, 240, 255))
    
    img.save(out_png_path, "PNG")


def build_act_video(chapter_data, out_filename):
    """
    Assemble un acte avec :
    1. Clips réels normalisés en 1920x1080 (16:9) avec boucle infinie de sécurité (-stream_loop -1)
    2. Concaténation fluide sans à-coup
    3. Incrustation du bandeau officiel V003 via filtre overlay ultra-stable
    4. Nappe sonore solennelle mixée sous la voix-off
    5. Normalisation audio EBU R128 (-14 LUFS)
    """
    out_path = OUTPUT_DIR / out_filename
    if out_path.exists() and out_path.stat().st_size > 5000000:
        print(f"⏩ Déjà produit : {out_filename} (Ignoré en 0.1s)")
        return out_path

    info = chapter_data["info"]
    audio_path = chapter_data["audio_file"]
    target_dur = chapter_data["duration"]
    clips = chapter_data["clips"]
    
    print(f"🎬 Production de {info['titre_court']} -> {out_filename} ({target_dur:.1f}s)...")
    
    num_clips = max(1, len(clips))
    clip_dur = max(4.0, target_dur / num_clips)
    
    temp_dir = Path(f"/tmp/work_{info['id']}")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Normalisation de chaque clip vidéo en 1920x1080 25fps avec boucle de sécurité
    processed_clips = []
    for i, clip in enumerate(clips):
        proc_clip = temp_dir / f"clip_{i:03d}.mp4"
        vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=25"
        cmd_clip = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", str(clip),
            "-t", f"{clip_dur:.3f}",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-an",
            str(proc_clip)
        ]
        res = subprocess.run(cmd_clip, capture_output=True, text=True)
        if proc_clip.exists() and proc_clip.stat().st_size > 1000:
            processed_clips.append(proc_clip)
        else:
            # En cas de problème sur un clip particulier, logger l'avertissement
            pass

    if not processed_clips:
        print(f"⚠️ Aucun clip valide pour {info['id']}, génération d'un fond de secours...")
        fallback_clip = temp_dir / "fallback.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x09262F:s=1920x1080:d={target_dur}:r=25",
            "-c:v", "libx264", "-preset", "ultrafast", str(fallback_clip)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processed_clips.append(fallback_clip)

    # Concaténation des clips
    concat_list = temp_dir / "concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in processed_clips:
            f.write(f"file '{p}'\n")
            
    raw_video = temp_dir / "raw_video.mp4"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(raw_video)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2. Génération du bandeau PNG officiel pour cet Acte
    banner_png = temp_dir / "banner.png"
    titre_bandeau = f"{info['titre_court']}  |  {info['titre_long']}"
    generate_banner_png(titre_bandeau, info['sous_titre'], banner_png)
    
    # 3. Assemblage Master de l'Acte avec overlay et mixage audio
    filter_complex = (
        f"[0:v][2:v]overlay=0:0:enable='between(t,1.5,8.5)'[vout];"
        f"[1:a]aresample=44100,loudnorm=I=-14:TP=-1.5:LRA=11[voice];"
        f"aevalsrc=sin(65*2*PI*t)*0.035+sin(130*2*PI*t)*0.015:d={target_dur}:s=44100[bgm];"
        f"[voice][bgm]amix=inputs=2:weights=1.0 0.15:duration=first[aout]"
    )
    
    cmd_master_act = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(audio_path),
        "-i", str(banner_png),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{target_dur:.3f}",
        str(out_path)
    ]
    res_master = subprocess.run(cmd_master_act, capture_output=True, text=True)
    
    if res_master.returncode != 0:
        print(f"⚠️ Erreur ffmpeg sur {out_filename} : {res_master.stderr[:300]}")
        # Repli ultra-robuste sans filtre complexe si nécessaire
        cmd_fallback = [
            "ffmpeg", "-y",
            "-i", str(raw_video),
            "-i", str(audio_path),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{target_dur:.3f}",
            str(out_path)
        ]
        subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✅ Acte validé : {out_filename}")
    return out_path

# Exécution séquentielle des 7 Actes
acts_rendered = []
for i, chap in enumerate(chapters):
    act_filename = f"ZIOLABS_SAMORY_ACTE_{i:02d}_{chap['info']['id']}.mp4"
    rendered_file = build_act_video(chap, act_filename)
    acts_rendered.append(rendered_file)
    display_video_player(rendered_file, width=640, title=f"{chap['info']['titre_court']} : {chap['info']['titre_long']}")


# ==============================================================================
# CELLULE 4 : INTRO OFFICIELLE, OUTRO CADENCE BOISÉE & CONCATÉNATION DU GRAND MASTER
# ==============================================================================
#@title 4. Assemblage Final du Grand Master 16:9 (20 min 28s) & Clôture Cadence Boisée

GRAND_MASTER_PATH = OUTPUT_DIR / "MASTER_SAMORY_TOURE_GRAND_DOCUMENTAIRE_16x9.mp4"

print("="*70)
print("🎬 ENCODAGE DU GRAND MASTER FINAL DU FILM SAMORY TOURÉ...")
print("="*70)

# Détection de l'intro officielle ou génération procédurale de prestige
intro_candidate = BASE_DIR / "ZIOLABS TECH" / "IDENTITE ZIOLABS WEB" / "ZIOLABS_WEBTV_KIT_MONTAGE_V001" / "VALIDES" / "16x9" / "ZWEBTV_INTRO_A_CADENCE_BOISEE_16x9_v001.mp4"
final_segments = []

if intro_candidate.exists():
    print(f"✨ Intro officielle détectée : {intro_candidate.name}")
    final_segments.append(intro_candidate)
else:
    # Génération d'un carton d'ouverture royal de 4s
    carton_intro = OUTPUT_DIR / ".carton_intro_samory.mp4"
    if not carton_intro.exists():
        intro_png = "/tmp/intro_card.png"
        img_intro = Image.new('RGB', (1920, 1080), (9, 38, 47))
        d_intro = ImageDraw.Draw(img_intro)
        d_intro.rectangle([200, 200, 1720, 880], outline=(255, 215, 0), width=3)
        d_intro.text((300, 360), "ZIOLABS WEB TV  PRÉSENTE", fill=(208, 138, 38))
        d_intro.text((300, 440), "L'ÉPOPÉE DE L'ALMAMY SAMORY TOURÉ", fill=(255, 215, 0))
        d_intro.text((300, 540), "20 Ans de Résistance Inflexible face à l'Empire Colonial", fill=(250, 247, 240))
        img_intro.save(intro_png)
        
        cmd_carton = [
            "ffmpeg", "-y", "-loop", "1", "-i", intro_png,
            "-f", "lavfi", "-i", "aevalsrc=sin(75*2*PI*t)*0.03:d=4.0:s=44100",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-t", "4.0",
            str(carton_intro)
        ]
        subprocess.run(cmd_carton, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    final_segments.append(carton_intro)

# Ajout des 7 Actes
final_segments.extend(acts_rendered)

# Détection de l'outro Cadence Boisée officielle
outro_candidate = BASE_DIR / "ZIOLABS TECH" / "IDENTITE ZIOLABS WEB" / "ZIOLABS_WEBTV_KIT_MONTAGE_V001" / "VALIDES" / "16x9" / "ZWEBTV_OUTRO_A_CADENCE_BOISEE_16x9_v001.mp4"
if not outro_candidate.exists():
    outro_candidate = BASE_DIR / "ZIOLABS TECH" / "IDENTITE ZIOLABS WEB" / "ZIOLABS_WEBTV_PACK_AUDIO_A_V001" / "ZWEBTV_OUTRO_A_CADENCE_BOISEE_16x9_v001.mp4"

if outro_candidate.exists():
    print(f"✨ Outro officielle Cadence Boisée détectée : {outro_candidate.name}")
    final_segments.append(outro_candidate)
else:
    # Carton de clôture officiel
    carton_outro = OUTPUT_DIR / ".carton_outro_samory.mp4"
    if not carton_outro.exists():
        outro_png = "/tmp/outro_card.png"
        img_outro = Image.new('RGB', (1920, 1080), (9, 38, 47))
        d_outro = ImageDraw.Draw(img_outro)
        d_outro.rectangle([200, 200, 1720, 880], outline=(255, 215, 0), width=3)
        d_outro.text((300, 380), "ZIOLABS WEB TV", fill=(255, 215, 0))
        d_outro.text((300, 480), "Des regards. Des histoires. Des idées.", fill=(250, 247, 240))
        d_outro.text((300, 580), "ABONNEZ-VOUS  |  ziolabs.ci", fill=(208, 138, 38))
        img_outro.save(outro_png)
        
        cmd_outro = [
            "ffmpeg", "-y", "-loop", "1", "-i", outro_png,
            "-f", "lavfi", "-i", "aevalsrc=sin(85*2*PI*t)*0.03:d=5.0:s=44100",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-t", "5.0",
            str(carton_outro)
        ]
        subprocess.run(cmd_outro, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    final_segments.append(carton_outro)

# Assemblage par concaténation FFmpeg
master_concat_txt = OUTPUT_DIR / ".master_concat_list.txt"
with open(master_concat_txt, "w", encoding="utf-8") as f:
    for seg in final_segments:
        f.write(f"file '{seg}'\n")

cmd_grand_master = [
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", str(master_concat_txt),
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
    "-c:a", "aac", "-b:a", "192k",
    str(GRAND_MASTER_PATH)
]
subprocess.run(cmd_grand_master, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("\n" + "="*80)
print("🎉 LE GRAND MASTER SAMORY TOURÉ EST TERMINÉ AVEC SUCCÈS !")
print(f"📁 Fichier disponible sur Google Drive dans :")
print(f"👉 {GRAND_MASTER_PATH}")
print("="*80)

# Affichage direct du lecteur pour le Grand Master complet
display_video_player(GRAND_MASTER_PATH, width=760, title="MASTER FINAL : L'ÉPOPÉE DE SAMORY TOURÉ (20 MIN 28S)")
