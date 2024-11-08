import fcntl
import os
import time
import asyncio
import eyed3
from shazamio import Shazam

def instance_already_running(label="default"):
    """
    Detect if an an instance with the label is already running, globally
    at the operating system level.

    Using `os.open` ensures that the file pointer won't be closed
    by Python's garbage collector after the function's scope is exited.

    The lock will be released when the program exits, or could be
    released if the file pointer were closed.
    """
    lock_file_pointer = os.open(f"/tmp/instance_{label}.lock", os.O_WRONLY | os.O_CREAT)
    
    try:
        fcntl.lockf(lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)
        already_running = False
    except IOError:
        already_running = True

    return already_running

async def get_metadata(file_path):
    """
    Uses shazamio API to detect metadata about a song
    """
    shazam = Shazam()
    out = await shazam.recognize(file_path)
    song_info = out['track']

    artist = song_info.get('subtitle', 'Unknown Artist')
    title = song_info.get('title', 'Unknown Title')
    album = song_info.get('sections', [{}])[0].get('metadata', [{}])[0].get("text", 'Unknown Album')
    year = song_info.get('sections', [{}])[0].get('metadata', [{},{},{}])[2].get("text", '')
    genres = song_info.get('genres', {}).get('primary', "")

    return artist, title, album, year, genres

def update_necessary(file_path):
    """
    Returns True if the key metadata are missing and the update is necessary.
    """
    audiofile = eyed3.load(file_path)
    artist = audiofile.tag.artist
    title = audiofile.tag.title
    album = audiofile.tag.album
    if artist == "" or artist == None or artist.lower() == "unknown artist":
        return True
    
    if title == "" or title == None or title.lower() == "unknown title" or "track" in title.lower():
        return True
    
    if album == "" or album == None or album.lower() == "unknown album":
        return True

    return False

def update_mp3_metadata(file_path, artist, title, album, year, genres):
    """
    Overwrites metadata of an mp3 file with the ones provided as parameters
    """
    audiofile = eyed3.load(file_path)
    audiofile.tag.artist = artist
    audiofile.tag.title = title
    audiofile.tag.album = album
    if year != "":
        audiofile.tag.year = int(year)

    audiofile.tag.genre = genres
    audiofile.tag.save()


def main():
    if instance_already_running():
        print("Another instance already running.")
        return
    
    rate_limit = int(os.getenv("rate", 4))
    sleep_time = 60 / rate_limit   
    stats = {'visited': 0, 'skipped': 0, 'updated': 0, 'error': 0}
    
    def identify_and_update(full_path):
        artist, title, album, year, genres = asyncio.run(get_metadata(full_path))
        update_mp3_metadata(full_path, artist, title, album, year, genres)  

    def process_file(filename):
        stats['visited'] += 1
        print(f"visited so far: {stats['visited']}", end="\r")
        try:
            if os.path.splitext(filename)[1] != ".mp3":
                return

            full_path = os.path.join(dirpath, filename)

            if not update_necessary(full_path):
                stats['skipped'] += 1
                return

            identify_and_update(full_path)
            stats['updated'] += 1
            time.sleep(sleep_time)
        except:
            stats['error'] += 1
            return
           
    for dirpath, dirnames, filenames in os.walk("/source/"):
            for filename in filenames:
                process_file(filename)

    print(f"Visited: {stats['visited']} Skipped: {stats['skipped']} Error: {stats['error']} Updated: {stats['updated']}")

if __name__ == '__main__':
    main()