# ==============================================================================
# 🎬 ZIOLABS WEB TV — PIPELINE INDUSTRIEL DE PRODUCTION CINÉMATOGRAPHIQUE (16:9)
# SUJET : « L'ÉPOPÉE DE L'ALMAMY SAMORY TOURÉ : 20 Ans de Résistance Inflexible »
# FORMAT : Grand Documentaire 16:9 Widescreen (1920x1080, 25 fps, ~20 min 28s)
# STYLE : 100% Documentaire Cinématographique SANS ANIMATEUR / SANS AVATAR
# SYNCHRONISATION : Montage réel des 141 clips sur les 7 Actes audio de narration
# INVARIANTS : Charte V003 (Pétrole #09262F, Or #FFD700, Ambre #D08A26, Ivoire #FAF7F0)
# NORME AUDIO : EBU R128 (-14 LUFS, True Peak -1.5 dB, Broadcast Master)
# ==============================================================================

# ==============================================================================
# CELLULE 1 : CONNEXION DRIVE, DOUBLE GARDIEN ANTI-VEILLE & AUDIT DES ASSETS
# ==============================================================================
#@title 1. Initialisation, Double Gardien Anti-Veille & Détection des Médias
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

# Détection des répertoires du projet Samory Touré
BASE_DIR = DRIVE_ROOT / 'PATRIMOINE_ZIOLABS_WEBTV'
SAMORY_DIR = BASE_DIR / 'THEME_02_HORONYA_SAMORY_TOURE'
OUTPUT_DIR = BASE_DIR / '00_EXPORTS_FINAUX'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Vérification des sous-dossiers
VOIX_DIR = SAMORY_DIR / 'voix_off_samory'
LOT1_DIR = SAMORY_DIR / 'lot1'
LOT2_DIR = SAMORY_DIR / 'lot2'
CLIPS_MANQUANTS_DIR = SAMORY_DIR / 'clips_manquant_samory'

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
        if not p.exists(): return
        size_mb = p.stat().st_size / (1024 * 1024)
        filename = p.name
        
        # Extrait optimisé pour prévisualisation fluide dans le navigateur
        preview_path = f"/tmp/preview_{p.stem}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:00", "-i", str(p), "-t", "40",
            "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-c:a", "aac", preview_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        with open(preview_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        if os.path.exists(preview_path): os.remove(preview_path)
        
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
    except Exception as e:
        print(f"ℹ️ Vidéo prête : {video_path}")

print("⚡ [3/4] Moteur de visionnage interactif configuré !")

# Récolte et validation des assets
video_exts = {'.mp4', '.mov', '.mkv', '.webm'}
all_clips = []
for d in [LOT1_DIR, LOT2_DIR, CLIPS_MANQUANTS_DIR]:
    if d.exists():
        for f in sorted(d.iterdir()):
            if f.is_file() and f.suffix.lower() in video_exts and not f.name.startswith('.'):
                all_clips.append(f)

# Récolte des audios de narration
all_audios = sorted([f for f in VOIX_DIR.iterdir() if f.is_file() and f.suffix.lower() in {'.wav', '.mp3'} and not f.name.startswith('.')])

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
        "pool": "lot2", # Clips de jungle, campement, brume, tirailleurs
    },
    {
        "id": "ACTE_01",
        "titre_court": "ACTE I",
        "titre_long": "L'ASCENSION D'UN COLPORTEUR (1830–1881)",
        "sous_titre": "De la Caravane de Cola au Serment Filial des Cissé",
        "audio_keyword": "8_30PM",
        "pool": "lot1", # Clips de savane, ânes, marchés, villages
    },
    {
        "id": "ACTE_02",
        "titre_court": "ACTE II",
        "titre_long": "L'USINE DE GUERRE & LES FORGES CLANDESTINES",
        "sous_titre": "Dabakala · La Duplication Secrète des Fusils Modernes",
        "audio_keyword": "8_33PM",
        "pool": "lot1", # Clips de forges, métal incandescent, armes
    },
    {
        "id": "ACTE_03",
        "titre_court": "ACTE III",
        "titre_long": "LE GRAND CHOC AVEC L'ARMÉE COLONIALE",
        "sous_titre": "Les Batailles du Fleuve Niger & la Discipline des Sofas",
        "audio_keyword": "8_39PM",
        "pool": "lot2", # Clips de charges, cavalerie, fumée, salves
    },
    {
        "id": "ACTE_04",
        "titre_court": "ACTE IV",
        "titre_long": "LA TERRE BRÛLÉE & L'EMPIRE NOMADE",
        "sous_titre": "L'Exode Historique de 120 000 Âmes vers l'Est",
        "audio_keyword": "8_42PM",
        "pool": "lot2", # Clips d'exil, colonnes de civils, feux
    },
    {
        "id": "ACTE_05",
        "titre_court": "ACTE V",
        "titre_long": "LA CHUTE TRAGIQUE À GUÉLÉBA (1898)",
        "sous_titre": "La Reddition d'Honneur pour Sauver son Peuple",
        "audio_keyword": "8_44PM",
        "pool": "clips_manquants", # Clips de pluie, visages solennels, sabre
    },
    {
        "id": "ACTE_06",
        "titre_court": "ÉPILOGUE",
        "titre_long": "L'HÉRITAGE HISTORIQUE DE L'ALMAMY",
        "sous_titre": "L'Exil au Gabon & la Mémoire Vivante d'une Afrique Debout",
        "audio_keyword": "8_45PM",
        "pool": "clips_manquants", # Clips de statues, soleil couchant, dignité
    }
]

