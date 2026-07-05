#!/usr/bin/env bash
#ai-assisted with OCA/OpenAI Model with human supervision

set -euo pipefail

binary=${VISUAL_SMOKE_BINARY:-"$(pwd)/bin/pacman"}
output=${VISUAL_SMOKE_OUTPUT:-"$(pwd)/tmp/pacman-smoke.png"}

for command in xvfb-run xwininfo import identify timeout; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "visual smoke requires '$command'" >&2
        exit 2
    fi
done

if [[ ! -x "$binary" ]]; then
    echo "visual smoke binary is missing or not executable: $binary" >&2
    exit 2
fi

mkdir -p "$(dirname "$output")"
config_dir=$(mktemp -d)
log_file=$(mktemp)
trap 'rm -rf "$config_dir" "$log_file"' EXIT

xvfb-run -a -s '-screen 0 1280x1024x24' bash -c '
    set -euo pipefail
    binary=$1
    output=$2
    config_dir=$3
    log_file=$4

    timeout 6s env \
        PACMAN_DISABLE_AUDIO=1 \
        PACMAN_CONFIG_DIR="$config_dir" \
        "$binary" >"$log_file" 2>&1 &
    app_pid=$!

    sleep 3
    if ! kill -0 "$app_pid" 2>/dev/null; then
        cat "$log_file" >&2
        wait "$app_pid"
        exit 1
    fi

    window_id=$(xwininfo -root -tree | awk '\''/"Pacman \(Go \+ Ebiten\)"/ {print $1; exit}'\'')
    if [[ -z "$window_id" ]]; then
        echo "could not find the Pac-Man window" >&2
        exit 1
    fi
    import -display "$DISPLAY" -window "$window_id" "PNG24:$output"

    set +e
    wait "$app_pid"
    status=$?
    set -e
    if [[ "$status" -ne 124 ]]; then
        cat "$log_file" >&2
        echo "game exited before the expected timeout (status=$status)" >&2
        exit 1
    fi
' _ "$binary" "$output" "$config_dir" "$log_file"

if [[ ! -s "$output" ]]; then
    echo "visual smoke did not create a screenshot: $output" >&2
    exit 1
fi

dimensions=$(identify -format '%w %h' "$output")
read -r width height <<<"$dimensions"
if (( width < 400 || height < 400 )); then
    echo "visual smoke screenshot is unexpectedly small: ${width}x${height}" >&2
    exit 1
fi
identify "$output"
