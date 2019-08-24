#!/bin/bash

data_root="$1"
mdk_root="$data_root/mandriva"

if [[ ! -d $mdk_root ]]; then
    mkdir $mdk_root
fi

cd $mdk_root

svn_co () {
    if [[ -d "$mdk_root/$2" ]]; then
	echo -n "up $2..."
	svn up "$mdk_root/$2" > /dev/null || true
	echo "done."
    else
	echo -n "co $2..."
	svn co $1 $2 > /dev/null || true
	echo "done."
    fi
}

URL=http://svn.mandriva.com/svn/soft/
DRAKX_URL=$URL/drakx/trunk/perl-install/

svn_co $DRAKX_URL/install/share/po DrakX
svn_co $DRAKX_URL/share/po libDrakX
svn_co $DRAKX_URL/standalone/po libDrakX-standalone
svn_co $URL/bootsplash/trunk/po bootsplash
svn_co $URL/control-center/trunk/po control-center
svn_co $URL/doc_isos/po doc_isos
svn_co $URL/drak3d/trunk/po drak3d
svn_co $URL/drakbackup/trunk/po drakbackup
svn_co $URL/drakbt/trunk/po drakbt
svn_co $URL/drakfax/trunk/po drakfax
svn_co $URL/drakguard/trunk/po drakguard
svn_co $URL/draklive-install/trunk/po draklive-install
svn_co $URL/draklive-resize/trunk/po draklive-resize
svn_co $URL/drakmenustyle/trunk/po drakmenustyle
svn_co $URL/drakmsync/trunk/po drakmsync
svn_co $URL/drakoo/trunk/po drakoo
svn_co $URL/draksnapshot/trunk/po draksnapshot
svn_co $URL/drakstats/trunk/po drakstats
svn_co $URL/draktermserv/trunk/po draktermserv
svn_co $URL/drakvirt/trunk/po drakvirt
svn_co $URL/drakwizard/trunk/po drakwizard
svn_co $URL/drakx-kbd-mouse-x11/trunk/po drakx-kbd-mouse-x11
svn_co $URL/drakx-net/trunk/po network-tools
svn_co $URL/ftw/trunk/po drakfirstboot
svn_co $URL/ftw-web/trunk/po ftw-web
svn_co $URL/GtkMdkWidgets/trunk/po gtkmdkwidgets
svn_co $URL/hcl/trunk/po hcl
svn_co $URL/initscripts/trunk/mandriva/po initscripts
svn_co $URL/kde4-splash-mdv/trunk/po/ kde4-splash-mdv
svn_co $URL/mandriva-kde-translation/trunk/po mandriva-kde-translation
svn_co $URL/mdkhtmlbrowser/trunk/po mdkhtmlbrowser
svn_co $URL/mdkonline/trunk/po mdkonline
svn_co $URL/menu-messages/trunk/contrib menu-contrib
svn_co $URL/menu-messages/trunk/main menu-main
svn_co $URL/menu-messages/trunk/non-free menu-non-free
svn_co $URL/msec/trunk/po msec
svn_co $URL/park-rpmdrake/trunk/po park-rpmdrake
svn_co $URL/printerdrake/trunk/po printerdrake
svn_co $URL/rfbdrake/trunk/po rfbdrake
svn_co $URL/rpmdrake/trunk/po rpmdrake
svn_co $URL/rpm-summary/trunk/rpm-summary-contrib rpm-summary-contrib
svn_co $URL/rpm-summary/trunk/rpm-summary-devel rpm-summary-devel
svn_co $URL/rpm-summary/trunk/rpm-summary-main rpm-summary-main
svn_co $URL/system-config-printer/po system-config-printer
svn_co $URL/rpm/urpmi/trunk/po urpmi
svn_co $URL/theme/mandriva-gfxboot-theme/trunk/po mandriva-gfxboot-theme
svn_co $URL/transfugdrake/trunk/po transfugdrake
svn_co $URL/userdrake2/trunk/po userdrake2
svn_co $URL/mandriva-galaxy-data/trunk/po mandriva-galaxy-data
svn_co $URL/mandriva-galaxy-kde4/trunk/po mandriva-galaxy-kde4
