from pwt.utility import Utility
import logging


class SubContainer(object):
    def __init__(self, container):
        self.container = container  # should be Layout object
        self.windows = list()
        self.curr_win_index = 0

    def has_windows(self):
        return (len(self.windows) >= 1)

    def has_window(self, window):
        if(window in self.windows):
            return True
        else:
            logging.warning('Window "%s" not in column' % windows.get_name())
            # need to renumerate windows
            return False

    # updates self.curr_win_index in case the user focused a different
    # window using the mouse or something
    def sync_curr_window(self, curr_win):
        if(curr_win != self.windows[self.curr_win_index]):
            logging.warning('Current window is "%s" but expected "%s"'
                % (curr_win.get_name(), self.windows[self.curr_win_index].get_name()))
            if(self.has_window(curr_win)):
                self.curr_win_index = self.windows.index(curr_win)
                return True
            else:
                logging.error('Current window "%s" is not in column' % curr_win.get_name())
                return False
        else:
            return True

    def remove_window(self, window):
        try:
            self.windows.remove(window)
            window.container = None
            if(self.curr_win_index >= len(self.windows)):
                self.curr_win_index = len(self.windows)-1
            logging.debug('Removed window "%s"' % window.get_name())
        except ValueError:
            logging.exception('Failed to remove window from column')


    def change_focus_left(self, curr_win):
        self.sync_curr_window(curr_win)
        layout = self.container

        new_col_index = layout.curr_col_index - 1
        if(new_col_index < 0):
            new_col_index = 0

        if(layout.columns[new_col_index].has_windows()):
            layout.curr_col_index = new_col_index
            col = layout.columns[layout.curr_col_index]
            col.windows[col.curr_win_index].focus()

    def change_focus_right(self, curr_win):
        self.sync_curr_window(curr_win)
        layout = self.container

        new_col_index = layout.curr_col_index + 1
        if(new_col_index >= len(layout.columns)):
            new_col_index = len(layout.columns) - 1

        if(layout.columns[new_col_index].has_windows()):
            layout.curr_col_index = new_col_index
            col = layout.columns[layout.curr_col_index]
            col.windows[col.curr_win_index].focus()

    def change_focus_up(self, curr_win):
        self.sync_curr_window(curr_win)
        self.curr_win_index = self.windows.index(curr_win) - 1
        if(self.curr_win_index < 0):
            self.curr_win_index = 0
        self.windows[self.curr_win_index].focus()

    def change_focus_down(self, curr_win):
        self.sync_curr_window(curr_win)
        self.curr_win_index = self.windows.index(curr_win) + 1
        if(self.curr_win_index >= len(self.windows)):
            self.curr_win_index = len(self.windows) - 1
        self.windows[self.curr_win_index].focus()


WINDOW_VERTICAL_NON_OVERLAP = 20    # pixels

