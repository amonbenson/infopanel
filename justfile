setup:
    uv --verbose sync
    just build-rgbmatrix

# Build the rgbmatrix C extension manually.
# Required because the upstream hatch build hook fails silently:
# it lacks setuptools and the Pillow libImaging headers (Imaging.h is
# only in the sdist, not the installed package).
build-rgbmatrix:
    #!/usr/bin/env bash
    set -euo pipefail
    PROJECT=$(pwd)
    PYTHON="$PROJECT/.venv/bin/python"
    SRC=$("$PYTHON" -c "
    import json, pathlib, glob
    url_file = next(pathlib.Path('$PROJECT/.venv/lib').glob('python*/site-packages/rgbmatrix-*.dist-info/direct_url.json'))
    data = json.loads(url_file.read_text())
    commit = data['vcs_info']['commit_id'][:7]
    hits = glob.glob(f'/home/pi/.cache/uv/git-v0/checkouts/*/{commit}')
    print(hits[0])
    ")
    PILLOW_INC=$(find /home/pi/.cache/uv/sdists-v9/pypi/pillow -name "Imaging.h" | head -1 | xargs dirname)
    DEST=$(echo "$PROJECT"/.venv/lib/python*/site-packages/rgbmatrix/)
    echo "Building rgbmatrix from $SRC"
    make -C "$SRC/lib"
    cd "$SRC/bindings/python" && CFLAGS="-I$PILLOW_INC" "$PYTHON" setup.py build --build-lib .
    cp "$SRC/bindings/python/rgbmatrix/"*.so "$DEST"
    echo "rgbmatrix extension installed to $DEST"

run:
    sudo REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt .venv/bin/python -m infopanel

dev:
    uv run watchfiles "python -m infopanel"

build:
    just font-build tb-8
    just font-build tb-8-bold

    uv build

font-edit name:
    java -jar tools/BitsNPicas.jar edit infopanel/fonts/{{name}}.kbitx

font-build name:
    rm -f infopanel/fonts/{{name}}.bdf
    java -jar tools/BitsNPicas.jar convertbitmap -f bdf -o infopanel/fonts/{{name}}.bdf infopanel/fonts/{{name}}.kbitx
