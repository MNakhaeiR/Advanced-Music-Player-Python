from mutagen import File
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB


def get_metadata_and_album_art(path):
    meta = {}
    art = None
    audio = File(path)
    if audio is None:
        return meta, art
    if path.lower().endswith(".mp3") and audio.tags:
        tags = audio.tags
        meta["title"] = (
            tags.get("TIT2", TIT2(encoding=3, text="")).text[0]
            if tags.get("TIT2")
            else ""
        )
        meta["artist"] = (
            tags.get("TPE1", TPE1(encoding=3, text="")).text[0]
            if tags.get("TPE1")
            else ""
        )
        meta["album"] = (
            tags.get("TALB", TALB(encoding=3, text="")).text[0]
            if tags.get("TALB")
            else ""
        )
        for tag in tags.values():
            if isinstance(tag, APIC):
                art = tag.data
                break
    else:
        meta["title"] = audio.get("title", [""])[0] if audio.get("title") else ""
        meta["artist"] = audio.get("artist", [""])[0] if audio.get("artist") else ""
        meta["album"] = audio.get("album", [""])[0] if audio.get("album") else ""
    return meta, art
