#!/bin/bash
# Fix Antigravity IDE Service Worker error
# Chạy: sudo bash fix_ide.sh

echo "=== Fixing Antigravity IDE Service Worker ==="

# Thêm --disable-gpu vào launcher
sed -i 's|Exec=/usr/share/antigravity/antigravity %F|Exec=/usr/share/antigravity/antigravity --disable-gpu %F|' /usr/share/applications/antigravity.desktop

# Thêm --disable-gpu vào action new-empty-window nếu có
sed -i 's|Exec=/usr/share/antigravity/antigravity --new-window %F|Exec=/usr/share/antigravity/antigravity --disable-gpu --new-window %F|' /usr/share/applications/antigravity.desktop 2>/dev/null

echo "✅ Done! Đóng Antigravity rồi mở lại."
