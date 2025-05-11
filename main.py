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

async def text_to_speech(text, output_audio_path, voice="fr-FR-DeniseNeural"):
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

if __name__ == "__main__":
    # Remplacez par votre fichier d'entrée et répertoire de sortie
    input_path = "votre_livre.epub"  # ou "votre_livre.epub"
    output_dir = "audio_chapitres"
    process_file(input_path, output_dir)
