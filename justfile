sync:
    uv --verbose sync

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
