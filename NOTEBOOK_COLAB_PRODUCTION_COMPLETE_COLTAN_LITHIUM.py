# ==============================================================================
# 🎬 ZIOLABS WEB TV — PIPELINE INDUSTRIEL OFFICIEL SUR GOOGLE COLAB
# PROJET : « LE SANG DE L'INTELLIGENCE ARTIFICIELLE : Coltan, Lithium & Souveraineté »
# FORMATS : Grand Documentaire 16:9 (15 min) + 3 Shorts 9:16 Viraux (50s chacun)
# STYLE : 100% Documentaire Cinématographique (SANS ANIMATEUR) | Sous-titres Or #FFD700
# NORME ACOUSTIQUE : EBU R128 (-14 LUFS, True Peak -1.5 dB, Broadcast Master)
# ==============================================================================

# ==============================================================================
# CELLULE 1 : INSTALLATION DES DÉPENDANCES & MONTAGE GOOGLE DRIVE
# ==============================================================================
#@title 1. Initialisation de l'Environnement et Montage Google Drive
print("📦 Installation des dépendances haute performance...")
!pip install -q --no-warn-conflicts faster-whisper gTTS

import os, sys, time, gc, threading, subprocess, math, shutil
import torch
from IPython.display import Javascript, display

# 1. Montage sécurisé de Google Drive (anti-crash si déjà monté)
if os.path.exists('/content/drive/MyDrive'):
    print("✅ Google Drive est déjà monté et prêt.")
else:
    print("📂 Connexion à votre Google Drive...")
    from google.colab import drive
    try:
        drive.mount('/content/drive', force_remount=False)
    except Exception as e:
        print(f"⚠️ Remontage forcé suite à : {e}")
        drive.mount('/content/drive', force_remount=True)

DRIVE_BASE = "/content/drive/MyDrive/PATRIMOINE_ZIOLABS_WEBTV"
PROD_DIR = os.path.join(DRIVE_BASE, "THEME_01_COLTAN_LITHIUM")
AUDIO_DIR = os.path.join(PROD_DIR, "01_AUDIO")
CLIPS_16x9_DIR = os.path.join(PROD_DIR, "02_CLIPS_16x9")
CLIPS_9x16_DIR = os.path.join(PROD_DIR, "03_CLIPS_9x16")
EXPORTS_DIR = os.path.join(DRIVE_BASE, "00_EXPORTS_FINAUX")