class Column(SubContainer):
    def __init__(self, container, width):
        super(Column, self).__init__(container)
        self.width = width
        self.stacked = True # stacked or tiled

    def is_tiling(self):
        return True # to differentiate between tiling or floating

    def toggle_stacking(self):
        self.stacked = not(self.stacked)
        return self.is_tiling()

    def add_window(self, window):
        if(window.floating):
            logging.error('Attempted to add floating window to Column')
            return False
        self.windows.insert(self.curr_win_index, window)
        window.container = self
        logging.debug('Added window "%s"' % window.get_name())


    def move_left(self, curr_win):
        # print('move left requested on column')  #__debug__

        if(self.sync_curr_window(curr_win)):
            self.container.move_window_left(self, curr_win)
        else:
            logging.error('Window not found. Unable to move window left.')

    def move_right(self, curr_win):
        # print('move right requested on column') #__debug__

        if(self.sync_curr_window(curr_win)):
            self.container.move_window_right(self, curr_win)
        else:
            logging.error('Window not found. Unable to move window right.')

    def move_up(self, curr_win):
        self.sync_curr_window(curr_win)
        if(self.curr_win_index > 0):
            curr_index = self.curr_win_index
            new_index = self.curr_win_index - 1

            (self.windows[new_index], self.windows[curr_index]) = (
                self.windows[curr_index], self.windows[new_index])
            self.curr_win_index = new_index
            self.container.tile_columns()

    def move_down(self, curr_win):
        self.sync_curr_window(curr_win)
        if(self.curr_win_index < len(self.windows)-1):
            curr_index = self.curr_win_index
            new_index = self.curr_win_index + 1

            (self.windows[new_index], self.windows[curr_index]) = (
                self.windows[curr_index], self.windows[new_index])
            self.curr_win_index = new_index
            self.container.tile_columns()

    def tile_stacked_rows(self, top, height, current_left, current_right):
        global WINDOW_VERTICAL_NON_OVERLAP
        success = True
        if not(self.has_windows()):
            return success

        # stacked windows behavior
        current_top = top
        current_bottom = top + height - WINDOW_VERTICAL_NON_OVERLAP*(len(self.windows)-1)
        for win in self.windows:
            position = (current_left, current_top, current_right, current_bottom)
            if not(win.position(position)):
                success = False
                # self.remove_window(win)
                self.container.float_window(win)
                break
            win.update()
            win.show()
            current_top += WINDOW_VERTICAL_NON_OVERLAP
            current_bottom += WINDOW_VERTICAL_NON_OVERLAP

        return success

    def tile_tiled_rows(self, top, height, current_left, current_right):
        success = True
        if not(self.has_windows()):
            return success

        # tiled windows behavior
        win_height = height // len(self.windows)
        current_top = top
        for win in self.windows:
            current_bottom = current_top + win_height
            position = (current_left, current_top, current_right, current_bottom)
            if not(win.position(position)):
                success = False
                # self.remove_window(win)
                self.container.float_window(win)
                break
            win.update()
            win.show()
            current_top = current_bottom

        return success

    def tile_rows(self, top, height, current_left, current_right):
        if(self.stacked):
            return self.tile_stacked_rows(top, height, current_left, current_right)
        else:
            return self.tile_tiled_rows(top, height, current_left, current_right)


class FloatingWindows(SubContainer):
    def __init__(self, container):
        super(FloatingWindows, self).__init__(container)

    def is_tiling(self):
        return False    # to differentiate between tiling or floating

    def toggle_stacking(self):
        return self.is_tiling()

    def add_window(self, window):
        if not(window.floating):
            logging.error('Attempted to add non-floating window to FloatingWindows')
            return False
        self.windows.insert(self.curr_win_index, window)
        window.container = self
        logging.debug('Added window "%s"' % window.get_name())


    def move_left(self, curr_win):
        self.sync_curr_window(curr_win) # for checking purposes only

    def move_right(self, curr_win):
        self.sync_curr_window(curr_win) # for checking purposes only

    def move_up(self, curr_win):
        self.sync_curr_window(curr_win) # for checking purposes only

    def move_down(self, curr_win):
        self.sync_curr_window(curr_win) # for checking purposes only


    def tile_rows(self, current_left, current_right):
        logging.error('FloatingWindows does not support tiling')


