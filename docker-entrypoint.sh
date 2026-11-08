#!/bin/sh
set -e

DB_FILE=/app/db.sqlite3
DB_DIR=$(dirname "$DB_FILE")

if [ "$(id -u)" = "0" ]; then
    # Bind-mounted db files may be owned by root (created by older images).
    chown app:app "$DB_DIR" 2>/dev/null || true
    for f in "$DB_FILE" "$DB_FILE-journal" "$DB_FILE-wal" "$DB_FILE-shm"; do
        [ -e "$f" ] && chown app:app "$f" 2>/dev/null || true
    done

    if ! su-exec app sh -c ': > "$1/.write-test" && rm -f "$1/.write-test"' _ "$DB_DIR" 2>/dev/null; then
        echo "ERROR: $DB_DIR is not writable by user app. Mount a writable volume or fix its permissions." >&2
        exit 1
    fi
    if [ -e "$DB_FILE" ] && ! su-exec app sh -c ': >> "$1"' _ "$DB_FILE" 2>/dev/null; then
        echo "ERROR: $DB_FILE is not writable by user app. Mount a writable volume or fix its permissions." >&2
        exit 1
    fi

    exec su-exec app "$@"
fi

exec "$@"
