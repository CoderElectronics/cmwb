#!/bin/bash
rm -r webrtc_event_logs
rm error.log
rm -r VideoDecodeStats
rm -r blob_storage

echo "{\"history\":[]}" > config/history.json
echo "{\"bookmarks\":{}}" > config/bookmarks.json
echo "{\"home_url\": \"https://www.google.com/\", \"button_zoom\": 100, \"window_size\": \"800x600\"}" > config/base.json

rm -r config/extensions
mkdir config/extensions

echo "Clean up done!"
