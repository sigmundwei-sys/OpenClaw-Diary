#!/bin/sh
set -e

MDFILE="$1"
if [ -z "$MDFILE" ] || [ ! -f "$MDFILE" ]; then
    echo "Usage: $0 <content.md>"
    exit 1
fi

DATESTR=$(date +%Y-%m-%d)
HTMLFILE="index.html"
TMPFILE="index.html.tmp"

# 1. Remove active classes
sed -i 's/class="date-tab active"/class="date-tab"/g' "$HTMLFILE"
sed -i 's/class="screen active"/class="screen"/g' "$HTMLFILE"

# 2. Add date tab before the closing div of tabs
TAB_HTML="<button class=\"date-tab active\" onclick=\"showScreen('screen-${DATESTR}')\">${DATESTR}<\/button>"
if ! grep -q "screen-${DATESTR}" "$HTMLFILE"; then
    awk -v tab="$TAB_HTML" '/<\/button>[[:space:]]*<\/div>/ { sub(/<\/button>[[:space:]]*<\/div>/, "</button>\n            " tab "\n        </div>"); } 1' "$HTMLFILE" > "$TMPFILE"
    mv "$TMPFILE" "$HTMLFILE"
fi

# 3. Format Markdown content to HTML (basic conversion)
# Convert bullets to <ul><li>, and paragraphs to <p>
awk '
BEGIN { in_list=0; print "<div class=\"long-text\">" }
/^- / {
    if (!in_list) { print "<ul>"; in_list=1 }
    sub(/^- /, "");
    print "<li>" $0 "</li>"
    next
}
/^$/ { next }
{
    if (in_list) { print "</ul>"; in_list=0 }
    print "<p>" $0 "</p>"
}
END {
    if (in_list) { print "</ul>" }
    print "</div>"
}
' "$MDFILE" > "formatted.tmp"

FORMATTED_HTML=$(cat "formatted.tmp")
rm -f "formatted.tmp"

# 4. Create the new screen HTML
NEW_SCREEN="
            <!-- ${DATESTR} -->
            <div class=\"screen active\" id=\"screen-${DATESTR}\">
                <div class=\"entry\">
                    <div class=\"entry-bar\">
                        <span class=\"entry-filename\">~/${DATESTR}/learning.md</span>
                        <span class=\"entry-status\">✓</span>
                    </div>
                    <div class=\"entry-body\">
                        <div class=\"quote-box\">
                            <div class=\"quote-title\">💡 今天的學習總結</div>
                            ${FORMATTED_HTML}
                        </div>
                    </div>
                </div>
            </div>
"

# 5. Insert before <!-- Placeholder -->
if ! grep -q "id=\"screen-${DATESTR}\"" "$HTMLFILE"; then
    awk -v screen="$NEW_SCREEN" '/<!-- Placeholder -->/ && !inserted { print screen; inserted=1 } 1' "$HTMLFILE" > "$TMPFILE"
    mv "$TMPFILE" "$HTMLFILE"
fi

echo "Successfully updated index.html with entry for ${DATESTR}"