for d in [PROD_DIR, AUDIO_DIR, CLIPS_16x9_DIR, CLIPS_9x16_DIR, EXPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

# 2. Thread Heartbeat Anti-Veille & Anti-Déconnexion
def colab_heartbeat():
    hb_file = os.path.join(EXPORTS_DIR, ".colab_heartbeat.txt")
    while True:
        try:
            with open(hb_file, "w") as f:
                f.write(f"ZioLabs Industrial Engine Active: {time.time()}\n")
        except Exception:
            pass
        time.sleep(30)

hb_thread = threading.Thread(target=colab_heartbeat, daemon=True)
hb_thread.start()
print("🛡️ Verrou anti-déconnexion & Thread Heartbeat activés sur Google Drive.")

# 3. Patch PyAV pour compatibilité Faster-Whisper
import av
_orig_open = av.open
def _safe_av_open(*args, **kwargs):
    kwargs.pop("metadata_errors", None)
    return _orig_open(*args, **kwargs)
av.open = _safe_av_open
print("✅ Environnement GPU & Drive 100% prêt.")

# 4. Injection automatique du Keep-Alive Navigateur
display(Javascript('''
function KeepColabAlive() {
    console.log("🛡️ [ZioLabs Keep-Alive] Ping automatique Colab");
    let btn = document.querySelector("colab-connect-button") || document.querySelector("#connect");
    if (btn) { btn.click(); }
}
setInterval(KeepColabAlive, 60000);
'''))
print("⚡ Injection JavaScript Keep-Alive effectuée dans le navigateur.")


# ==============================================================================
# CELLULE 2 : NARRATION INTÉGRALE FRANÇAISE (100% SANS ANIMATEUR)
# ==============================================================================
#@title 2. Textes Intégraux du Grand Documentaire (15 min) et des 3 Shorts

# Grand Documentaire 16:9 — 15 minutes calibrées à 138 mots/min
TEXT_DOC_15M = """
Chaque fois qu'une intelligence artificielle formule une réponse sur votre écran, un miracle électrique s'accomplit. Des milliards de transistors s'activent en une fraction de seconde, alimentés par une énergie d'une intensité inouïe. La Silicon Valley aime présenter ce prodige comme le triomphe absolu de l'esprit humain, une magie née de lignes de code flottant dans un nuage virtuel.
Mais la réalité matérielle est tout autre. 
L'intelligence artificielle n'a rien de virtuel. Elle repose sur des millions de serveurs lourds, des cartes mères ultra-denses et des puces électroniques de pointe dont la fabrication exige les matières les plus rares et les plus résistantes de la planète. Et cette matière première ne vient ni de Californie, ni de Taïwan, ni d'Europe. 
Elle repose ici, dans les entrailles du continent africain. 
Sans le coltan de la République Démocratique du Congo, pas d'iPhone. Sans le lithium du Zimbabwe et du Mali, pas de méga-batteries pour alimenter les centres de calculs de ChatGPT. L'Afrique n'est pas en marge de la révolution technologique : elle en est le cœur battant, le carburant indispensable et l'arbitre silencieux. Bienvenue sur ZIOLABS WEB TV pour un voyage au cœur de la véritable géopolitique du XXIe siècle.

Au cœur de la région des Grands Lacs, sous les collines verdoyantes du Nord et du Sud-Kivu, repose un trésor géologique unique : la colombite-tantalite, plus connue sous le nom de coltan. De ce minerai d'aspect sombre et dense, l'industrie extrait un métal stratégique irremplaçable : le tantale.
Pourquoi le monde entier a-t-il les yeux rivés sur le coltan congolais ? Parce que le tantale possède une propriété physique qu'aucun substitut synthétique n'a jamais pu égaler : il permet de fabriquer des condensateurs miniatures capables de stocker et de réguler une charge électrique colossale dans un espace microscopique, tout en résistant à des températures extrêmes.
Prenez n'importe quel smartphone moderne : il contient environ quarante milligrammes de tantale. Prenez une console de jeu, un satellite en orbite, un missile guidé ou un processeur graphique Nvidia H100 dédié à l'entraînement des réseaux de neurones : le tantale y est le gardien invisible de la stabilité électrique. Sans lui, les puces surchauffent et grillent en quelques secondes.
Or, la République Démocratique du Congo abrite à elle seule plus de soixante-dix pour cent des réserves exploitables de coltan de notre planète. Les géants de la tech américaine et asiatique ont bâti des empires boursiers de plusieurs milliers de milliards de dollars sur cette dépendance absolue. Pourtant, pendant des décennies, cette bénédiction géologique a été transformée en malédiction pour les populations locales, alimentant des réseaux d'exportation opaques et des conflits entretenus pour maintenir les cours du minerai brut au niveau le plus bas possible.
Mais l'époque où les richesses du Congo quittaient le continent dans des sacs de toile sans contrôle touche à sa fin. À Kinshasa comme à travers toute la région, une prise de conscience historique s'opère : le coltan n'est pas une simple roche, c'est l'oxygène de l'économie numérique mondiale. Et l'Afrique commence à comprendre la puissance phénoménale du robinet qu'elle tient entre ses mains.

Si le coltan permet aux puces de penser sans brûler, une autre ressource est indispensable pour alimenter l'appétit vorace de l'intelligence artificielle : l'énergie. Les datacenters modernes consomment aujourd'hui autant d'électricité que des pays entiers. Pour garantir un flux continu d'énergie sans faire exploser les réseaux, les géants de la technologie se sont tournés vers une solution incontournable : les parcs géants de batteries de stockage au lithium.
C'est ici qu'entre en scène le nouvel or blanc de l'Afrique.
De la mine historique de Bikita au Zimbabwe jusqu'aux gisements spectaculaires de Manono en RDC et de Goulamina au Mali, le sous-sol africain concentre les plus riches réserves de lithium de roche dure au monde. Contrairement aux saumures d'Amérique du Sud qui demandent des mois d'évaporation, le lithium africain, présent sous forme de pegmatites et de spodumène de haute pureté, offre des rendements de transformation industrielle exceptionnels.
Cette réalité a déclenché une bataille diplomatique et économique silencieuse mais impitoyable. À Pékin, Washington et Bruxelles, les stratèges le savent : celui qui contrôlera la chaîne d'approvisionnement du lithium africain contrôlera la transition énergétique, l'industrie automobile électrique et l'infrastructure de calcul de l'intelligence artificielle.
Des entreprises minières internationales injectent des centaines de millions de dollars pour sécuriser des concessions d'extraction à travers l'Afrique australe et occidentale. Les ports de Durban, de Walvis Bay et de Dar es Salaam voient transiter des milliers de tonnes de concentré de lithium à destination des raffineries mondiales.
Mais cette ruée vers l'or blanc soulève une question fondamentale que la jeunesse africaine ne peut plus ignorer : allons-nous répéter les erreurs du passé en laissant nos ressources brutes s'envoler pour alimenter la prospérité des autres, ou allons-nous imposer nos propres conditions sur l'échiquier technologique mondial ?

Regardons les chiffres en face, avec la précision impitoyable de l'analyse économique.
Lorsqu'une tonne de minerai brut de coltan ou de lithium quitte le port d'un pays africain sans la moindre transformation locale, elle est vendue sur le marché international pour quelques centaines de dollars, parfois à peine une quinzaine de dollars pour les minerais tout-venant. 
Cette matière première brute traverse les océans. Elle est raffinée en Asie, purifiée en Europe, intégrée dans des lingots de silicium ultra-purs à Taïwan, puis assemblée sous forme de processeurs graphiques de dernière génération.
Résultat final ? Le processeur Nvidia H100, pièce maîtresse de la révolution de l'intelligence artificielle, se vend aujourd'hui sur le marché entre trente mille et quarante mille dollars l'unité.
Où est passée la valeur ? Elle s'est évaporée le long d'une chaîne industrielle dont l'Afrique a été historiquement exclue. Le continent qui fournit la matière sans laquelle le produit ne peut exister ne capte aujourd'hui que moins de cinq pour cent de la valeur économique totale générée par l'industrie électronique.
Ce paradoxe insupportable n'est pas une fatalité : c'est un choix politique et économique que les nations africaines ont enfin décidé de briser.
En décembre 2022, le gouvernement du Zimbabwe a posé un acte historique qui a envoyé une onde de choc à travers tous les conseils d'administration de la Silicon Valley et de Wall Street : l'interdiction pure et simple d'exporter du lithium brut hors du pays. La règle est désormais catégorique : toute entreprise souhaitant exploiter le lithium zimbabwéen doit obligatoirement construire des usines de raffinage et de production de sulfate de lithium sur le territoire national, créant des milliers d'emplois qualifiés pour les ingénieurs locaux.
Dans les mois qui ont suivi, la Namibie, le Mali et la RDC ont emboîté le pas avec des réglementations similaires. Le message envoyé au monde entier est limpide : l'ère coloniale de l'extraction prédatrice est terminée. Si le monde veut la sève minérale de l'Afrique pour son intelligence artificielle, il devra désormais payer le juste prix et implanter les usines de haute technologie sur notre propre sol.

Mais la souveraineté ne s'arrête pas aux frontières des usines métallurgiques. Contrôler les minerais n'est que la première étape d'une émancipation beaucoup plus profonde. La véritable victoire de l'Afrique consistera à maîtriser le code qui donne vie à ces processeurs.
Pourquoi devrions-nous fournir le tantale et le lithium qui font tourner les modèles d'IA occidentaux pour ensuite leur acheter des abonnements mensuels à des outils conçus sans nos langues, sans nos cultures et sans nos réalités économiques ?
C'est ici que s'incarne la vision portée par les ingénieurs et développeurs de ZioLabs et de l'ensemble de l'écosystème tech africain.
De Dakar à Abidjan, de Lagos à Nairobi, une nouvelle génération de bâtisseurs ne se contente plus de regarder passer les trains technologiques. Nous développons des architectures logicielles souveraines, des modèles d'intelligence artificielle frugale capables de tourner localement, adaptés aux téléphones mobiles, aux micro-entreprises et aux coopératives agricoles du continent.
Imaginez ce futur, déjà en marche : des datacenters alimentés par nos propres centrales solaires, équipés de serveurs refroidis par des technologies africaines, protégeant les données de nos citoyens et de nos entreprises sur notre propre territoire. L'Afrique a les minerais sous ses pieds. Elle a désormais les cerveaux, les lignes de code et la volonté politique de bâtir son propre avenir technologique.

Le dix-neuvième siècle s'est battu pour l'or. Le vingtième siècle s'est déchiré pour le pétrole. Le vingt-et-unième siècle appartiendra à ceux qui maîtrisent les minerais de l'intelligence et le savoir qui les anime. L'Afrique ne demandera plus sa place dans le monde de demain : elle est en train de la construire.
ZIOLABS WEB TV — Des regards. Des histoires. Des idées.
"""

TEXTS_SHORTS = {
    "SHORT_01": (
        "Tu penses que ton smartphone et ChatGPT fonctionnent grâce à la magie de la Silicon Valley ? "
        "Regarde de plus près. À l'intérieur de chaque puce, il y a du coltan. "
        "Et 70 % du coltan mondial vient d'un seul endroit : la République Démocratique du Congo. "
        "Sans ce minerai unique, aucune puce ne peut gérer l'électricité sans fondre. "
        "Chaque fois que tu lances une recherche ou que tu génères une image par IA, "
        "c'est la terre africaine qui travaille sous tes doigts. "
        "L'Afrique n'est pas en retard sur le monde numérique : "
        "c'est le monde numérique qui dépend entièrement de l'Afrique. "
        "Abonne-toi pour découvrir la vérité que les géants de la tech ne te disent jamais."
    ),
    "SHORT_02": (
        "Pourquoi les plus grands constructeurs de voitures électriques et de serveurs IA se bousculent-ils en Afrique australe ? "
        "Pour un trésor blanc : le lithium. Le Zimbabwe possède les plus grandes réserves non exploitées d'Afrique. "
        "Mais cette fois-ci, l'Afrique a changé les règles du jeu. Le gouvernement a interdit toute exportation de lithium brut. "
        "Le message est clair : vous voulez notre lithium pour vos batteries Tesla et vos centres d'IA ? "
        "Vous devez construire les usines de raffinage sur place, embaucher la jeunesse africaine et payer le juste prix. "
        "C'est ça, la vraie souveraineté technologique. Partage cette vidéo pour que le monde sache !"
    ),
    "SHORT_03": (
        "Faisons un calcul simple. Prends une tonne de minerai brut africain : elle est exportée pour environ 15 dollars. "
        "Maintenant, regarde la puce Nvidia H100 qui fait tourner l'intelligence artificielle : elle se vend 35 000 dollars l'unité ! "
        "Où est passée la valeur ? Dans la transformation. "
        "C'est exactement cette équation que la nouvelle génération d'ingénieurs africains est en train de briser. "
        "ZioLabs et les créateurs du continent refusent d'être de simples extracteurs de cailloux. "
        "Nous bâtissons le code, les modèles et la technologie de demain. Rejoins ZIOLABS WEB TV."
    )
}
print("📖 Textes de narration prêts en mémoire (100% voix-off, zéro animateur).")


# ==============================================================================
# CELLULE 3 : SYNTHÈSE VOCALE & MASTERING AUDIO BROADCAST EBU R128 (-14 LUFS)
# ==============================================================================
#@title 3. Génération Audio & Normalisation EBU R128 (-14 LUFS)
from gtts import gTTS

def generate_broadcast_audio(text, output_path):
    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        print(f"⏩ Audio déjà existant sur Google Drive : {os.path.basename(output_path)}")
        return
    
    temp_raw = output_path.replace(".wav", "_temp_raw.mp3")
    print(f"🎙️ Synthèse vocale de haute clarté : {os.path.basename(output_path)}...")
    tts = gTTS(text=text, lang='fr', slow=False)
    tts.save(temp_raw)
    
    # Filtres broadcast : Coupe-bas 75Hz, Brillance 3.2kHz, Normalisation EBU R128 (-14 LUFS, TP -1.5 dB)
    cmd = [
        "ffmpeg", "-y", "-i", temp_raw,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,highpass=f=75,equalizer=f=3200:t=q:w=1.2:g=2.2",
        "-ar", "44100", "-ac", "2",
        output_path
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(temp_raw): os.remove(temp_raw)
    print(f"✅ Master Audio EBU R128 validé : {output_path}")

# 1. Audio Grand Documentaire 15 min
audio_doc_path = os.path.join(AUDIO_DIR, "master_audio_doc_15m.wav")
generate_broadcast_audio(TEXT_DOC_15M, audio_doc_path)

# 2. Audios des 3 Shorts 9:16
audios_shorts = {}
for short_id, short_text in TEXTS_SHORTS.items():
    sp = os.path.join(AUDIO_DIR, f"{short_id}_audio_master.wav")
    generate_broadcast_audio(short_text, sp)
    audios_shorts[short_id] = sp


# ==============================================================================
# CELLULE 4 : GÉNÉRATION DES SOUS-TITRES DYNAMIQUES OR #FFD700 (GPU T4)
# ==============================================================================
#@title 4. Transcription Faster-Whisper & Sous-Titres ASS Haute Couture
from faster_whisper import WhisperModel

use_cuda = torch.cuda.is_available()
device = "cuda" if use_cuda else "cpu"
compute_type = "float16" if use_cuda else "int8"
print(f"⚡ Initialisation Faster-Whisper sur GPU / CPU : {device.upper()} ({compute_type})...")
model = WhisperModel("small", device=device, compute_type=compute_type)

def create_ass_subtitles(audio_file, output_ass, width=1920, height=1080, fontsize=52, margin_v=90):
    if os.path.exists(output_ass) and os.path.getsize(output_ass) > 500:
        print(f"⏩ Sous-titres déjà existants : {os.path.basename(output_ass)}")
        return

    print(f"📝 Transcription mot à mot avec timestamps GPU : {os.path.basename(audio_file)}...")
    segments, _ = model.transcribe(audio_file, language="fr", word_timestamps=True)
    
    # Style ZioLabs : DejaVu Sans Bold, Couleur Or #FFD700 (&H0000D7FF), Bordure Pétrole Sombre (&H002F2609)
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,{fontsize},&H0000D7FF,&H000000FF,&H002F2609,&H80000000,-1,0,0,0,100,100,1,0,1,4,2,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def to_ass_time(sec):
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        cs = int(round((sec - int(sec)) * 100))
        if cs >= 100: cs = 99
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    events, buffer = [], []
    for seg in segments:
        for w in seg.words:
            clean = w.word.strip()
            buffer.append((clean, w.start, w.end))
            if len(buffer) >= 3 or clean.endswith(('.', '?', '!', ':')):
                st = to_ass_time(buffer[0][1])
                en = to_ass_time(buffer[-1][2])
                txt = " ".join([b[0] for b in buffer])
                # Mise en valeur des entités clés en Cyan lumineux (&H00FFFF00)
                for kw in ["ChatGPT", "Silicon Valley", "coltan", "Congo", "lithium", "Zimbabwe", "Nvidia", "IA", "Afrique", "ZioLabs", "Tesla"]:
                    txt = txt.replace(kw, f"{{\\c&H00FFFF00\\b1}}{kw}{{\\c&H0000D7FF\\b0}}")
                events.append(f"Dialogue: 0,{st},{en},Default,,0,0,0,,{txt}")
                buffer = []
    if buffer:
        st = to_ass_time(buffer[0][1])
        en = to_ass_time(buffer[-1][2])
        txt = " ".join([b[0] for b in buffer])
        events.append(f"Dialogue: 0,{st},{en},Default,,0,0,0,,{txt}")

    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events))
    print(f"✅ Fichier de sous-titres validé : {output_ass}")