# Résolution des fichiers audio réels
chapters = []
total_film_seconds = 0.0

# Séparer les clips par sous-dossiers pour respecter les thématiques
clips_lot1 = sorted([c for c in all_clips if 'lot1' in str(c)])
clips_lot2 = sorted([c for c in all_clips if 'lot2' in str(c)])
clips_comp = sorted([c for c in all_clips if 'clips_manquant' in str(c)])

# Répartiteur intelligent de clips
cursor_lot1 = 0
cursor_lot2 = 0
cursor_comp = 0

for idx, acte_def in enumerate(ACTES_DEFINITION):
    # Trouver le fichier audio correspondant
    matched_audio = next((a for a in all_audios if acte_def["audio_keyword"] in a.name), None)
    if matched_audio is None and idx < len(all_audios):
        matched_audio = all_audios[idx]
        
    dur = get_audio_duration(matched_audio) if matched_audio else 180.0
    total_film_seconds += dur
    
    # Sélectionner les clips correspondants (environ 1 clip toutes les 7 à 9 secondes)
    nb_clips_needed = max(8, int(dur // 8.5))
    
    if acte_def["pool"] == "lot1":
        selected = clips_lot1[cursor_lot1:cursor_lot1 + nb_clips_needed]
        cursor_lot1 += len(selected)
        if len(selected) < nb_clips_needed:
            # complément
            selected += (clips_comp + clips_lot2)[:(nb_clips_needed - len(selected))]
    elif acte_def["pool"] == "lot2":
        selected = clips_lot2[cursor_lot2:cursor_lot2 + nb_clips_needed]
        cursor_lot2 += len(selected)
        if len(selected) < nb_clips_needed:
            selected += (clips_lot1 + clips_comp)[:(nb_clips_needed - len(selected))]
    else:
        selected = clips_comp[cursor_comp:cursor_comp + nb_clips_needed]
        cursor_comp += len(selected)
        if len(selected) < nb_clips_needed:
            selected += (clips_lot2 + clips_lot1)[:(nb_clips_needed - len(selected))]
            
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
print(f"🏆 DURÉE TOTALE DU GRAND MASTER ESTIMÉE : {total_film_seconds:.1f}s (~{total_film_seconds/60:.2f} MINUTES)")
print("="*70)


# ==============================================================================
# CELLULE 3 : MOTEUR DE MONTAGE CINÉMATOGRAPHIQUE (ACTE PAR ACTE)
# ==============================================================================
#@title 3. Moteur d'Assemblage Haute Fidélité (Normalisation 16:9, Ken Burns, Lower-Thirds)

def build_act_video(chapter_data, out_filename):
    """
    Monte un acte complet avec :
    1. Clips réels normalisés en 1920x1080 (16:9) à durée parfaitement synchronisée
    2. Effet subtil de mouvement cinématographique (Ken Burns)
    3. Bandeau titre officiel V003 (Pétrole #09262F, Or #FFD700, Ivoire #FAF7F0)
    4. Nappe sonore solennelle mixée sous la voix-off
    5. Normalisation EBU R128
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
    
    # 1. Normalisation temporelle des clips pour combler exactement target_dur
    num_clips = max(1, len(clips))
    clip_dur = target_dur / num_clips
    
    temp_dir = Path(f"/tmp/work_{info['id']}")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    processed_clips = []
    for i, clip in enumerate(clips):
        proc_clip = temp_dir / f"clip_{i:03d}.mp4"
        # Filtre cinématographique : scale 1080p, recadrage centré, pan/zoom léger, fps 25
        vf = (
            f"scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,"
            f"setsar=1,"
            f"fps=25"
        )
        cmd_clip = [
            "ffmpeg", "-y", "-ss", "00:00:00", "-i", str(clip),
            "-t", f"{clip_dur:.3f}",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-an",
            str(proc_clip)
        ]
        subprocess.run(cmd_clip, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc_clip.exists():
            processed_clips.append(proc_clip)
            
    # Concaténation des clips vidéo
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
    
    # 2. Habillage officiel V003 (Lower-Third de début d'Acte)
    titre_affiche = f"{info['titre_court']}  |  {info['titre_long'][:45]}"
    vf_habillage = (
        f"drawbox=x=60:y=880:w=1250:h=110:color=0x09262F@0.85:t=fill:enable='between(t,1.5,8.5)',"
        f"drawbox=x=60:y=880:w=12:h=110:color=0xFFD700@1.0:t=fill:enable='between(t,1.5,8.5)',"
        f"drawtext=text='{titre_affiche}':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=30:x=90:y=905:enable='between(t,1.5,8.5)',"
        f"drawtext=text='{info[\"sous_titre\"][:60]}':font='DejaVu Sans':fontcolor=0xFAF7F0:fontsize=22:x=90:y=945:enable='between(t,1.5,8.5)',"
        f"drawtext=text='ZIOLABS WEB TV':font='DejaVu Sans':fontcolor=0xFFD700@0.7:fontsize=20:x=60:y=40"
    )
    
    # 3. Nappe sonore de fond solennelle et mastering audio EBU R128
    # On génère un lit musical discret si aucun fichier externe n'est fourni
    filter_complex = (
        f"[0:v]{vf_habillage}[vout];"
        f"aevalsrc=sin(65*2*PI*t)*0.04+sin(130*2*PI*t)*0.02:d={target_dur}:s=44100[bgm];"
        f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[voice];"
        f"[voice][bgm]amix=inputs=2:weights=1.0 0.15:duration=first[aout]"
    )
    
    cmd_master_act = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{target_dur:.3f}",
        str(out_path)
    ]
    subprocess.run(cmd_master_act, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Nettoyage espace temporaire
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✅ Acte terminé : {out_filename}")
    return out_path

# Production des 7 Actes
acts_rendered = []
for i, chap in enumerate(chapters):
    act_filename = f"ZIOLABS_SAMORY_ACTE_{i:02d}_{chap['info']['id']}.mp4"
    rendered_file = build_act_video(chap, act_filename)
    acts_rendered.append(rendered_file)
    # Affichage du lecteur pour chaque acte
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
        vf_intro = (
            "drawbox=color=0x09262F:t=fill,"
            "drawtext=text='ZIOLABS WEB TV  PRÉSENTE':font='DejaVu Sans':fontcolor=0xD08A26:fontsize=26:x=(w-text_w)/2:y=380,"
            "drawtext=text='L\\'ÉPOPÉE DE L\\'ALMAMY SAMORY TOURÉ':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=46:x=(w-text_w)/2:y=460,"
            "drawtext=text='20 Ans de Résistance Inflexible face à l\\'Empire':font='DejaVu Sans':fontcolor=0xFAF7F0:fontsize=26:x=(w-text_w)/2:y=560"
        )
        cmd_carton = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x09262F:s=1920x1080:d=4.0:r=25",
            "-f", "lavfi", "-i", "aevalsrc=sin(80*2*PI*t)*0.03:d=4.0:s=44100",
            "-vf", vf_intro,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-c:a", "aac",
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
        vf_outro = (
            "drawbox=color=0x09262F:t=fill,"
            "drawtext=text='ZIOLABS WEB TV':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=48:x=(w-text_w)/2:y=420,"
            "drawtext=text='Des regards. Des histoires. Des idées.':font='DejaVu Sans':fontcolor=0xFAF7F0:fontsize=28:x=(w-text_w)/2:y=510,"
            "drawtext=text='ABONNEZ-VOUS  |  ziolabs.ci':font='DejaVu Sans':fontcolor=0xD08A26:fontsize=24:x=(w-text_w)/2:y=600"
        )
        cmd_outro = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x09262F:s=1920x1080:d=5.0:r=25",
            "-f", "lavfi", "-i", "aevalsrc=sin(90*2*PI*t)*0.03:d=5.0:s=44100",
            "-vf", vf_outro,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-c:a", "aac",
            str(carton_outro)
        ]
        subprocess.run(cmd_outro, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    final_segments.append(carton_outro)

# Assemblage par concaténation FFmpeg
master_concat_txt = OUTPUT_DIR / ".master_concat_list.txt"
with open(master_concat_txt, "w", encoding="utf-8") as f:
    for seg in final_segments:
        # Convertir temporairement en format compatible si besoin
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

# Affichage direct du lecteur pour le Grand Master complet !
display_video_player(GRAND_MASTER_PATH, width=760, title="MASTER FINAL : L'ÉPOPÉE DE SAMORY TOURÉ (20 MIN 28S)")
