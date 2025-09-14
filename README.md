A Python script for automated recording of university lecture streams using scheduled jobs.

## Features

- Records video streams from specified m3u8 URLs.
- Schedules recordings using the `schedule` library.
- Saves output files with timestamped names in the `outputs/` directory.
- Logging with rotation using `loguru`.

## Requirements

- Python 3.12
- uv
- ffmpeg
- yt-dlp
- loguru
- schedule
- omegaconf
- pydantic
- typer

## Usage

1. Install [uv](https://github.com/astral-sh/uv):

2. Prepare your configuration in `config.yaml`. Example:
   ```yaml
   schedules:
     - url: "https://example.com/stream.m3u8"
       name: "pv123"
       duration: 60
       day: "monday"
       time: "08:00"
   ```

3. Run the script with your config file:
   ```
   uv run main.py config.yaml
   ```

4. Recorded videos will be saved in the `outputs/` folder.

## Configuration

- Edit `config.yaml` to adjust stream URLs, recording times, and durations as needed.

---

This project is intended for educational use.
