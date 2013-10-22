config = dict()


################################################################################
# Global section
config['global'] = dict()
config['global']['center_cursor'] = 'yes'
config['global']['left_margin'] = '0'
config['global']['right_margin'] = '0'
config['global']['top_margin'] = '0'
config['global']['bottom_margin'] = '0'


################################################################################
# Hotkey section
config['hotkey'] = dict()

config['hotkey']['move_window_right'] = 'alt+shift+l'
config['hotkey']['move_window_left'] = 'alt+shift+j'
config['hotkey']['move_window_up'] = 'alt+shift+i'
config['hotkey']['move_window_down'] = 'alt+shift+k'
config['hotkey']['focus_right'] = 'alt+l'
config['hotkey']['focus_left'] = 'alt+j'
config['hotkey']['focus_up'] = 'alt+i'
config['hotkey']['focus_down'] = 'alt+k'

config['hotkey']['increase_column_left'] = 'ctrl+alt+j'
config['hotkey']['increase_column_right'] = 'ctrl+alt+l'

config['hotkey']['close_focused_window'] = 'alt+shift+q'

config['hotkey']['switch_to_group_1'] = 'alt+1'
config['hotkey']['switch_to_group_2'] = 'alt+2'
config['hotkey']['switch_to_group_3'] = 'alt+3'
config['hotkey']['switch_to_group_4'] = 'alt+4'
config['hotkey']['switch_to_group_5'] = 'alt+5'
config['hotkey']['switch_to_group_6'] = 'alt+6'
config['hotkey']['switch_to_group_7'] = 'alt+7'
config['hotkey']['switch_to_group_8'] = 'alt+8'
config['hotkey']['switch_to_group_9'] = 'alt+9'

config['hotkey']['send_to_group_1'] = 'alt+shift+1'
config['hotkey']['send_to_group_2'] = 'alt+shift+2'
config['hotkey']['send_to_group_3'] = 'alt+shift+3'
config['hotkey']['send_to_group_4'] = 'alt+shift+4'
config['hotkey']['send_to_group_5'] = 'alt+shift+5'
config['hotkey']['send_to_group_6'] = 'alt+shift+6'
config['hotkey']['send_to_group_7'] = 'alt+shift+7'
config['hotkey']['send_to_group_8'] = 'alt+shift+8'
config['hotkey']['send_to_group_9'] = 'alt+shift+9'

config['hotkey']['move_to_previous_monitor'] = 'alt+shift+u'
config['hotkey']['move_to_next_monitor'] = 'alt+shift+o'
config['hotkey']['focus_previous_monitor'] = 'alt+u'
config['hotkey']['focus_next_monitor'] = 'alt+o'

config['hotkey']['toggle_stacked_column'] = 'alt+s'
config['hotkey']['toggle_tiled_floating'] = 'alt+shift+space'
config['hotkey']['toggle_window_decoration'] = 'alt+shift+d'
config['hotkey']['toggle_taskbar_visibility'] = 'alt+t'

config['hotkey']['print_focused_window_classname'] = 'alt+p'    # for debug
config['hotkey']['stop_pythonwindowstiler'] = 'alt+shift+delete'


################################################################################
# Window section
config['window'] = dict()

config['window']['float'] = [
    '#32770',               # task manager and other popups
    'progman',              # windows program manager?
    'ConsoleWindowClass'    # command prompt window is weird
]

config['window']['decorate'] = [
    'Chrome_WidgetWin_0',   # chrome browser, needs its own border decoration
    'Chrome_WidgetWin_1',   # chrome browser, needs its own border decoration
]