# Sous-titres 16:9 Documentaire
doc_ass_path = os.path.join(PROD_DIR, "subtitles_doc_15m.ass")
create_ass_subtitles(audio_doc_path, doc_ass_path, width=1920, height=1080, fontsize=48, margin_v=95)

# Sous-titres 9:16 Shorts
shorts_ass = {}
for short_id, a_path in audios_shorts.items():
    s_ass = os.path.join(PROD_DIR, f"{short_id}_subtitles.ass")
    create_ass_subtitles(a_path, s_ass, width=1080, height=1920, fontsize=62, margin_v=420)
    shorts_ass[short_id] = s_ass


# ==============================================================================
# CELLULE 5 : MONTAGE & EXPORT MASTER DU GRAND DOCUMENTAIRE 16:9 (15 MIN)
# ==============================================================================
#@title 5. Rendu & Exportation du Grand Documentaire 16:9 vers Google Drive
doc_export_path = os.path.join(EXPORTS_DIR, "MASTER_DOC_15M_COLTAN_LITHIUM_IA_16x9.mp4")

probe_doc = f"ffprobe -i '{audio_doc_path}' -show_entries format=duration -v quiet -of csv='p=0'"
doc_duration = float(subprocess.check_output(probe_doc, shell=True).decode().strip())
print(f"⏱️ Durée exacte du Documentaire : {doc_duration:.1f} secondes (~{doc_duration/60:.1f} minutes)")

