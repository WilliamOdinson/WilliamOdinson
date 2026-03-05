FONT_URL     := https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.tar.xz
FONT_ARCHIVE := assets/Meslo.tar.xz
FONT_REGULAR := assets/MesloLGLNerdFont-Regular.ttf
FONT_BOLD    := assets/MesloLGLNerdFont-Bold.ttf
TEMPLATE     := assets/banner-template.xml
DARK_TMP     := assets/.banner-dark-tmp.svg
LIGHT_TMP    := assets/.banner-light-tmp.svg
DARK_OUT     := assets/banner-dark.svg
LIGHT_OUT    := assets/banner-light.svg
SCRIPT       := scripts/build_banner.py

# Dark theme colors
DARK_BG    := \#0d0d0d
DARK_FG    := \#ffffff
DARK_MUTED := \#b0b0b0
DARK_CARD  := \#ffffff
DARK_CODE  := \#1a1a1a
DARK_SHADOW:= \#000000

# Light theme colors (inverted)
LIGHT_BG    := \#f5f5f5
LIGHT_FG    := \#0d0d0d
LIGHT_MUTED := \#555555
LIGHT_CARD  := \#0d0d0d
LIGHT_CODE  := \#e0e0e0
LIGHT_SHADOW:= \#888888

.PHONY: all

all: $(DARK_OUT) $(LIGHT_OUT)

$(FONT_ARCHIVE):
	curl -fL $(FONT_URL) -o $@

$(FONT_REGULAR) $(FONT_BOLD): $(FONT_ARCHIVE)
	tar -xf $< -C assets/ $(notdir $(FONT_REGULAR)) $(notdir $(FONT_BOLD))
	touch $(FONT_REGULAR) $(FONT_BOLD)

$(DARK_OUT): $(TEMPLATE) $(FONT_REGULAR) $(FONT_BOLD) $(SCRIPT)
	sed -e 's/{{BG}}/$(DARK_BG)/g' -e 's/{{FG}}/$(DARK_FG)/g' \
	    -e 's/{{MUTED}}/$(DARK_MUTED)/g' -e 's/{{CARD}}/$(DARK_CARD)/g' \
	    -e 's/{{CODE}}/$(DARK_CODE)/g' -e 's/{{SHADOW}}/$(DARK_SHADOW)/g' \
	    $(TEMPLATE) > $(DARK_TMP)
	python3 $(SCRIPT) $(DARK_TMP) $@ $(FONT_REGULAR) $(FONT_BOLD)
	npx svgo $@ -o $@
	rm -f $(DARK_TMP)
	@echo "Generated $@ ($$(du -h $@ | cut -f1))"

$(LIGHT_OUT): $(TEMPLATE) $(FONT_REGULAR) $(FONT_BOLD) $(SCRIPT)
	sed -e 's/{{BG}}/$(LIGHT_BG)/g' -e 's/{{FG}}/$(LIGHT_FG)/g' \
	    -e 's/{{MUTED}}/$(LIGHT_MUTED)/g' -e 's/{{CARD}}/$(LIGHT_CARD)/g' \
	    -e 's/{{CODE}}/$(LIGHT_CODE)/g' -e 's/{{SHADOW}}/$(LIGHT_SHADOW)/g' \
	    $(TEMPLATE) > $(LIGHT_TMP)
	python3 $(SCRIPT) $(LIGHT_TMP) $@ $(FONT_REGULAR) $(FONT_BOLD)
	npx svgo $@ -o $@
	rm -f $(LIGHT_TMP)
	@echo "Generated $@ ($$(du -h $@ | cut -f1))"
	rm -f $(FONT_ARCHIVE) $(FONT_REGULAR) $(FONT_BOLD)
