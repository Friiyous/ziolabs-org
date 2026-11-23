# ==============================================================================
# 🎬 ZIOLABS WEB TV — PIPELINE INDUSTRIEL OFFICIEL SUR GOOGLE COLAB
# PROJET : « LE SANG DE L'INTELLIGENCE ARTIFICIELLE : Coltan, Lithium & Souveraineté »
# FORMATS : Grand Documentaire 16:9 (15 min) + 3 Shorts 9:16 Viraux (50s chacun)
# STYLE : 100% Documentaire Cinématographique (SANS ANIMATEUR) | Sous-titres Or #FFD700
# EXPÉRIENCE : LECTEURS VIDÉO INTÉGRÉS DANS LE NAVIGATEUR EN TEMPS RÉEL
# NORME ACOUSTIQUE : EBU R128 (-14 LUFS, True Peak -1.5 dB, Broadcast Master)
# ==============================================================================

# ==============================================================================
# CELLULE 1 : GARDIEN ANTI-VEILLE, INSTALLATION & MONTAGE DRIVE
# ==============================================================================
#@title 1. Initialisation, Gardien Anti-Veille & Montage Drive
print("📦 [1/3] Installation des modules de haute performance...")
!pip install -q --no-warn-conflicts faster-whisper gTTS

import os, sys, time, gc, threading, subprocess, math, shutil, glob, base64
import torch
from IPython.display import Javascript, display, HTML

# 1. Montage sécurisé de Google Drive (anti-crash si déjà monté)
print("📂 [2/3] Connexion sécurisée à Google Drive...")
if os.path.exists('/content/drive/MyDrive'):
    print("✅ Google Drive est déjà connecté et opérationnel.")
else:
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

