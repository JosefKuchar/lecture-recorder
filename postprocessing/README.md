# Video Audio Cleanup Script

This Bash script processes a video by extracting its audio, cleaning it using **DeepFilterNet**, and creating a new video with the filtered audio. Temporary files are automatically cleaned up.

## Requirements

- `ffmpeg` installed and available in PATH
- `deep-filter` executable in the same directory as the script
    - You can download it from the [DeepFilterNet GitHub repository](https://github.com/Rikorose/DeepFilterNet/releases)
- `DeepFilterNet3_onnx.tar.gz` model file in the same directory as the script
    - You can download it from the [DeepFilterNet GitHub repository](https://github.com/Rikorose/DeepFilterNet/raw/refs/heads/main/models/DeepFilterNet3_onnx.tar.gz)

## Usage

```bash
./process_video.sh input_video.mp4
```