class Layout(object):
    def __init__(self, tiler, left, top, width, height):
        self.container = tiler  # must be a Tiler object
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        self.columns = [FloatingWindows(self), Column(self, width)]
        self.curr_col_index = len(self.columns) - 1

    def has_windows(self):
        result = False
        for col in self.columns:
            if(col.has_windows()):
                result = True
                break
        return result

    def has_window(self, window):
        '''
        checks if window is in this layout
        '''
        col = window.container
        if(col in self.columns and col.has_window(window)):
            return True
        else:
            logging.warning('Window "%s" not in layout' % window.get_name())
            # need to renumerate windows
            return False

    def sync_curr_column(self, curr_col):
        if(curr_col != self.columns[self.curr_col_index]):
            logging.warning('Current column is out of sync')
            try:
                self.curr_col_index = self.columns.index(curr_col)
                return True
            except:
                logging.exception('Failed to find current column')
                return False
        else:
            return True

    def num_tiling_columns(self):
        return (len(self.columns)-1)

    def get_tiling_columns(self):
        col_iter = self.columns.__iter__()
        col_iter.next()
        return col_iter

    def reset_column_widths(self):
        # resetting column widths
        width_per_column = self.width // self.num_tiling_columns()
        for col in self.get_tiling_columns():
            col.width = width_per_column

    def get_current_window(self):
        curr_col = self.columns[self.curr_col_index]
        if(curr_col.has_windows()):
            return curr_col.windows[curr_col.curr_win_index]
        else:
            return None

    def add_window(self, window):
        '''
        adds window to this layout
        '''
        if(window.floating):
            self.columns[0].add_window(window)
        else:
            # adding window to existing non-floating column
            if(self.curr_col_index == 0):
                self.columns[1].add_window(window)
            else:
                self.columns[self.curr_col_index].add_window(window)

    def remove_column(self, column):
        if(column.has_windows()):
            logging.error('Failed to remove non-empty column from layout')
        else:
            try:
                # removing an empty column
                self.columns.remove(column)
                if(self.curr_col_index >= len(self.columns)):
                    self.curr_col_index = len(self.columns)-1
                self.reset_column_widths()
            except ValueError:
                logging.exception('Failed to remove column from layout')

    def remove_window(self, window):
        '''
        remove window from this layout (no checks)
        '''
        column = window.container
        column.remove_window(window)

        # remove superfluous column if applicable
        # always keep at least one tiling column
        if(not column.has_windows() and self.num_tiling_columns() > 1 and column.is_tiling()):
            self.remove_column(column)

    def tile_columns(self):
        '''
        Tiles the windows with manual control
        '''
        retry_tiling = False

        current_left = self.left
        for col in self.get_tiling_columns():
            if(col.width <= 0):
                self.reset_column_widths()
                retry_tiling = True
            else:
                current_right = current_left + col.width
                retry_tiling |= not(col.tile_rows(self.top, self.height, current_left, current_right))
                current_left = current_right

            if(retry_tiling):
                logging.debug('Needed to retry tiling')
                break

        if(retry_tiling):
            self.tile_columns()

    def hide_windows(self):
        for column in self.columns:
            for window in column.windows:
                window.hide()

    def show_windows(self):
        for column in self.columns:
            for window in column.windows:
                window.show()

    def move_window_left(self, curr_col, curr_win):
        # print('move left requested on layout') #__debug__

        # assume valid self.curr_col_index after this
        if not(self.sync_curr_column(curr_col)):
            # print('failed to sync current column')  #__debug__
            return

        curr_col = self.columns[self.curr_col_index]
        if(self.curr_col_index == 1):
            # create a new column since we're currently at the leftmost column
            self.columns.insert(1, Column(self, -1))
        else:
            self.curr_col_index -= 1

        new_col = self.columns[self.curr_col_index]
        if(new_col != curr_col):
            curr_col.remove_window(curr_win)
            new_col.add_window(curr_win)

            if not(curr_col.has_windows()):
                self.remove_column(curr_col)
            self.reset_column_widths()
            self.tile_columns()

    def move_window_right(self, curr_col, curr_win):
        # print('move right requested on layout') #__debug__

        # assume valid self.curr_col_index after this
        if not(self.sync_curr_column(curr_col)):
            # print('failed to sync current column')  #__debug__
            return

        curr_col = self.columns[self.curr_col_index]
        if(self.curr_col_index == len(self.columns)-1):
            # create a new column since we're currently at the rightmost column
            self.columns.append(Column(self, -1))
        self.curr_col_index += 1

        new_col = self.columns[self.curr_col_index]
        if(new_col != curr_col):
            curr_col.remove_window(curr_win)
            new_col.add_window(curr_win)

            if not(curr_col.has_windows()):
                self.remove_column(curr_col)
            self.reset_column_widths()
            self.tile_columns()

    def tile_window(self, window):
        if(window.must_float or not window.floating):
            return

        curr_col = window.container
        if not(self.sync_curr_column(curr_col)):
            return
        if(self.curr_col_index != 0):
            logging.error('Found floating window in Column')
            return

        self.remove_window(window)
        window.floating = False
        window.undecorate()
        self.add_window(window)
        self.tile_columns()

    def float_window(self, window):
        if(window.floating):
            return

        curr_col = window.container
        if not(self.sync_curr_column(curr_col)):
            return
        if(self.curr_col_index == 0):
            logging.error('Found tiled window in FloatingWindows')
            return

        self.remove_window(window)
        window.floating = True
        window.decorate()
        self.add_window(window)
        self.tile_columns()
        window.update()
        window.show()
        

    def decorate_all_tiled_windows(self):
        '''
        put title bar back onto all the windows under the layout
        usually called when exiting the program
        '''
        for col in self.columns:
            for window in col.windows:
                window.decorate()
                window.update()
                window.show()

