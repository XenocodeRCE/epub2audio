# epub2audio
Utilise Edge-TTS pour convertir un fichier EPUB en fichier audio. Gère aussi très bien les PDFs.


# Installation des dépendances
```
pip install edge-tts PyPDF2 ebooklib beautifulsoup4
```

## FFMpeg

1. Téléchargez les binaires ici  : https://github.com/BtbN/FFmpeg-Builds/releases
2. Décompressez le tout dans un nouveau dossier
3. Ouvrez une fenêtre Powershell et éxecutez le script suivant :

```
# Ajoute le dossier bin de ffmpeg au PATH utilisateur
$ffmpegBin = "votre\chemin\vers\le\dossier\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$ffmpegBin", "User")
```


## Autres
Commande pour voir la lite des voix :
```
edge-tts --list-voices
```
