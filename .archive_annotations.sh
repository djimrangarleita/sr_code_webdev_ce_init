#!/bin/bash

set -e

archive_path="$(cd .. && pwd)/$(basename "$PWD").zip"
echo "📦 Creating ZIP archive: $archive_path"

zip -r "$archive_path" . \
  -x ".*" \
  -x ".*/*" \
  -x ".*/**" \
  -x "*/.*" \
  -x "*/.*/*" \
  -x "*/.*/**" \
  -x "__MACOSX/*" \
  -x "__MACOSX/**" \
  -x "*/__MACOSX/*" \
  -x "*/__MACOSX/**" \
  -x "__pycache__/*" \
  -x "__pycache__/**" \
  -x "*/__pycache__/*" \
  -x "*/__pycache__/**" \
  -x "node_modules/*" \
  -x "node_modules/**" \
  -x "*/node_modules/*" \
  -x "*/node_modules/**" \
  -x "*file_collector.py" \
  -x "*convert_to_json.py"

echo "✅ Archive created successfully at:"
echo "$archive_path"


