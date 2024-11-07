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
    shazam = Shazam()
    out = await shazam.recognize(file_path)
    song_info = out['track']
    
    artist = song_info.get('subtitle', 'Unknown Artist')
    title = song_info.get('title', 'Unknown Title')
    album = song_info.get('sections', [{}])[0].get('metadata', [{}])[0].get("text", 'Unknown Album')
    year = song_info.get('sections', [{}])[0].get('metadata', [{},{},{}])[2].get("text", '')
    genres = song_info.get('genres', {}).get('primary', "")

    return artist, title, album, year, genres

def main():
    if instance_already_running():
        print("Another instance already running.")
        return
    
    rate_limit = os.getenv("rate", 4)
    sleep_time = 60 / rate_limit
    
    for dirpath, dirnames, filenames in os.walk("/source/"):
            for filename in filenames:
                if os.path.splitext(filename)[1] != ".mp3":
                    continue

                # Join the directory path with the file name
                full_path = os.path.join(dirpath, filename)
                artist, title, album, year, genres = asyncio.run(get_metadata(full_path))
                print(f"{full_path}\n\tArtist: {artist}\n\tTitle: {title}\n\tAlbum: {album}\n\tYear: {year}\n\tGenres: {genres}\n")
                time.sleep(sleep_time)

if __name__ == '__main__':
    main()