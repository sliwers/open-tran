#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require ('2.0')
import gtk
import os
import time
from Settings import Settings
from common import LANGUAGES
from suggest import TranDB
from translate.storage import factory
from phrase import Phrase

class MainWin:
    def quit (self, widget, event):
        self.config.width, self.config.height = self.window.get_size()
        self.config.onquit()
        gtk.main_quit ()

    def make_scrollable(self, widget):
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(widget)
        sw.show()
        return sw

    def create_editor(self):
        editor = gtk.TextView()
        editor.show()
        sw = self.make_scrollable(editor)
        return (sw, editor.get_buffer())

    def create_suggestions(self):
        self.list_store = gtk.ListStore(str)
        treeview = gtk.TreeView(self.list_store)
        column = gtk.TreeViewColumn('Suggestions')
        treeview.append_column(column)
        cell = gtk.CellRendererText()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', 0)
        treeview.show()
        treeview.connect("row-activated", self.suggest)
        sw = self.make_scrollable(treeview)
        hpane = gtk.HPaned()
        hpane.set_position(int(self.config.correct_width))
        hpane.pack1(sw, True)
        hpane.pack2(self.create_editor()[0], True)
        self.config.register(hpane.get_position, "correct_width")
        hpane.show()
        return hpane

    def create_arrow(self, atype, data):
        button = gtk.Button()
        arrow = gtk.Arrow(atype, gtk.SHADOW_OUT)
        button.add(arrow)
        button.show()
        button.connect("clicked", self.scroll, data)
        button.set_focus_on_click(False)
        if data > 0:
            key = ord('N')
        else:
            key = ord('P')
        button.add_accelerator("clicked", self.accel_group, key, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        arrow.show()
        return button

    def create_dst_editor(self):
        sw, self.dst_buffer = self.create_editor()
        hbox = gtk.HBox(False, 0)
        self.left_arrow = self.create_arrow(gtk.ARROW_LEFT, -1)
        self.right_arrow = self.create_arrow(gtk.ARROW_RIGHT, 1)
        hbox.pack_start(self.left_arrow, False, False, 0)
        hbox.pack_start(sw, True, True, 0)
        hbox.pack_start(self.right_arrow, False, False, 0)
        hbox.show()
        return hbox
    
    def create_dst(self):
        vpane = gtk.VPaned()
        vpane.pack1(self.create_dst_editor(), True)
        vpane.pack2(self.create_suggestions(), True)
        vpane.set_position(int(self.config.dst_heigth))
        self.config.register(vpane.get_position, "dst_heigth")
        vpane.show()
        return vpane

    def create_editors(self):
        sw, self.src_buffer = self.create_editor()
        vpane = gtk.VPaned()
        vpane.pack1(sw, True)
        vpane.pack2(self.create_dst(), True)
        vpane.set_position(int(self.config.src_heigth))
        self.config.register(vpane.get_position, "src_heigth")
        vpane.show()
        return vpane

    def open_button_click(self, widget, data=None):
        self.config.file = ""
        self.open_file()

    def save_button_click(self, widget, data=None):
        pass

    def lang_changed(self, widget, data=None):
        model = widget.get_model()
        self.config.lang = model[widget.get_active()][0]
        self.load_phrases()

    def select_lang(self, lang):
        l = self.lang_combo.get_model()
        idx = [x[0] for x in l].index(lang)
        self.lang_combo.set_active(idx)

    def create_combo(self):
        liststore = gtk.ListStore(str, str)
        for (key, lang) in sorted(LANGUAGES.iteritems()):
            liststore.append([key, '%s: %s' % (key, lang)])
        self.lang_combo = gtk.ComboBox(liststore)
        cell = gtk.CellRendererText()
        self.lang_combo.pack_start(cell, True)
        self.lang_combo.add_attribute(cell, 'text', 1)
        self.select_lang(self.config.lang)
        return self.lang_combo
        

    def create_toolbar(self):
        hbox = gtk.HBox(False, 0)
        open_button = gtk.Button(stock=gtk.STOCK_OPEN)
        open_button.set_focus_on_click(False)
        open_button.show()
        open_button.connect("clicked", self.open_button_click)
        save_button = gtk.Button(stock=gtk.STOCK_SAVE)
        save_button.set_focus_on_click(False)
        save_button.show()
        save_button.connect("clicked", self.save_button_click)
        lang_combo = self.create_combo()
        lang_combo.connect("changed", self.lang_changed)
        lang_combo.show()
        hbox.pack_start(open_button, False, False, 0)
        hbox.pack_start(save_button, False, False, 0)
        hbox.pack_start(lang_combo, False, False, 0)
        hbox.show()
        return hbox
        

    def create_content(self):
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.create_toolbar(), False, False, 0)
        vbox.pack_start(self.create_editors(), True, True, 0)
        vbox.show()
        return vbox

    def init_window (self):
        self.accel_group = gtk.AccelGroup()
        self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.window.set_title ("Tran")
        self.window.set_name ("Tran")
        self.window.set_default_size(int(self.config.width), int(self.config.height))
        self.window.connect ("delete_event", self.quit)
        self.window.add_accel_group(self.accel_group)
        self.window.show ()
        self.window.add(self.create_content())

    def load_phrases(self):
        self.src_buffer.set_text(self.store.units[self.index].source)
        self.dst_buffer.set_text(self.store.units[self.index].target)
        self.list_store.clear()
        if self.index == 0:
            return
        try:
            for sug in self.sug.suggest(str(self.store.units[self.index].source), self.config.lang):
                self.list_store.append([sug.text])
        except:
            pass
    
    def disable_arrows(self):
        self.left_arrow.set_sensitive(self.index != 0)
        self.right_arrow.set_sensitive(self.index != len(self.store.units) - 1)

    def scroll(self, widget, data=None):
        self.index += data
        self.load_phrases()
        self.disable_arrows()

    def suggest(self, treeview, path, column):
        self.dst_buffer.set_text(self.suggestions[self.index - 1][path[0]])

    def load_file(self, filename):
        cls = factory.getclass(filename)
        self.store = cls.parsefile(filename)
        self.index = int(self.config.phrase_index)
        self.config.register(lambda: self.index, "phrase_index")
        self.scroll(None, 0)
        self.config.file = filename

    def open_file(self):
        if self.config.file != "":
            self.load_file(self.config.file)
            return
        dialog = gtk.FileChooserDialog(title = "Open File", parent = self.window,
                                       action = gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                  gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_current_folder(self.config.folder)
        dialog.set_local_only(True)
        dialog.set_select_multiple(False)
        ret = dialog.run()
        self.config.folder = dialog.get_current_folder()
        if ret == gtk.RESPONSE_OK:
            self.load_file(dialog.get_filename())
        dialog.destroy()


    def __init__ (self):
        self.first = -1
        self.last = -1
        self.config = Settings()
        self.sug = TranDB(os.path.expanduser(self.config.dbpath))
        self.init_window ()
        self.open_file()

    def main (self):
        gtk.main ()


if __name__ == "__main__":
    base = MainWin ()
    base.main ()
