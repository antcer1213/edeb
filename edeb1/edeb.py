#!/usr/bin/env python
# encoding: utf-8
import os
import ecore
import elementary as elm
import evas
import checks
import logging
import mimetypes
import debfile as debianfile
logging.basicConfig(level=logging.DEBUG)

"""eDeb

A deb-package installer built on Python-EFL's.
By: AntCer (bodhidocs@gmail.com)

Uses a slightly modified eSudo, initially made
by Anthony Cervantes, now maintained by Jeff Hoogland,
and improved upon further by Kai Huuko.

Started: January 17, 2013
"""

import sys
import argparse
parser = argparse.ArgumentParser(description='A deb-package installer built on Python-EFLs.')
parser.add_argument("deb", metavar="file", type=str, nargs="*",
                    help="Debian package to initially load.")
clargs = parser.parse_args(sys.argv[1:])
HOME = os.getenv("HOME")




class buttons_main(object):
    def __init__(self, command=False):

#----Main Window
        win = self.win = elm.StandardWindow("edeb", "eDeb")
        win.callback_delete_request_add(lambda o: elm.exit())

        vbox = elm.Box(win)
        vbox.padding_set(5, 25)
        vbox.size_hint_align_set(-1.0, -1.0)
        vbox.size_hint_weight_set(1.0, 1.0)
        vbox.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        fsbox = elm.Box(win)
        fsbox.size_hint_align_set(-1.0, -1.0)
        fsbox.size_hint_weight_set(1.0, 1.0)
        vbox.pack_end(fsbox)
        fsbox.show()

        fs = self.fs = elm.FileselectorEntry(win)
        fs.text_set("Select .deb file")
        fs.window_title_set("Select a .deb file:")
        fs.expandable_set(False)
        fs.inwin_mode_set(True)
        fs.is_save_set(True)
        fs.path_set(HOME)
        fs.callback_file_chosen_add(self.init_wait)
        fs.callback_activated_add(self.en_wait)
        fs.size_hint_align_set(-1.0, -1.0)
        fs.size_hint_weight_set(1.0, 1.0)
        fsbox.pack_end(fs)
        fs.show()

        fil = elm.Box(win)
        fil.size_hint_align_set(-1.0, -1.0)
        fil.size_hint_weight_set(1.0, 1.0)
        vbox.pack_end(fil)
        fil.show()

        btbox = elm.Box(win)
        btbox.size_hint_align_set(-1.0, -1.0)
        btbox.size_hint_weight_set(1.0, 0.0)
        vbox.pack_end(btbox)
        btbox.show()

        tb = elm.Toolbar(self.win)
        tb.size_hint_weight_set(1.0, 0.0)
        tb.size_hint_align_set(-1.0, -1.0)
        self.bt1 = tb.item_append("", "Install", self.inst_check, win)
        tb.select_mode_set(2)
        btbox.pack_end(tb)
        tb.show()

        tb = elm.Toolbar(self.win)
        tb.size_hint_weight_set(1.0, 0.0)
        tb.size_hint_align_set(-1.0, -1.0)
        self.bt2 = tb.item_append("", "Package Info", self.bt_wait)
        tb.select_mode_set(2)
        btbox.pack_end(tb)
        tb.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        win.resize_object_add(vbox)
        win.resize(425, 285)
        win.show()

#-------Add deb from CLI
        if clargs.deb:
            separator_string = " "
            path = separator_string.join(clargs.deb)
            if os.path.exists(path):
                self.fs.path_set("%s" %path)
                self.fs.selected_set("%s" %path)
                self.et = ecore.Timer(0.11, self.cli_add, path)

                self.n = n = elm.Notify(self.win)
                lb = elm.Label(self.win)
                lb.text = "<b>Loading Package Information...</b>"
                lb.size_hint_align = 0.0, 0.5
                lb.show()
                n.orient = 1
                n.allow_events_set(False)
                n.content = lb
                n.show()
            else:
                checks.file_noexist_popup(self.win)

#----Common
    def cli_add(self, path):
        logging.info("Loading %s..." %path)
        path = self.fs.selected_get()
        deb = path
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        logging.info("Starting initial check...")
        if mimetype == "application/x-debian-package":
            deb = debianfile.DebPackage(path, cache=None)
            if deb.check() ==  False:
                logging.info("Initial check failed.")
                self.fs.selected_set(HOME)
                self.fs.path_set(HOME)
                self.n.delete()
                checks.not_installable_popup(self.win)
                return
            else:
                logging.info("Initial check passed.")
                chk = checks.Checks(path, self.win, end_callback=None)
                chk.check_file(self.fs, self.win)
                self.n.delete()
                return
        elif path == HOME or path == "%s/" %HOME:
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            self.n.delete()
            return
        else:
            logging.info("Invalid file!")
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            checks.file_error_popup(self.win)
            self.n.delete()
            return
        self.et.delete()

    def init_wait(self, fs, path):
        fullpath = self.fs.selected_get()
        if fullpath == HOME or fullpath == "%s/" %HOME:
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            return
        elif path:
            deb = path
            mimetype = mimetypes.guess_type (deb, strict=1)[0]
            if mimetype == "application/x-debian-package":
                self.et = ecore.Timer(0.03, self.init_check, path)
                self.n = n = elm.Notify(self.win)
                lb = elm.Label(self.win)
                lb.text = "<b>Loading Package Information...</b>"
                lb.size_hint_align = 0.0, 0.5
                lb.show()
                n.orient = 1
                n.allow_events_set(False)
                n.content = lb
                n.show()
                return
            else:
                logging.info("Invalid file!")
                self.fs.selected_set(HOME)
                self.fs.path_set(HOME)
                checks.file_error_popup(self.win)
                return
        else:
            self.fs.selected_set(fullpath)
            self.fs.path_set(fullpath)
            return

    def en_wait(self, fs):
        path = fs.selected_get()
        if os.path.exists(path):
            self.init_wait(fs, path)
            return
        else:
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            checks.file_noexist_popup(self.win)

    def bt_wait(self, tb, bt):
        path = self.fs.selected_get()
        if path == HOME:
            checks.nofile_error_popup(self.win)
            return
        else:
            self.et = ecore.Timer(0.4, self.bt_init_check, path)
            self.n = n = elm.Notify(self.win)
            lb = elm.Label(self.win)
            lb.text = "<b>Loading Package Information...</b>"
            lb.size_hint_align = 0.0, 0.5
            lb.show()
            n.orient = 1
            n.allow_events_set(False)
            n.content = lb
            n.show()

    def init_check(self, path):
        deb = debianfile.DebPackage(path, cache=None)
        logging.info("Loading %s..." %path)
        logging.info("Starting initial check...")
        if deb.check() ==  False:
            logging.info("Initial check failed.")
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            checks.not_installable_popup(self.win)
        else:
            logging.info("Initial check passed.")
            chk = checks.Checks(path, self.win, end_callback=None)
            chk.check_file(self.fs, self.win)
        self.n.delete()
        self.et.delete()

    def inst_check(self, tb, bt, win):
        path = self.fs.selected_get()
        chk = checks.Checks(path, self.win, end_callback=None)
        chk.check_file_install(bt, win, self.bt2, self.fs)

    def bt_init_check(self, path):
        chk = checks.Checks(path, self.win, end_callback=None)
        chk.check_file(self.fs, self.win)
        self.n.delete()
        self.et.delete()

#----- Main -{{{-
if __name__ == "__main__":
    elm.init()

    buttons_main(None)

    elm.run()
    elm.shutdown()
# }}}
# vim:foldmethod=marker
