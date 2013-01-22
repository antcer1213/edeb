#!/usr/bin/env python
# encoding: utf-8
import os
import elementary
import edje
import ecore
import evas
import mimetypes
import getpass, pwd, time#, crypt   -FUTURE
#~ import commands                  -FUTURE

"""eDeb

A deb package installer built on Python-EFL's.
By: AntCer (bodhidocs@gmail.com)

Started: January 17, 2013
"""
#----M.V.P.
def buttons_main(obj, item=None):

#----Common
    def run_command(bnt, window, command):
        cmd = ecore.Exe(command)

    def destroy(obj):
        elementary.exit()

    def popup_close(btn, popup):
        popup.delete()

#----Popups
    def file_error_popup(bt, win):
        popup = elementary.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Invalid File Format</><br><br>That is <em>not</> a .deb file!"
        popup.timeout = 3.0
        popup.show()

    def pw_error_popup(bt, win1):
        popup = elementary.Popup(win1)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Password Error</><br><br>Password & confirmation password did <em>not</> match!"
        popup.timeout = 3.0
        popup.show()

    def finished_popup(bt, win):
        popup = elementary.Popup(win)
        popup.size_hint_weight = (evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        popup.text = "<b>Installation Finished!</>"
        bt = elementary.Button(win)
        bt.text = "Close"
        bt.size_hint_align_set(0.5, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bt.callback_clicked_add(popup_close, popup)
        popup.part_content_set("button1", bt)
        popup.show()
        win.resize_object_add(popup)
        

#----Checks
    #~ def file_selected(fse, bt, win): -FUTURE
        #~ file = fse.selected_get()
        #~ deb = file
        #~ mimetype = mimetypes.guess_type (deb, strict=1)[0]
        #~ if not mimetype == "application/x-debian-package":
            #~ print("Invalid file")
            #~ return

    def file_selected2(bt, win):
        file = fse.selected_get()
        deb = file
        mimetype = mimetypes.guess_type (deb, strict=1)[0]
        if not mimetype == "application/x-debian-package":
            print("Invalid file")
            file_error_popup(bt, win)
            return
        else:
            print(file)
            esudo(None)

#----eSudo
    def esudo(win1):
        #~ def password_check(bt, en, en1): -FUTURE
            #~ str = en.entry_get()
            #~ str1 = en1.entry_get()
            #~ allegedpwd = str
            #~ username = getpass.getuser()
            #~ cryptpwd = pwd.getpwnam(username)[1]
            #~ realpwd = crypt.crypt(allegedpwd, cryptpwd)
            #~ print(username, cryptpwd, realpwd)-Debugging Purposes
            #~ if not str == str1:
                #~ pw_error_popup(bt, win1)
                #~ en.entry_set("")
                #~ en1.entry_set("")
                #~ return
            #~ else:
                #~ esudo_ok(bt, en)

        def esudo_cancel(bt, en):
            en.entry_set("")
            en1.entry_set("")
            win1.delete()

        def esudo_ok(bt, en, en1):
            file = fse.selected_get()
            str = en.entry_get()
            str1 = en1.entry_get()
            if not str == str1:
                pw_error_popup(bt, win1)
                en.entry_set("")
                en1.entry_set("")
                return
            else:
                run_command(False, False, "echo %s | sudo -S dpkg -i %s" %(str, file))
                time.sleep(10)
                print("Installation Finished.")
                win1.delete()
                finished_popup(bt, win)


        win1 = elementary.Window("eSudo", elementary.ELM_WIN_BASIC)
        win1.title_set("eSudo")
        win1.borderless_set(True)
        win1.focus_allow_set(True)
        win1.focus_set(True)
        win1.center(True, True)
        win1.autodel_set(True)

        bg = elementary.Background(win1)
        win1.resize_object_add(bg)
        bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        bg.show()

        bz = elementary.Box(win1)
        win1.resize_object_add(bz)
        bz.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)

        fr = elementary.Frame(win1)
        fr.text_set("eSudo")
        bz.pack_end(fr)

        sep = elementary.Separator(win1)
        sep.horizontal_set(True)
        bz.pack_end(sep)
        sep.show()

        bz1 = elementary.Box(win1)
        bz.pack_end(bz1)
        bz1.show()

        lb = elementary.Label(win1)
        lb.text = "<b>Password:</b>"
        lb.size_hint_align = (0.0, 0.5)
        bz1.pack_end(lb)
        lb.show()

        en = elementary.Entry(win1)
        en.single_line = True
        en.line_wrap_set(False)
        en.input_panel_return_key_disabled = True
        en.password = True
        en.size_hint_weight_set(0.5, 0.5)
        en.size_hint_align_set(0.5, 0.5)
        bz1.pack_end(en)
        en.show()

        bz2 = elementary.Box(win1)
        bz.pack_end(bz2)
        bz2.show()

        lb = elementary.Label(win1)
        lb.text = "<b>Confirm Password:</b>"
        lb.size_hint_align = (0.0, 0.5)
        bz2.pack_end(lb)
        lb.show()

        en1 = elementary.Entry(win1)
        en1.single_line = True
        en1.line_wrap_set(False)
        en1.input_panel_return_key_disabled = True
        en1.password = True
        en1.size_hint_weight_set(0.5, 0.5)
        en1.size_hint_align_set(0.5, 0.5)
        bz2.pack_end(en1)
        en1.show()

        sep = elementary.Separator(win1)
        sep.horizontal_set(True)
        bz.pack_end(sep)
        sep.show()

        bz.show()
        fr.show()

        bx2 = elementary.Box(win1)
        bx2.horizontal_set(True)
        bx2.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bx2.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        bt = elementary.Button(win1)
        bt.text_set("Cancel")
        bt.callback_clicked_add(esudo_cancel, en)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bx2.pack_end(bt)
        bt.show()

        bt = elementary.Button(win1)
        bt.text_set("OK")
        #~ bt.callback_clicked_add(password_check, en, en1)
        bt.callback_clicked_add(esudo_ok, en, en1)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
        bx2.pack_end(bt)
        bt.show()

        bz.pack_end(bx2)
        bx2.show()

        en.focus_set(True)
        win1.resize(200, 100)
        win1.show()

#----Main Window
    win = elementary.Window("eDeb", elementary.ELM_WIN_BASIC)
    win.title = "eDeb"
    if obj is None:
        win.callback_delete_request_add(lambda o: elementary.exit())

    bg = elementary.Background(win)
    bg.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bg.show()

    vbox = elementary.Box(win)
    vbox.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    vbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    vbox.show()

    sep = elementary.Separator(win)
    sep.horizontal_set(True)
    vbox.pack_end(sep)
    sep.show()

    fse = elementary.FileselectorEntry(win)
    fse.text_set("Select .deb file")
    fse.window_title_set("Select a .deb file:")
    fse.expandable_set(False)
    fse.inwin_mode_set(False)
    fse.path_set(os.getenv("HOME"))
    #~ fse.callback_file_chosen_add(file_selected, win)
    fse.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    fse.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    vbox.pack_end(fse)
    fse.show()

    sep = elementary.Separator(win)
    sep.horizontal_set(True)
    vbox.pack_end(sep)
    sep.show()

    hbox = elementary.Box(win)
    hbox.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
    hbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    hbox.horizontal_set(True)
    vbox.pack_end(hbox)
    hbox.show()

    bt = elementary.Button(win)
    bt.text_set("Install")
    bt.callback_clicked_add(file_selected2, win)
    bt.size_hint_align_set(0.5, evas.EVAS_HINT_FILL)
    bt.size_hint_weight_set(evas.EVAS_HINT_EXPAND, 0.0)
    hbox.pack_end(bt)
    bt.show()

    sep = elementary.Separator(win)
    sep.horizontal_set(True)
    hbox.pack_end(sep)
    sep.show()

    win.resize_object_add(bg)
    win.resize_object_add(vbox)
    win.resize_object_add(fse)
    win.resize_object_add(hbox)
    win.resize_object_add(bt)
    win.resize(350, 100)
    win.show()

#----- Main -{{{-
if __name__ == "__main__":
    elementary.init()

    buttons_main(None)

    elementary.run()
    elementary.shutdown()
# }}}
# vim:foldmethod=marker
