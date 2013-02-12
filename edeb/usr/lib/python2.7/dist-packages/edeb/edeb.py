#!/usr/bin/env python
# encoding: utf-8
import os
import elementary as elm
import evas
from ecore import Idler
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


class idle_check(object):
    def __init__(self, command=False, start_callback=None, end_callback=None):

        idler = Idler(command, path_generator)


class buttons_main(object):
    def __init__(self, command=False):

#----Main Window
        win = self.win = elm.StandardWindow("edeb", "eDeb")
        win.callback_delete_request_add(lambda o: elm.exit())

        vbox = elm.Box(win)
        vbox.padding_set(5, 30)
        vbox.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        vbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        vbox.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        fsbox = elm.Box(win)
        fsbox.size_hint_align_set(evas.EVAS_HINT_FILL, 0.0)
        fsbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        vbox.pack_end(fsbox)
        fsbox.show()

        fs = self.fs = elm.FileselectorEntry(win)
        fs.text_set("Select .deb file")
        fs.window_title_set("Select a .deb file:")
        fs.expandable_set(False)
        fs.inwin_mode_set(False)
        fs.path_set(HOME)
        fs.callback_file_chosen_add(self.init_check, win)
        fs.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        fs.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        fsbox.pack_end(fs)
        fs.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        btbox = elm.Box(win)
        btbox.size_hint_align_set(evas.EVAS_HINT_FILL, -1.0)
        btbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        vbox.pack_end(btbox)
        btbox.show()

        bt = elm.Button(win)
        bt.text_set("Install")
        bt.callback_clicked_add(self.inst_check, win)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        btbox.pack_end(bt)
        bt.show()

        bt = elm.Button(win)
        bt.text_set("Package Info")
        bt.callback_clicked_add(self.bt_init_check, win)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        btbox.pack_end(bt)
        bt.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        win.resize_object_add(vbox)
        win.resize(425, 230)
        win.show()

#-------Add deb from CLI
        if clargs.deb:
            self.cli_add(clargs.deb, fs)

#----Common

    def cli_add(self, text, fs):
        separator_string = " "
        file = separator_string.join(text)
        self.fs.path_set("%s" %file)
        self.fs.selected_set("%s" %file)
        logging.info("Loading %s..." %file)
        file = self.fs.selected_get()
        deb = file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        logging.info("Starting initial check...")
        if mimetype == "application/x-debian-package":
            deb = debianfile.DebPackage(file, cache=None)
            if deb.check() ==  False:
                logging.info("Initial check failed.")
                self.fs.selected_set(HOME)
                self.fs.path_set(HOME)
                checks.not_installable_popup(self.win)
            else:
                logging.info("Initial check passed.")
                chk = checks.Checks(file, self.win, end_callback=True)
                chk.check_file(self.fs, self.win)
        elif file == HOME or file == "%s/" %HOME:
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            return
        else:
            logging.info("Invalid file!")
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            checks.file_error_popup(self.win)
            return


    def init_check(self, fs, bt, win):
        file = self.fs.selected_get()
        deb = file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        if mimetype == "application/x-debian-package":
            deb = debianfile.DebPackage(file, cache=None)
            logging.info("Loading %s..." %file)
            logging.info("Starting initial check...")
            if deb.check() ==  False:
                logging.info("Initial check failed.")
                self.fs.selected_set(HOME)
                self.fs.path_set(HOME)
                checks.not_installable_popup(self.win)
            else:
                logging.info("Initial check passed.")
                chk = checks.Checks(file, self.win, end_callback=True)
                chk.check_file(self.fs, self.win)
        elif file == HOME or file == "%s/" %HOME:
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            return
        else:
            logging.info("Invalid file!")
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            checks.file_error_popup(self.win)
            return

    def bt_init_check(self, bt, win):
        file = self.fs.selected_get()
        chk = checks.Checks(file, self.win, end_callback=True)
        chk.check_file(self.fs, self.win)

    def inst_check(self, bt, win):
        file = self.fs.selected_get()
        chk = checks.Checks(file, self.win, end_callback=True)
        chk.check_file_install(self.fs, win)


#----- Main -{{{-
if __name__ == "__main__":
    elm.init()

    buttons_main(None)

    elm.run()
    elm.shutdown()
# }}}
# vim:foldmethod=marker
