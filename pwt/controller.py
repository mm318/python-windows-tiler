import pwt.config

from pwt.notifyicon import NotifyIcon
from pwt.hotkey     import Hotkey
from pwt.monitor    import Monitor
from pwt.window     import Window
from pwt.taskbar    import Taskbar
from pwt.utility    import Utility
from pwt.hotkey     import keys # KEYS

from win32con import WM_HOTKEY
from win32con import HSHELL_WINDOWCREATED
from win32con import HSHELL_WINDOWDESTROYED
from win32con import CF_TEXT

import logging


class Controller(object):
    def __init__(self, name):
        '''
        Set up the notifyicon and the monitors
        '''
        self.group = 0
        self.ICONFOLDER = 'icons/'

        # the events that trigger the removal of a window
        self.REMOVE_EVENTS = (
            HSHELL_WINDOWDESTROYED,
            # placeholder
        )

        # the events that trigger an additional window
        self.ADD_EVENTS = (
            HSHELL_WINDOWCREATED,
            # placeholder
        )

        self.monitors = Monitor.display_monitors()
        if self.monitors is not None:
            self.stop = False
        else:
            self.stop = True

        self.notifyicon = NotifyIcon(name, self.icon)
        self.add_hotkeys_to_notifyicon()
        self.notifyicon.register_hotkeys()
        self.notifyicon.register_shellhook() 

        self.taskbar = Taskbar()
        self.taskbar.show()

        self.windows = dict()

    @property
    def icon(self):
        'Return the appropriate icon'
        return self.ICONFOLDER + str(self.group + 1) + '.ico'

    @property
    def current_tiler(self):
        'Returns the current tiler'
        return Monitor.current_monitor_from_list(self.monitors).tilers[self.group]

    def start(self):
        'start the listeners with a safety try/finally to unregister keys and kill the icon'
        self.notifyicon.show_balloon('Go!', 'PWT')

        # Do an initial lookup of all the windows and tile accordingly
        for monitor in self.monitors:
            windows = Window.valid_windows_from_monitor(monitor)
            for window in windows:
                self.add_window(monitor.tilers[self.group], window)
            monitor.tilers[self.group].tile_windows()

        try:
            # message priming read
            message = self.notifyicon.windowmessage

            while message:
                if message[1][1] == WM_HOTKEY:
                    # if message is WM_HOTKEY
                    # execute the corresponding hotkeycmd using the id
                    self.notifyicon.hotkeys[message[1][2]-1].execute()
                elif message[1][2] in self.ADD_EVENTS:
                    # if lparam is an add event
                    window = Window(message[1][3])
                    self.add_window(self.current_tiler, window)
                elif message[1][2] in self.REMOVE_EVENTS:
                    #if lparam is a remove event
                    self.handle_remove_event(message[1][3], Monitor.monitor_from_point_in_list(
                        self.monitors, message[1][5]))
                if self.stop:
                    self.notifyicon.show_balloon('Stopping!', 'PWT')
                    break

                # Grab the next message from the message queue
                message = self.notifyicon.windowmessage
        except:
            logging.exception('Exception occurred')

        self.notifyicon.unregister_shellhook()  # Unregister shellhook
        self.notifyicon.unregister_hotkeys()    # Unregister hotkeys
        self.decorate_all_tiled_windows()   # Decorate windows
        self.taskbar.show()                 # make sure the taskbar is shown on exit
        self.notifyicon.destroy()           # Remove icon

    def add_window(self, tiler, window):
        '''
        adds window to the tiling system
        '''
        old_tiler = None
        if(window.hWindow in self.windows):
            # sometimes a new window opens up to the same window
            window = self.windows[window.hWindow]
            # expect alredy existing window to have a valid tiler parent
            old_tiler = window.container.container.container
        else:
            if not(window.must_decorate):
                window.undecorate()
            window.update()
            self.windows[window.hWindow] = window

        if(tiler != old_tiler):
            if(old_tiler != None):
                old_tiler.remove_window(window)
            tiler.add_window(window)

    def handle_remove_event(self, win_handle, monitor):
        '''
        Triggered when a window needs to be removed
        '''
        if(win_handle in self.windows):
            tiler = monitor.tilers[self.group]
            tiler.remove_window(self.windows[win_handle])
            del self.windows[win_handle]

    # def show_all_windows(self):
    #     '''
    #     Called during exit
    #     Resets all windows to be visible so that windows that were
    #     invisible due workspaces are now usable, too
    #     '''
    #     for monitor in self.monitors:
    #         for tiler in monitor.tilers:
    #             tiler.show_all_windows()

    def decorate_all_tiled_windows(self):
        '''
        Called during exit
        Decorates all windows in the tiler's memory
        '''
        for monitor in self.monitors:
            for tiler in monitor.tilers:
                tiler.decorate_all_tiled_windows()

    def switch_group(self, i):
        '''
        Switch the current group into group i
        '''
        for monitor in self.monitors:
            monitor.tilers[self.group].hide_windows()
            monitor.tilers[i].show_windows()
            monitor.tilers[i].tile_windows()
        self.group = i
        self.notifyicon.draw_icon(self.icon)
        # Monitor.refresh_all_windows()

        # find new window to focus on (method 1)
        # new_curr_win = Window.window_under_cursor(self.windows)
        # if(new_curr_win != None):
        #     self.send_window_to_tiler(new_curr_win, i)
        #     new_curr_win.focus()
        # else:
        #     # other windows should lose focus
        #     # self.notifyicon.focus()
        #     self.taskbar.taskbar.focus()

        # find new window to focus on (method 2)
        curr_mon = Monitor.current_monitor_from_list(self.monitors)
        curr_win = curr_mon.tilers[i].get_current_window()
        if(curr_win != None):
            curr_win.focus()
        else:
            # other windows should lose focus
            # self.notifyicon.focus()
            self.taskbar.taskbar.focus()


    def send_window_to_tiler(self, window, i):
        '''
        sends window to tiler i
        '''
        currentMonitor = Monitor.monitor_from_window_in_list(self.monitors, window)
        currentTiler = window.container.container.container
        targetTiler = currentMonitor.tilers[i]
        if(targetTiler != currentTiler):
            currentTiler.remove_window(window)
            if(targetTiler.currentLayout.has_window(window)):
                logging.error('Window "%s" already in destination tiler', window.get_name())
            else:
                targetTiler.currentLayout.add_window(window)
            window.hide()   # hide the window from current tiler
            currentTiler.tile_windows()

            curr_window = currentTiler.get_current_window()
            if(curr_window != None):
                curr_window.focus()
            else:
                # other windows should lose focus
                # self.notifyicon.focus()
                self.taskbar.taskbar.focus()


    def add_hotkeys_to_notifyicon(self):
        config = pwt.config.config
        for (i, func) in enumerate(config['hotkey']):
            keycombos = config['hotkey'][func].split('+')
            mods = sum([keys[x] for x in keycombos[:-1]])
            
            try:
                vk = keys[keycombos[-1]]
            except KeyError:
                vk = ord(keycombos[-1].upper())
                
            self.notifyicon.hotkeys.append(Hotkey(i+1, mods, vk,
                getattr(self, 'cmd_' + func)))


    ###
    #Hotkey cmds
    ###

    def cmd_move_window_left(self):
        curr_win = Window.focused_window(self.windows)
        if(curr_win != None):
            curr_win.move_left()

    def cmd_move_window_right(self):
        curr_win = Window.focused_window(self.windows)
        if(curr_win != None):
            curr_win.move_right()

    def cmd_move_window_up(self):
        curr_win = Window.focused_window(self.windows)
        if(curr_win != None):
            curr_win.move_up()

    def cmd_move_window_down(self):
        curr_win = Window.focused_window(self.windows)
        if(curr_win != None):
            curr_win.move_down()

    def cmd_focus_left(self):
        curr_win = Window.focused_window(self.windows)
        # if(curr_win == None):
            # curr_win = self.windows.values()[0]
        if(curr_win != None):
            curr_win.change_focus_left()

    def cmd_focus_right(self):
        curr_win = Window.focused_window(self.windows)
        # if(curr_win == None):
            # curr_win = self.windows.values()[0]
        if(curr_win != None):
            curr_win.change_focus_right()

    def cmd_focus_up(self):
        curr_win = Window.focused_window(self.windows)
        # if(curr_win == None):
            # curr_win = self.windows.values()[0]
        if(curr_win != None):
            curr_win.change_focus_up()

    def cmd_focus_down(self):
        curr_win = Window.focused_window(self.windows)
        # if(curr_win == None):
            # curr_win = self.windows.values()[0]
        if(curr_win != None):
            curr_win.change_focus_down()

    def cmd_increase_column_left(self):
        pass

    def cmd_increase_column_right(self):
        pass

    def cmd_close_focused_window(self):
        window = Window.focused_window(self.windows)
        window.container.container.remove_window(window)
        window.close()


    def cmd_switch_to_group_1(self):
        if(self.group != 0):
            self.switch_group(0)

    def cmd_switch_to_group_2(self):
        if(self.group != 1):
            self.switch_group(1)

    def cmd_switch_to_group_3(self):
        if(self.group != 2):
            self.switch_group(2)

    def cmd_switch_to_group_4(self):
        if(self.group != 3):
            self.switch_group(3)

    def cmd_switch_to_group_5(self):
        if(self.group != 4):
            self.switch_group(4)

    def cmd_switch_to_group_6(self):
        if(self.group != 5):
            self.switch_group(5)

    def cmd_switch_to_group_7(self):
        if(self.group != 6):
            self.switch_group(6)

    def cmd_switch_to_group_8(self):
        if(self.group != 7):
            self.switch_group(7)

    def cmd_switch_to_group_9(self):
        if(self.group != 8):
            self.switch_group(8)


    def cmd_send_to_group_1(self):
        if(self.group != 0):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 0)

    def cmd_send_to_group_2(self):
        if(self.group != 1):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 1)

    def cmd_send_to_group_3(self):
        if(self.group != 2):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 2)

    def cmd_send_to_group_4(self):
        if(self.group != 3):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 3)

    def cmd_send_to_group_5(self):
        if(self.group != 4):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 4)

    def cmd_send_to_group_6(self):
        if(self.group != 5):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 5)

    def cmd_send_to_group_7(self):
        if(self.group != 6):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 6)

    def cmd_send_to_group_8(self):
        if(self.group != 7):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 7)

    def cmd_send_to_group_9(self):
        if(self.group != 8):
            window = Window.focused_window(self.windows) 
            if(window):
                self.send_window_to_tiler(window, 8)


    def cmd_move_to_previous_monitor(self):
        window = Window.focused_window(self.windows)
        # if(window.validate()):
        monitor = Monitor.monitor_from_window_in_list(self.monitors, window)
        previousMonitor = Utility.previous_item(self.monitors, monitor)
        if(monitor != previousMonitor):
            tiler = monitor.tilers[self.group]
            previousTiler = previousMonitor.tilers[self.group]
            tiler.remove_window(window)
            previousTiler.add_window(window)
            window.focus()

    def cmd_move_to_next_monitor(self):
        window = Window.focused_window(self.windows)
        # if(window.validate()):
        monitor = Monitor.monitor_from_window_in_list(self.monitors, window)
        nextMonitor = Utility.next_item(self.monitors, monitor)
        if(monitor != nextMonitor):
            tiler = monitor.tilers[self.group]
            nextTiler = nextMonitor.tilers[self.group]
            tiler.remove_window(window)
            nextTiler.add_window(window)
            window.focus()

    def cmd_focus_next_monitor(self):
        monitor = Monitor.current_monitor_from_list(self.monitors)
        nextMonitor = Utility.next_item(self.monitors, monitor)
        if(nextMonitor and nextMonitor.tilers[self.group].has_windows()):
            window = nextMonitor.tilers[self.group].get_current_window()
            if(window != None):
                window.focus()

    def cmd_focus_previous_monitor(self):
        monitor = Monitor.current_monitor_from_list(self.monitors) 
        previousMonitor = Utility.previous_item(self.monitors, monitor)
        if(previousMonitor and previousMonitor.tilers[self.group].has_windows()):
            window = previousMonitor.tilers[self.group].get_current_window()
            if(window != None):
                window.focus()

    def cmd_toggle_stacked_column(self):
        win = Window.focused_window(self.windows)
        if(win != None and win.container.toggle_stacking()):
            win.container.container.container.tile_windows()

    def cmd_toggle_tiled_floating(self):
        win = Window.focused_window(self.windows)
        if(win != None):
            if(win.floating):
                win.tile()
            else:
                win.float()

    def cmd_toggle_window_decoration(self):
        Window.focused_window(self.windows).toggle_decoration()

    def cmd_toggle_taskbar_visibility(self):
        self.taskbar.toggle_visibility()
        curmonitor = Monitor.current_monitor_from_list(self.monitors)
        curmonitor.recalc_tiler_dimensions()
        self.current_tiler.tile_windows()


    def cmd_print_focused_window_classname(self):
        class_name = Window.focused_window(self.windows).classname
        self.notifyicon.show_balloon(class_name, 'PWT2')
        logging.debug(class_name)
        print(class_name)

    def cmd_stop_pythonwindowstiler(self):
        self.stop = True

