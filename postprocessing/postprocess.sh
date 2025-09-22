#!/bin/bash

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if input argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_video>"
    exit 1
fi

INPUT_VIDEO="$1"
BASENAME=$(basename "$INPUT_VIDEO" | sed 's/\.[^.]*$//')

# Paths relative to script directory
ORIGINAL_WAV="${SCRIPT_DIR}/${BASENAME}_original.wav"
FILTERED_WAV="${SCRIPT_DIR}/out/${BASENAME}_filtered.wav"
OUTPUT_VIDEO_TEMP="${SCRIPT_DIR}/${BASENAME}.temp.mp4"
OUTPUT_VIDEO="${SCRIPT_DIR}/${BASENAME}_processed.mp4"

# Ensure output dir exists
mkdir -p "${SCRIPT_DIR}/out"

echo "Extracting audio from $INPUT_VIDEO..."
ffmpeg -i "$INPUT_VIDEO" -vn -acodec pcm_s16le -ar 48000 -filter:a "pan=mono|c0=c1,dynaudnorm" "$ORIGINAL_WAV" -y

echo "Cleaning up audio using DeepFilterNet... (this will take a while)"
"${SCRIPT_DIR}/deep-filter" -o "${SCRIPT_DIR}/out" --model "${SCRIPT_DIR}/DeepFilterNet3_onnx.tar.gz" "$ORIGINAL_WAV"

# DeepFilterNet seems to dump processed files into out/, keep it consistent
FILTERED_OUT="${SCRIPT_DIR}/out/$(basename "$ORIGINAL_WAV")"
if [ ! -f "$FILTERED_OUT" ]; then
    echo "Error: Filtered audio not found!"
    exit 1
fi
mv "$FILTERED_OUT" "$FILTERED_WAV"

echo "Merging filtered audio with original video..."
ffmpeg -i "$INPUT_VIDEO" -i "$FILTERED_WAV" -c:v copy -map 0:v:0 -map 1:a:0 -shortest "$OUTPUT_VIDEO_TEMP" -y
mv "$OUTPUT_VIDEO_TEMP" "$OUTPUT_VIDEO"

# Cleanup intermediate files
echo "Cleaning up temporary files..."
rm -f "$ORIGINAL_WAV"
rm -f "$FILTERED_WAV"

echo "Done! Processed video saved as $OUTPUT_VIDEO"
