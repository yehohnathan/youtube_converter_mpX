PY   ?= py -3.12
MAIN := youtube_to_mpX.py

install:
	$(PY) -m pip install --upgrade yt_dlp imageio-ffmpeg

run: install
	$(PY) $(MAIN)

lint:
	$(PY) -m pip install --upgrade ruff
	ruff check --fix $(MAIN)

.PHONY: install run lint