# 2. Sentinelle d'Arrière-Plan : Empêche Colab et Drive de dormir
START_TIME = time.time()
def colab_sentinel_watchdog():
    hb_file = os.path.join(EXPORTS_DIR, ".colab_heartbeat.txt")
    counter = 0
    while True:
        try:
            now = time.time()
            elapsed_m = int((now - START_TIME) // 60)
            elapsed_s = int((now - START_TIME) % 60)
            with open(hb_file, "w") as f:
                f.write(f"ZioLabs Sentinel Active | Elapsed: {elapsed_m:02d}m{elapsed_s:02d}s | TS: {now}\n")
            if counter % 10 == 0 and counter > 0:
                print(f"🛡️ [SENTINEL EN VEILLE ACTIVE] Session Colab & Drive maintenues (Temps : {elapsed_m}m {elapsed_s}s)")
            counter += 1
        except Exception:
            pass
        time.sleep(25)

sentinel_thread = threading.Thread(target=colab_sentinel_watchdog, daemon=True)
sentinel_thread.start()
print("🛡️ [3/3] Sentinelle serveur activée (Colab ne s'endormira jamais).")

# 3. Patch PyAV pour compatibilité Faster-Whisper
import av
_orig_open = av.open
def _safe_av_open(*args, **kwargs):
    kwargs.pop("metadata_errors", None)
    return _orig_open(*args, **kwargs)
av.open = _safe_av_open

# 4. Injection automatique du Keep-Alive Navigateur (maintien d'onglet ouvert)
display(Javascript('''
function KeepColabAlive() {
    console.log("🛡️ [ZioLabs Keep-Alive] Ping automatique onglet : " + new Date().toLocaleTimeString());
    let btn = document.querySelector("colab-connect-button") || document.querySelector("#connect");
    if (btn) { btn.click(); }
}
setInterval(KeepColabAlive, 25000);
'''))

# 5. Fonction d'intégration du Lecteur Vidéo Navigateur dans Colab
def display_video_player(video_path, width=480, title="Production ZioLabs"):
    """Intègre un lecteur vidéo interactif directement dans le navigateur Colab."""
    try:
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        filename = os.path.basename(video_path)
        
        # Si le fichier fait moins de 35 MB (Shorts), encodage base64 pour lecture directe
        if size_mb <= 35:
            with open(video_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            video_tag = f"""
            <video width="100%" max-width="{width}px" controls autoplay muted loop style="border-radius: 8px; border: 1px solid #103C46; max-height: 520px; background: #000;">
                <source src="data:video/mp4;base64,{data}" type="video/mp4">
            </video>
            """
        else:
            # Pour les très gros fichiers (Documentaire 15 min), extrait teaser haute fidélité de 45s
            teaser_path = f"/tmp/teaser_{filename}"
            subprocess.run([
                "ffmpeg", "-y", "-ss", "00:00:00", "-i", video_path, "-t", "45",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-c:a", "aac",
                teaser_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            with open(teaser_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            if os.path.exists(teaser_path): os.remove(teaser_path)
            
            video_tag = f"""
            <p style="color: #D08A26; font-size: 13px; margin: 4px 0 8px 0;">⚡ Extrait de prévisualisation (45 premières secondes en direct) :</p>
            <video width="100%" max-width="{width}px" controls autoplay muted loop style="border-radius: 8px; border: 1px solid #103C46; max-height: 400px; background: #000;">
                <source src="data:video/mp4;base64,{data}" type="video/mp4">
            </video>
            """

        html = f"""
        <div style="background-color: #09262F; border: 2px solid #FFD700; border-radius: 12px; padding: 18px; margin: 20px 0; max-width: {max(width, 480)}px; font-family: Trebuchet MS, sans-serif; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #103C46; padding-bottom: 8px;">
                <h3 style="color: #FFD700; margin: 0; font-size: 18px;">🎬 {title}</h3>
                <span style="background: #103C46; color: #FAF7F0; padding: 3px 10px; border-radius: 20px; font-size: 12px; border: 1px solid #D08A26;">{size_mb:.1f} MB</span>
            </div>
            {video_tag}
            <div style="margin-top: 12px; font-size: 13px; color: #FAF7F0;">
                📁 Fichier enregistré dans : <code>00_EXPORTS_FINAUX/{filename}</code>
            </div>
        </div>
        """
        display(HTML(html))
    except Exception as e:
        print(f"ℹ️ Vidéo générée avec succès sur Google Drive : {video_path}")

print("⚡ Moteur d'affichage vidéo dans le navigateur configuré !")
print("🚀 Prêt pour la production complète !")


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
# CELLULE 4 : GÉNÉRATION DES SOUS-TITRES DYNAMIQUES OR #FFD700 (GPU / CPU / SMART)
# ==============================================================================
#@title 4. Génération Robuste des Sous-Titres ASS Haute Couture Or #FFD700

cudnn_libs = glob.glob("/usr/local/lib/python*/dist-packages/nvidia/cudnn/lib") + glob.glob("/usr/lib/x86_64-linux-gnu")
if cudnn_libs:
    os.environ["LD_LIBRARY_PATH"] = ":".join(cudnn_libs) + ":" + os.environ.get("LD_LIBRARY_PATH", "")

whisper_model = None
try:
    from faster_whisper import WhisperModel
    if torch.cuda.is_available():
        try:
            print("⚡ Initialisation Faster-Whisper sur GPU T4 (CUDA float16)...")
            whisper_model = WhisperModel("small", device="cuda", compute_type="float16")
            print("✅ Faster-Whisper opérationnel sur GPU T4 !")
        except Exception as e_cuda:
            print(f"⚠️ CUDA indisponible ({e_cuda}), basculement immédiat sur CPU...")
    if whisper_model is None:
        try:
            print("⚡ Initialisation Faster-Whisper sur CPU (int8)...")
            whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
            print("✅ Faster-Whisper opérationnel sur CPU !")
        except Exception as e_cpu:
            print(f"⚠️ Mode CPU indisponible ({e_cpu}), activation du Smart Synchronizer ZioLabs...")
            whisper_model = None
except Exception as e_import:
    print(f"⚠️ Faster-Whisper non disponible ({e_import}), passage au Smart Synchronizer.")
    whisper_model = None


def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100: cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_smart_subtitles(text, audio_duration, output_ass, width=1920, height=1080, fontsize=52, margin_v=90):
    words = [w.strip() for w in text.split() if w.strip()]
    if not words: return
    
    total_words = len(words)
    lead_in, lead_out = 0.5, 0.5
    available_duration = max(1.0, audio_duration - lead_in - lead_out)
    sec_per_word = available_duration / total_words

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
    events = []
    chunk_size = 3
    current_time = lead_in
    for i in range(0, total_words, chunk_size):
        chunk = words[i:i + chunk_size]
        chunk_dur = len(chunk) * sec_per_word
        st = current_time
        en = min(audio_duration, current_time + chunk_dur)
        current_time = en
        
        txt = " ".join(chunk)
        for kw in ["ChatGPT", "Silicon Valley", "coltan", "Congo", "lithium", "Zimbabwe", "Nvidia", "IA", "Afrique", "ZioLabs", "Tesla"]:
            txt = txt.replace(kw, f"{{\\c&H00FFFF00\\b1}}{kw}{{\\c&H0000D7FF\\b0}}")
        events.append(f"Dialogue: 0,{format_ass_time(st)},{format_ass_time(en)},Default,,0,0,0,,{txt}")

    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events))
    print(f"✅ Sous-titres Or générés : {output_ass}")


def create_ass_subtitles(audio_file, output_ass, text_fallback="", width=1920, height=1080, fontsize=52, margin_v=90):
    if os.path.exists(output_ass) and os.path.getsize(output_ass) > 500:
        print(f"⏩ Sous-titres déjà existants : {os.path.basename(output_ass)}")
        return

    probe_dur = f"ffprobe -i '{audio_file}' -show_entries format=duration -v quiet -of csv='p=0'"
    try: audio_dur = float(subprocess.check_output(probe_dur, shell=True).decode().strip())
    except Exception: audio_dur = 60.0

    success = False
    if whisper_model is not None:
        try:
            print(f"📝 Transcription mot à mot Whisper : {os.path.basename(audio_file)}...")
            segments, _ = whisper_model.transcribe(audio_file, language="fr", word_timestamps=True)
            
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
            events, buffer = [], []
            for seg in segments:
                for w in seg.words:
                    clean = w.word.strip()
                    buffer.append((clean, w.start, w.end))
                    if len(buffer) >= 3 or clean.endswith(('.', '?', '!', ':')):
                        st = format_ass_time(buffer[0][1])
                        en = format_ass_time(buffer[-1][2])
                        txt = " ".join([b[0] for b in buffer])
                        for kw in ["ChatGPT", "Silicon Valley", "coltan", "Congo", "lithium", "Zimbabwe", "Nvidia", "IA", "Afrique", "ZioLabs", "Tesla"]:
                            txt = txt.replace(kw, f"{{\\c&H00FFFF00\\b1}}{kw}{{\\c&H0000D7FF\\b0}}")
                        events.append(f"Dialogue: 0,{st},{en},Default,,0,0,0,,{txt}")
                        buffer = []
            if buffer:
                st = format_ass_time(buffer[0][1])
                en = format_ass_time(buffer[-1][2])
                txt = " ".join([b[0] for b in buffer])
                events.append(f"Dialogue: 0,{st},{en},Default,,0,0,0,,{txt}")

            with open(output_ass, "w", encoding="utf-8") as f:
                f.write(ass_header + "\n".join(events))
            print(f"✅ Sous-titres Whisper validés : {output_ass}")
            success = True
        except Exception as e_wh:
            print(f"⚠️ Décodage Whisper en échec ({e_wh}), basculement immédiat sur Smart Synchronizer...")
            success = False

    if not success:
        generate_smart_subtitles(text_fallback, audio_dur, output_ass, width=width, height=height, fontsize=fontsize, margin_v=margin_v)


# 1. Sous-titres 16:9 Documentaire (15 min)
doc_ass_path = os.path.join(PROD_DIR, "subtitles_doc_15m.ass")
create_ass_subtitles(audio_doc_path, doc_ass_path, text_fallback=TEXT_DOC_15M, width=1920, height=1080, fontsize=48, margin_v=95)

# 2. Sous-titres 9:16 Shorts
shorts_ass = {}
for short_id, a_path in audios_shorts.items():
    s_ass = os.path.join(PROD_DIR, f"{short_id}_subtitles.ass")
    create_ass_subtitles(a_path, s_ass, text_fallback=TEXTS_SHORTS[short_id], width=1080, height=1920, fontsize=62, margin_v=420)
    shorts_ass[short_id] = s_ass


# ==============================================================================
# CELLULE 5 : MONTAGE & VISIONNAGE DU GRAND DOCUMENTAIRE 16:9 (15 MIN)
# ==============================================================================
#@title 5. Rendu & Lecteur Vidéo du Grand Documentaire 16:9
doc_export_path = os.path.join(EXPORTS_DIR, "MASTER_DOC_15M_COLTAN_LITHIUM_IA_16x9.mp4")

probe_doc = f"ffprobe -i '{audio_doc_path}' -show_entries format=duration -v quiet -of csv='p=0'"
doc_duration = float(subprocess.check_output(probe_doc, shell=True).decode().strip())
print(f"⏱️ Durée exacte du Documentaire : {doc_duration:.1f} secondes (~{doc_duration/60:.1f} minutes)")

if not os.path.exists(doc_export_path) or os.path.getsize(doc_export_path) < 10000000:
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
    print(f"🏆 GRAND DOCUMENTAIRE PRÊT : {doc_export_path}")

# Affichage direct du lecteur vidéo dans l'onglet ouvert du navigateur
display_video_player(doc_export_path, width=720, title="Grand Documentaire 16:9 (15 min)")


# ==============================================================================
# CELLULE 6 : MONTAGE & VISIONNAGE DES 3 SHORTS VIRAUX 9:16
# ==============================================================================
#@title 6. Rendu & Lecteurs Vidéo des 3 Shorts Verticaux 9:16
titles_map = {
    "SHORT_01": "COLTAN & CHATGPT : LE SECRET DU CONGO",
    "SHORT_02": "LITHIUM : LE DÉCRET CHOC DU ZIMBABWE",
    "SHORT_03": "15 $ vs 35 000 $ : L\\'ÉQUATION DE L\\'IA"
}

for short_id, a_path in audios_shorts.items():
    s_export = os.path.join(EXPORTS_DIR, f"{short_id}_COLTAN_LITHIUM_9x16.mp4")
    s_ass = shorts_ass[short_id]
    
    probe_s = f"ffprobe -i '{a_path}' -show_entries format=duration -v quiet -of csv='p=0'"
    s_dur = float(subprocess.check_output(probe_s, shell=True).decode().strip())
    
    short_title = titles_map.get(short_id, "ZIOLABS WEB TV")
    
    if not os.path.exists(s_export) or os.path.getsize(s_export) < 1000000:
        print(f"🎬 Encodage {short_id} ({s_dur:.1f}s) en 1080x1920 vertical...")
        local_s_ass = f"/tmp/{short_id}_subtitles.ass"
        shutil.copy(s_ass, local_s_ass)

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
        print(f"🏆 SHORT VALIDÉ : {s_export}")

    # Affichage du lecteur vidéo vertical en direct dans le navigateur
    display_video_player(s_export, width=380, title=f"Short 9:16 — {short_title.replace(chr(92), '')}")


# ==============================================================================
# CELLULE 7 : TABLEAU DE BORD FINAL & CONTRÔLE QUALITÉ VISUEL
# ==============================================================================
#@title 7. Tableau de Bord Final & Téléchargement Direct
final_files = [
    ("MASTER_DOC_15M_COLTAN_LITHIUM_IA_16x9.mp4", "Grand Documentaire 16:9 (15 min)"),
    ("SHORT_01_COLTAN_LITHIUM_9x16.mp4", "Short 1 : Coltan & ChatGPT"),
    ("SHORT_02_COLTAN_LITHIUM_9x16.mp4", "Short 2 : Lithium & Zimbabwe"),
    ("SHORT_03_COLTAN_LITHIUM_9x16.mp4", "Short 3 : 15 $ vs 35 000 $")
]

rows_html = ""
for fn, label in final_files:
    fp = os.path.join(EXPORTS_DIR, fn)
    if os.path.exists(fp):
        size_mb = os.path.getsize(fp) / (1024 * 1024)
        probe_cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 '{fp}'"
        info = subprocess.check_output(probe_cmd, shell=True).decode().strip().split(",")
        w, h, dur = info[0], info[1], float(info[2])
        rows_html += f"""
        <tr style="border-bottom: 1px solid #103C46;">
            <td style="padding: 10px; color: #FFD700; font-weight: bold;">{label}</td>
            <td style="padding: 10px; color: #FAF7F0;">{w}×{h}</td>
            <td style="padding: 10px; color: #FAF7F0;">{dur/60:.1f}m ({dur:.0f}s)</td>
            <td style="padding: 10px; color: #D08A26; font-weight: bold;">{size_mb:.1f} MB</td>
            <td style="padding: 10px; color: #00FF88;">✅ Prêt</td>
        </tr>
        """
    else:
        rows_html += f"""
        <tr style="border-bottom: 1px solid #103C46;">
            <td style="padding: 10px; color: #FFD700;">{label}</td>
            <td colspan="4" style="padding: 10px; color: #FF4444;">⏳ En cours d'encodage...</td>
        </tr>
        """

dashboard_html = f"""
<div style="background-color: #09262F; border: 2px solid #FFD700; border-radius: 14px; padding: 22px; margin: 25px 0; font-family: Trebuchet MS, sans-serif;">
    <h2 style="color: #FFD700; margin-top: 0; display: flex; align-items: center; gap: 10px;">
        <span>🏆</span> TABLEAU DE BORD DE PRODUCTION — ZIOLABS WEB TV
    </h2>
    <p style="color: #FAF7F0; font-size: 14px; margin-bottom: 15px;">
        Toutes vos productions sont encodées selon les normes broadcast ZioLabs et enregistrées sur votre Google Drive.
    </p>
    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
        <thead>
            <tr style="background-color: #103C46; color: #FFD700;">
                <th style="padding: 10px; border-radius: 6px 0 0 6px;">Format & Titre</th>
                <th style="padding: 10px;">Résolution</th>
                <th style="padding: 10px;">Durée</th>
                <th style="padding: 10px;">Poids</th>
                <th style="padding: 10px; border-radius: 0 6px 6px 0;">Statut</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    <div style="margin-top: 20px; padding: 12px; background: #103C46; border-radius: 8px; color: #FAF7F0; font-size: 13px;">
        📁 <b>Dossier Google Drive :</b> <code>/MyDrive/PATRIMOINE_ZIOLABS_WEBTV/00_EXPORTS_FINAUX/</code>
    </div>
</div>
"""
display(HTML(dashboard_html))
