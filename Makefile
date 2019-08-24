include config.mak

RELEASE_FILES = lib/phrase.py lib/suggest.py lib/common.py gui/Settings.py gui/open-tran.py
TMP_DIR = ./open-tran-$(VERSION)

MKDIR = @echo "MKDIR $1"
TAR   = @echo "TAR   $1"
CP    = @echo "CP    $1"

all:
	$(Q)$(MAKE) -C lib

release:
	$(MKDIR) $(TMP_DIR)
	$(Q)rm -rf $(TMP_DIR)
	$(Q)mkdir $(TMP_DIR)
	$(CP) $(RELEASE_FILES)
	$(Q)cp $(RELEASE_FILES) $(TMP_DIR)
	$(TAR) $(TMP_DIR).tar.gz
	$(Q)tar zcf $(TMP_DIR).tar.gz $(TMP_DIR)
	$(Q)rm -rf $(TMP_DIR)

clean:
	$(Q)$(MAKE) -C lib clean

.PHONY: all release clean
