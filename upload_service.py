"""
Service to upload recorded videos to YouTube
"""

import threading
import time
from queue import Queue
from pathlib import Path

from googleapiclient.errors import HttpError
from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import pydantic
import typer
import omegaconf

from youtube import get_authenticated_service, initialize_upload

# Job queue
task_queue = Queue()

app = typer.Typer()


class Playlist(pydantic.BaseModel):
    """
    Represents a YouTube playlist - for linking uploaded videos
    """

    name: str
    playlist_id: str


class Config(pydantic.BaseModel):
    """
    App configuration
    """

    playlists: list[Playlist] = []
    num_workers: int = 1
    watch_dir: str = "postprocessing"


def enqueue_if_valid(file_path):
    """Check if file is a valid mp4 and not temp, then enqueue."""

    if not file_path.endswith(".mp4"):
        return
    if file_path.endswith(".temp.mp4"):
        logger.debug(f"Ignored temporary file: {file_path}")
        return
    logger.info(f"New video ready: {file_path}")
    task_queue.put(file_path)


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class VideoHandler(FileSystemEventHandler):
    """
    Handles new video files in the watched directory
    """

    def on_created(self, event):
        if not event.is_directory:
            enqueue_if_valid(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            enqueue_if_valid(event.dest_path)


def upload_video(file_path: str, playlists: list[Playlist]):
    """
    Upload video to YouTube
    """
    path = Path(file_path)

    # Find playlist ID if configured
    playlist_id = None
    for pl in playlists:
        if path.stem.startswith(pl.name):
            playlist_id = pl.playlist_id
            break
    if playlist_id is None:
        logger.warning(f"No playlist configured for {path.stem}, uploading without")

    settings = {
        "videofile": file_path,
        "title": path.stem,
        "description": "",
        "category": "27",  # Education
        "keywords": "lecture, recording, education",
        "privacyStatus": "unlisted",
        "latitude": None,
        "longitude": None,
        "language": "cs",
        "playlistId": playlist_id,
        "thumbnail": None,
        "license": "youtube",
        "publishAt": None,
        "publicStatsViewable": True,
        "madeForKids": False,
        "ageGroup": None,
        "gender": None,
        "geo": None,
        "defaultAudioLanguage": None,
        "force_refresh": True,
    }
    settings = dotdict(settings)
    service = get_authenticated_service(settings)
    initialize_upload(service, settings)


def worker(worker_id, playlists: list[Playlist]):
    """
    Worker thread to process video files from the queue
    """

    while True:
        file_path = task_queue.get()
        try:
            logger.info(f"[Worker {worker_id}] Processing {file_path}")
            upload_video(file_path, playlists)
            logger.success(f"[Worker {worker_id}] Finished {file_path}")
        except HttpError as e:
            logger.error(f"[Worker {worker_id}] Error processing {file_path}: {e}")
        finally:
            task_queue.task_done()


@app.command()
def main(config_path: Path):
    """
    Main function to set up logging and start the upload service
    """

    conf: Config = omegaconf.OmegaConf.load(config_path)
    conf_dict = omegaconf.OmegaConf.to_container(conf, resolve=True)
    conf = Config(**conf_dict)

    logger.add("logs/upload_{time}.log", rotation="10 MB")

    # Start worker threads
    for i in range(conf.num_workers):
        t = threading.Thread(target=worker, args=(i + 1, conf.playlists), daemon=True)
        t.start()

    # Start watcher
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, conf.watch_dir, recursive=False)
    observer.start()

    logger.info(f"Watching {conf.watch_dir} with {conf.num_workers} worker(s)...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.warning("Shutting down watcher...")
    observer.join()


if __name__ == "__main__":
    app()
