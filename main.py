import edge_tts
import PyPDF2
import asyncio
import os
import time
from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return {"Full_Document": text}

def extract_chapters_from_epub(epub_path):
    book = epub.read_epub(epub_path)
    chapters = {}
    chapter_number = 1
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), "html.parser")

        heading = soup.find(['h1', 'h2', 'h3'])
        title = heading.text.strip() if heading else f"Chapitre_{chapter_number}"
        text = soup.get_text(separator="\n", strip=True)
        if len(text) > 100:
            chapters[title] = text
            chapter_number += 1
    return chapters

async def text_to_speech(text, output_audio_path, voice="fr-FR-VivienneMultilingualNeural"): # Changez la voix ici
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(output_audio_path)

def process_file(input_path, output_dir):
    ext = os.path.splitext(input_path)[-1].lower()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if ext == ".pdf":
        chapters = extract_text_from_pdf(input_path)
    elif ext == ".epub":
        chapters = extract_chapters_from_epub(input_path)
    else:
        raise ValueError("Format non supporté. Utilisez un PDF ou EPUB.")

    total_chapters = len(chapters)
    print(f"Nombre total de chapitres à convertir : {total_chapters}")
    times = []
    for idx, (chapter_title, chapter_text) in enumerate(chapters.items(), 1):
        safe_title = "".join(c if c.isalnum() else "_" for c in chapter_title)
        audio_path = os.path.join(output_dir, f"{safe_title}.mp3")
        print(f"\n[{idx}/{total_chapters}] Conversion du chapitre '{chapter_title}' en audio...")
        start_time = time.time()
        asyncio.run(text_to_speech(chapter_text, audio_path))
        elapsed = time.time() - start_time
        times.append(elapsed)
        print(f"Chapitre '{chapter_title}' converti en {elapsed:.1f} secondes.")
        if idx < total_chapters:
            avg_time = sum(times) / len(times)
            remaining = avg_time * (total_chapters - idx)
            print(f"Temps estimé restant : {remaining/60:.1f} minutes ({remaining:.0f} secondes)")
    print("\nConversion terminée.")

def merge_mp3s_in_creation_order(input_dir, output_path):
    """
    Fusionne tous les fichiers MP3 du dossier input_dir dans l'ordre de date de création.
    Le plus vieux en premier, le plus récent en dernier.
    """
    from pydub import AudioSegment
    import glob
    from pydub.exceptions import CouldntDecodeError

    mp3_files = glob.glob(os.path.join(input_dir, "*.mp3"))
    mp3_files = [f for f in mp3_files if os.path.isfile(f)]
    mp3_files.sort(key=lambda x: os.stat(x).st_ctime)

    if not mp3_files:
        print("Aucun fichier MP3 trouvé dans le dossier.")
        return

    print("Fusion des fichiers MP3 dans l'ordre de création :")
    for f in mp3_files:
        print(f" - {os.path.abspath(f)}")

    merged = AudioSegment.empty()
    nb_ok = 0
    for mp3_file in mp3_files:
        try:
            merged += AudioSegment.from_mp3(mp3_file)
            nb_ok += 1
        except FileNotFoundError:
            print(f"Fichier introuvable, ignoré : {os.path.abspath(mp3_file)}")
        except CouldntDecodeError:
            print(f"Impossible de décoder (ffmpeg absent ou fichier corrompu) : {os.path.abspath(mp3_file)}")
        except Exception as e:
            print(f"Erreur inattendue avec {os.path.abspath(mp3_file)} : {e}")

    if nb_ok == 0:
        print("Aucun fichier audio valide à fusionner.")
        print("Vérifiez que ffmpeg est installé et accessible dans votre PATH système.")
        print("Téléchargement : https://ffmpeg.org/dowwnload.html")
        return

    merged.export(output_path, format="mp3")
    print(f"Fichier fusionné exporté sous : {output_path}")


if __name__ == "__main__":
    # Remplacez par votre fichier d'entrée et répertoire de sortie
    input_path = "live.epub"  # ou "votre_livre.pdf"
    output_dir = "audio_chapitres"
    process_file(input_path, output_dir)
    merge_mp3s_in_creation_order(output_dir, "titre_du_livre_et_auteur.mp3")