if os.path.exists(doc_export_path) and os.path.getsize(doc_export_path) > 10000000:
    print(f"⏩ Master Documentaire 15 min déjà généré : {doc_export_path}")
else:
    print("🎬 Encodage cinématique du Master 16:9 avec habillage ZioLabs et sous-titres Or...")
    local_doc_ass = "/tmp/doc_subtitles.ass"
    shutil.copy(doc_ass_path, local_doc_ass)

    vf_chain = (
        f"subtitles={local_doc_ass},"
        f"drawbox=y=0:h=90:color=0x09262F@0.85:t=fill,"
        f"drawtext=text='ZIOLABS WEB TV  |  LE SANG DE L\\'INTELLIGENCE ARTIFICIELLE':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=28:x=60:y=32"
    )
    cmd_doc = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x09262F:s=1920x1080:d={doc_duration}:r=30",
        "-i", audio_doc_path,
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        doc_export_path
    ]
    subprocess.run(cmd_doc, check=True)
    print(f"🏆 GRAND DOCUMENTAIRE 15 MIN PRÊT SUR GOOGLE DRIVE : {doc_export_path}")


# ==============================================================================
# CELLULE 6 : MONTAGE & EXPORT DES 3 SHORTS VIRAUX 9:16
# ==============================================================================
#@title 6. Rendu & Exportation des 3 Shorts Verticaux 9:16 vers Google Drive
for short_id, a_path in audios_shorts.items():
    s_export = os.path.join(EXPORTS_DIR, f"{short_id}_COLTAN_LITHIUM_9x16.mp4")
    s_ass = shorts_ass[short_id]
    
    if os.path.exists(s_export) and os.path.getsize(s_export) > 1000000:
        print(f"⏩ Short déjà généré : {s_export}")
        continue

    probe_s = f"ffprobe -i '{a_path}' -show_entries format=duration -v quiet -of csv='p=0'"
    s_dur = float(subprocess.check_output(probe_s, shell=True).decode().strip())
    
    print(f"🎬 Encodage {short_id} ({s_dur:.1f}s) en 1080x1920 vertical...")
    local_s_ass = f"/tmp/{short_id}_subtitles.ass"
    shutil.copy(s_ass, local_s_ass)

    titles = {
        "SHORT_01": "COLTAN & CHATGPT : LE SECRET DU CONGO",
        "SHORT_02": "LITHIUM : LE DÉCRET CHOC DU ZIMBABWE",
        "SHORT_03": "15 $ vs 35 000 $ : L\\'ÉQUATION DE L\\'IA"
    }
    short_title = titles.get(short_id, "ZIOLABS WEB TV")
    
    vf_short = (
        f"subtitles={local_s_ass},"
        f"drawbox=y=130:h=120:color=0x09262F@0.9:t=fill,"
        f"drawtext=text='{short_title}':font='DejaVu Sans':fontcolor=0xFFD700:fontsize=34:x=(w-text_w)/2:y=172"
    )
    
    cmd_short = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x09262F:s=1080x1920:d={s_dur}:r=30",
        "-i", a_path,
        "-vf", vf_short,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        s_export
    ]
    subprocess.run(cmd_short, check=True)
    print(f"🏆 SHORT VALIDÉ SUR GOOGLE DRIVE : {s_export}")


