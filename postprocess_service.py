"""
Service to postprocess recorded videos by enhancing audio quality
"""

import time
import subprocess
import threading
from queue import Queue
from argparse import ArgumentParser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from loguru import logger

WATCH_DIR = "outputs"

# Job queue
task_queue = Queue()


def enqueue_if_valid(file_path):
    """Check if file is a valid mp4 and not temp, then enqueue."""

    if not file_path.endswith(".mp4"):
        return
    if file_path.endswith(".temp.mp4"):
        logger.debug(f"Ignored temporary file: {file_path}")
        return
    logger.info(f"New video ready: {file_path}")
    task_queue.put(file_path)


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


def worker(worker_id):
    """
    Worker thread to process video files from the queue
    """

    while True:
        file_path = task_queue.get()
        try:
            logger.info(f"[Worker {worker_id}] Processing {file_path}")
            subprocess.run(["postprocessing/postprocess.sh", file_path], check=True)
            logger.success(f"[Worker {worker_id}] Finished {file_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"[Worker {worker_id}] Error processing {file_path}: {e}")
            # optionally re-queue for retry
            # task_queue.put(file_path)
        finally:
            task_queue.task_done()


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Watch directory and process videos with Service B"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker threads for parallel processing",
    )
    args = parser.parse_args()

    logger.add("logs/postprocess_{time}.log", rotation="10 MB")

    # Start worker threads
    for i in range(args.workers):
        t = threading.Thread(target=worker, args=(i + 1,), daemon=True)
        t.start()

    # Start watcher
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    logger.info(f"Watching {WATCH_DIR} with {args.workers} worker(s)...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.warning("Shutting down watcher...")
    observer.join()
