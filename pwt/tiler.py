from pwt.layout     import Layout
from pwt.window     import Window
from pwt.utility    import Utility

import pwt.config

class Tiler(object):
    def __init__(self, name, workarea):
        self.name = name
        self.calc_dimensions(workarea)
        self.currentLayout = Layout(self, self.left, self.top, self.width, self.height)

    def calc_dimensions(self, workarea):
        # workarea: rectangle = (left, top, right, bottom)
        config = pwt.config.config
        
        self.left = workarea[0] + int(config['global']['left_margin'])
        self.top = workarea[1] + int(config['global']['top_margin'])

        self.width = workarea[2] - int(config['global']['right_margin']) - self.left
        self.height = workarea[3] - int(config['global']['bottom_margin']) - self.top

    def has_windows(self):
        return self.currentLayout.has_windows()

    def get_current_window(self):
        return self.currentLayout.get_current_window()


    ############################################
    ### Start of the commands
    ############################################

    def tile_windows(self):
        '''
        Tiles all windows by feeding it to the layout
        '''
        self.currentLayout.tile_columns()

    def hide_windows(self):
        self.currentLayout.hide_windows()

    def show_windows(self):
        self.currentLayout.show_windows()

    def add_window(self, window):
        '''
        Adds the window to the list and retiles the setup
        '''
        if(not self.currentLayout.has_window(window) and window.validate()):
            self.currentLayout.add_window(window)
            self.tile_windows()

    def remove_window(self, window):
        '''
        Removes the window from the list and retiles the setup
        '''
        if(self.currentLayout.has_window(window)):
            self.currentLayout.remove_window(window)
            self.tile_windows()

    def decorate_all_tiled_windows(self):
        '''
        put title bar back onto all the windows under the tiler
        usually called when exiting the program
        '''
        self.currentLayout.decorate_all_tiled_windows()