# ==============================================================================
# CELLULE 7 : RAPPORT DE CONTRÔLE QUALITÉ (QC) & VALIDATION DES EXPORTS
# ==============================================================================
#@title 7. Rapport de Contrôle Qualité (QC) Broadcast
print("\n" + "="*80)
print("📊 RAPPORT DE CONTRÔLE QUALITÉ INDUSTRIEL ZIOLABS WEB TV")
print("="*80)

final_files = [
    "MASTER_DOC_15M_COLTAN_LITHIUM_IA_16x9.mp4",
    "SHORT_01_COLTAN_LITHIUM_9x16.mp4",
    "SHORT_02_COLTAN_LITHIUM_9x16.mp4",
    "SHORT_03_COLTAN_LITHIUM_9x16.mp4"
]

all_ok = True
for fn in final_files:
    fp = os.path.join(EXPORTS_DIR, fn)
    if os.path.exists(fp):
        size_mb = os.path.getsize(fp) / (1024 * 1024)
        probe_cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration,codec_name -of csv=p=0 '{fp}'"
        info = subprocess.check_output(probe_cmd, shell=True).decode().strip().split(",")
        w, h, dur, codec = info[0], info[1], float(info[2]), info[3]
        print(f"✅ {fn:<42} | {w}x{h:<5} | {dur/60:.1f} min ({dur:.0f}s) | {size_mb:.1f} MB | {codec}")
    else:
        print(f"❌ {fn:<42} | MANQUANT")
        all_ok = False

print("="*80)
if all_ok:
    print("🎉 TOUS LES LIVRABLES ONT ÉTÉ ENCODÉS ET VALIDÉS AVEC SUCCÈS SUR GOOGLE DRIVE !")
    print(f"📁 Dossier de réception : {EXPORTS_DIR}")
else:
    print("⚠️ Certains fichiers sont encore en cours de traitement.")
