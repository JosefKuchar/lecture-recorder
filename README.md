A Python script for automated recording of university lecture streams using scheduled jobs.

## Features

- Records video streams from specified m3u8 URLs.
- Schedules recordings using the `schedule` library.
- Saves output files with timestamped names in the `outputs/` directory.
- Logging with rotation using `loguru`.

## Requirements

- Python 3.12
- yt-dlp
- loguru
- schedule

## Usage

1. Install [uv](https://github.com/astral-sh/uv):

2. Run the script:
   ```
   uv run main.py
   ```

3. Recorded videos will be saved in the `outputs/` folder.

## Configuration

- Edit `main.py` to adjust stream URLs, recording times, and durations as needed.

---

This project is intended for educational use.
