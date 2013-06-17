#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import ecore
import elementary as elm
import evas
import checks
import mimetypes
import debfile as debianfile


"""                 eDeb

A deb-package installer built on Python-EFL's.
By: AntCer (bodhidocs@gmail.com)

Started: January 17, 2013
"""
HOME = os.getenv("HOME")

try:
    clargs = sys.argv[1:]
    if "-h" in " ".join(clargs) or "--help" in " ".join(clargs):
        print("usage: edeb [-h] [file]\n")
        print("An Elementary GUI debian package installer built on Python-EFLs\n")
        print("arguments:")
        print("\tfile\t\tDebian package to initially load.\n")
        print("optional arguments:")
        print("\t-h, --help\tShow this help message and exit.")
        quit()
except:
    clargs = False





class eDeb(object):
    def __init__(self, debclarg=False):
        self.deb = False
        clargs = debclarg

#----Main Window
        win = self.win = elm.StandardWindow("edeb", "eDeb")
        win.callback_delete_request_add(lambda o: elm.exit())

        vbox = elm.Box(win)
        vbox.size_hint_align_set(-1.0, -1.0)
        vbox.size_hint_weight_set(1.0, 1.0)
        vbox.show()

        fil = elm.Box(win)
        fil.size_hint_align_set(-1.0, -1.0)
        fil.size_hint_weight_set(1.0, 1.0)
        vbox.pack_end(fil)
        fil.show()

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
        fs.size_hint_weight_set(1.0, 0.0)
        fil.pack_end(fs)
        fs.show()

        fil = elm.Box(win)
        fil.size_hint_align_set(-1.0, -1.0)
        fil.size_hint_weight_set(1.0, 1.0)
        vbox.pack_end(fil)
        fil.show()

        bt = elm.Button(win)
        bt0 = elm.Button(win)

        bt.text = "Install"
        bt.size_hint_weight_set(1.0, 0.0)
        bt.size_hint_align_set(-1.0, -1.0)
        bt.callback_clicked_add(self.inst_check, bt0)
        fil.pack_end(bt)
        bt.show()

        bt0.text = "Package Info"
        bt0.size_hint_weight_set(1.0, 0.0)
        bt0.size_hint_align_set(-1.0, -1.0)
        bt0.callback_clicked_add(self.bt_wait)
        fil.pack_end(bt0)
        bt0.show()

        win.resize_object_add(vbox)
        #~ win.resize(425, 285)
        win.resize(460, 285)
        win.show()

#-------Add deb from CLI
        if clargs:
            path = clargs[0]
            if os.path.exists(path):
                self.fs.path_set("%s" %path)
                self.fs.selected_set("%s" %path)
                et = ecore.Timer(0.3, self.cli_add, path)

                self.n = n = elm.Notify(win)
                lb = elm.Label(self.win)
                lb.text = "<b>Loading Package Information...</b>"
                lb.size_hint_align = 0.0, 0.5
                lb.show()
                n.orient = 1
                n.allow_events_set(False)
                n.content = lb
                n.show()
            else:
                print("eDeb Error: Path, %s, does not exist." %path)
                checks.generic_error_popup(self.win, "<b>File does not exist</><br><br>Please select an appropriate file candidate for installation.")

#----Common
    def cli_add(self, path):
        print("Loading %s..." %path)
        path = self.fs.selected_get()
        deb = path
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        print("Starting initial check...")
        if mimetype == "application/x-debian-package":
            try:
                self.deb = debianfile.DebPackage(path, None)
            except:
                return False
            chk_fail = self.deb.check()
            if chk_fail != True:
                print("Initial check failed.")
                self.fs.selected_set(HOME)
                self.fs.path_set(HOME)
                checks.not_installable_popup(self.win, chk_fail)
            else:
                print("Initial check passed.\n")
                self.chk = checks.Checks(path, self.win)
                self.chk.check_file(self.fs, self.win, self.deb)
        elif path == HOME or path == "%s/" %HOME:
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
        else:
            print("Invalid file.")
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            checks.generic_error_popup(self.win, "<b>Invalid File Format</><br><br>That is <em>not</> a .deb file!")
        self.n.delete()

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
                print("Invalid file!")
                self.fs.selected_set(HOME)
                self.fs.path_set(HOME)
                checks.generic_error_popup(self.win, "<b>Invalid File Format</><br><br>That is <em>not</> a .deb file!")
                return
        else:
            self.fs.selected_set(fullpath)
            self.fs.path_set(fullpath)
            return

    def en_wait(self, fs):
        path = fs.selected_get()
        if os.path.exists(path):
            self.init_wait(fs, path)
        else:
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            checks.generic_error_popup(self.win, "<b>File does not exist</><br><br>Please select an appropriate file candidate for installation.")

    def bt_wait(self, bt):
        path = self.fs.selected_get()
        if path == HOME:
            checks.generic_error_popup(self.win, "<b>No File Selected</><br><br>Please select an appropriate file candidate for installation.")
        else:
            self.bt_init_check(path)

    def init_check(self, path):
        print("Loading %s..." %path)
        print("Starting initial check...")
        self.deb = debianfile.DebPackage(path, None)
        chk_fail = self.deb.check()
        if chk_fail != True:
            print("Initial check failed.")
            self.fs.selected_set(HOME)
            self.fs.path_set(HOME)
            checks.not_installable_popup(self.win, chk_fail)
        else:
            print("Initial check passed.\n")
            self.chk = checks.Checks(path, self.win)
            self.chk.check_file(self.fs, self.win, self.deb)
        self.n.delete()
        self.et.delete()

    def inst_check(self, bt, bt2):
        path = self.fs.selected_get()
        if path == HOME:
            checks.generic_error_popup(self.win, "<b>No File Selected</><br><br>Please select an appropriate file candidate for installation.")
        else:
            self.chk.check_file_install(bt, bt2, self.win, self.fs)

    def bt_init_check(self, path):
        try:
            self.chk.check_file(self.fs, self.win, self.deb)
        except:
            checks.generic_error_popup(self.win, "<b>No File Selected</><br><br>Please select an appropriate file candidate for installation.")


#----- Main -{{{-
if __name__ == "__main__":
    elm.init()

    eDeb(clargs)

    elm.run()
    elm.shutdown()
# }}}
# vim:foldmethod=marker
