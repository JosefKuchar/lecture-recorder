A Python script for automated recording of university lecture streams using scheduled jobs.

## Features

- Records video streams from specified m3u8 URLs.
- Schedules recordings using the `schedule` library.
- Saves output files with timestamped names in the `outputs/` directory.
- Logging with rotation using `loguru`.
- Post-processing of recorded videos (optional) to enhance audio quality using machine learning model.

## Requirements

- Python 3.12
- uv
- ffmpeg
- yt-dlp
- loguru
- schedule
- omegaconf
- pydantic
- watchdog
- typer

## Usage

Install [uv](https://github.com/astral-sh/uv)

## Download service
This service handles the scheduling and recording of streams

1. Prepare your configuration in `config.yaml`. Example:
   ```yaml
   schedules:
     - url: "https://example.com/stream.m3u8"
       name: "pv123"
       duration: 60
       day: "monday"
       time: "08:00"
   ```

2. Run the script with your config file:
   ```sh
   uv run download_service.py config.yaml
   ```

3. Recorded videos will be saved in the `outputs/` folder.

### Configuration

- Edit `config.yaml` to adjust stream URLs, recording times, and durations as needed.

## Post-processing service
This service monitors the `outputs/` directory for new recordings and processes them. You don't need to run this service, but the quality of the recordings will be better if you do.

First, you have to setup the postprocessing environment. Look at the `postprocessing/README.md` for instructions.

1. Run the postprocessing service:
   ```sh
   uv run postprocess_service.py
   ```

2. The service will automatically process new recordings in the `outputs/` folder. After processing, the processed files will be in the `postprocessing` folder

## Upload service
This service watches new files and uploads them to YouTube. You need to configure it first. Youtube module is included as a git submodule so you have to pull it first - `git submodule update --init --recursive`

1. Configure the YouTube upload settings by following the instructions in the `youtube/README.md` file.

2. Run the upload service:
   ```sh
   uv run upload_service.py
   ```
3. The service will automatically upload new processed recordings in the `postprocessing` folder to YouTube. You can also monitor raw recordings in the `outputs` folder using the `--watch-dir` option.


---

This project is intended for educational use.
