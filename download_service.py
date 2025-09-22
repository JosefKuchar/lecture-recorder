"""
Service to download and record video streams based on a schedule
"""

import pathlib
import signal
import subprocess
import threading
import time
from datetime import datetime
import os

import omegaconf
import pydantic
import schedule
import typer
from loguru import logger


class Schedule(pydantic.BaseModel):
    """
    Represents a recording schedule
    """

    url: str
    name: str
    duration: int  # in minutes
    day: str  # e.g., "monday", "tuesday", etc.
    time: str  # in HH:MM format


class Config(pydantic.BaseModel):
    """
    App configuration
    """

    schedules: list[Schedule]


app = typer.Typer()


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
            f"outputs/{name}_{current_time}.temp.mp4",
        ]
    )

    # Record for the specified length of time
    time.sleep(length * 60)

    # Stop recording
    process.send_signal(signal.SIGINT)
    process.wait()  # wait for the process to terminate

    # Rename the temporary file to final name
    os.rename(
        f"outputs/{name}_{current_time}.temp.mp4",
        f"outputs/{name}_{current_time}.mp4",
    )

    logger.info("Job finished")


def job(*args):
    """
    Starts a new thread to execute the 'record' function with the provided arguments.
    """
    job_thread = threading.Thread(target=record, args=args)
    job_thread.start()


@app.command()
def main(config_path: pathlib.Path):
    """
    Main function to set up logging and schedule the recording jobs
    """
    conf: Config = omegaconf.OmegaConf.load(config_path)

    logger.add("logs/download_{time}.log", rotation="10 MB")

    logger.info("Scheduler started")

    # Schedule jobs
    for schedule_item in conf.schedules:
        getattr(schedule.every(), schedule_item.day).at(schedule_item.time).do(
            job,
            schedule_item.url,
            schedule_item.name,
            schedule_item.duration,
        )

    logger.info(f"Loaded {len(conf.schedules)} schedules")
    logger.info("Waiting for jobs...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    app()
