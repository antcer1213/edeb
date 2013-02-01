#!/usr/bin/env python
# encoding: utf-8
import os
import elementary as elm
import evas
import checks

"""eDeb

A deb-package installer built on Python-EFL's.
By: AntCer (bodhidocs@gmail.com)

Uses a slightly modified eSudo, initially made
by Anthony Cervantes, now maintained by Jeff Hoogland,
and improved upon further by Kai Huuko.

Started: January 17, 2013
"""




def buttons_main(obj, item=None):

#----Common
    def init_check(fs, bt, win):
        file = fs.selected_get()
        chk = checks.Checks(file, win, end_callback=False)
        chk.check_file_initial(fs, win)

    def bt_init_check(bt, win):
        file = fs.selected_get()
        chk = checks.Checks(file, win, end_callback=False)
        chk.check_file_initial(fs, win)

    def inst_check(bt, win):
        file = fs.selected_get()
        chk = checks.Checks(file, win, end_callback=False)
        chk.check_file_install(fs, win)

#----Main Window
    win = elm.StandardWindow("edeb", "eDeb")
    win.callback_delete_request_add(lambda o: elm.exit())

    vbox = elm.Box(win)
    vbox.padding_set(5, 20)
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

    fs = elm.FileselectorEntry(win)
    fs.text_set("Select .deb file")
    fs.window_title_set("Select a .deb file:")
    fs.expandable_set(False)
    fs.inwin_mode_set(False)
    fs.path_set(os.getenv("HOME"))
    fs.callback_file_chosen_add(init_check, win)
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
    bt.callback_clicked_add(inst_check, win)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    btbox.pack_end(bt)
    bt.show()

    bt = elm.Button(win)
    bt.text_set("Package Info")
    bt.callback_clicked_add(bt_init_check, win)
    bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    btbox.pack_end(bt)
    bt.show()

    sep = elm.Separator(win)
    sep.horizontal_set(True)
    vbox.pack_end(sep)
    sep.show()

    win.resize_object_add(vbox)
    win.resize(425, 200)
    win.show()

#----- Main -{{{-
if __name__ == "__main__":
    elm.init()

    buttons_main(None)

    elm.run()
    elm.shutdown()
# }}}
# vim:foldmethod=marker
