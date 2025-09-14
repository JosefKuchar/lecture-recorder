import threading
import time
import schedule
import subprocess
import time
import signal
from loguru import logger
from datetime import datetime


def record(url: str, name: str, length: int):
    """
    Records a video stream from the specified URL for a given duration and saves it to a file.
    Args:
        url (str): The m3u8 stream URL of the video stream to record.
        name (str): The base name for the output file.
        length (int): The duration (in minutes) to record the stream.
    """

    logger.info("Recording started")
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Start recording
    process = subprocess.Popen(
        [
            "yt-dlp",
            url,
            "-o",
            f"outputs/{name}_{current_time}.mp4",
        ]
    )

    # Record for the specified length of time
    time.sleep(length * 60)

    # Stop recording
    process.send_signal(signal.SIGINT)
    process.wait()  # wait for the process to terminate

    logger.info("Job finished")


def job(*args):
    """
    Starts a new thread to execute the 'record' function with the provided arguments.
    """
    job_thread = threading.Thread(target=record, args=args)
    job_thread.start()


def main():
    """
    Main function to set up logging and schedule the recording jobs
    """

    logger.add("file_{time}.log", rotation="100 MB")

    logger.info("Scheduler started")

    # Schedule jobs
    # PV179 System Development in C#/.NET
    schedule.every().tuesday.at("14:00").do(
        job,
        "https://cdn.streaming.cesnet.cz/muni/munifia318.stream/playlist.m3u8",
        "pv179",
        120,
    )

    # PV293 Software Architectures
    schedule.every().wednesday.at("14:00").do(
        job,
        "https://cdn.streaming.cesnet.cz/muni/munifia217.stream/playlist.m3u8",
        "pv293",
        120,
    )

    logger.info("Waiting for jobs...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
