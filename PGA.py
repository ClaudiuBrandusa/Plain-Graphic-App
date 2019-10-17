# ======================================================|Imports|======================================================

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import PIL
from PIL import ImageGrab
import os
import json
import time

# ======================================================|Globals|======================================================

HEIGHT = 600
WIDTH = 1000

# =====================================================|Functions|=====================================================


# auxiliary functions
def get_last_character(string, character=None):
    last_character = 0
    if character is not None:
        for i in range(len(string)):
            if string[i] == character:
                last_character = i
    else:
        for i in range(len(string)):
            if string[i] != ' ':
                last_character = i
    return last_character


def get_name(string):
    return string[get_last_character(string, '/')+1:]


def has_extension(name):
    a = get_last_character(name, '.')
    if a == 0:
        return False
    else:
        return True


def get_extension(name):
    return name[get_last_character(name, '.'):]


def remove_extension(name):
    if has_extension(name):
        return name[:get_last_character(name, '.')-1]
    else:
        return name


def get_distance(a, b):
    return ((b.x-a.x)**2+(b.y-a.y)**2)**(1/2)


# ======================================================|Classes|======================================================

class Timer:
    def __init__(self, wait_time):
        self.wait_time = wait_time
        self.next_time = time.time() + self.wait_time

    def check(self):
        if time.time() > self.next_time:
            self.set_next_time()
            return True

    def set_next_time(self):
        self.next_time = time.time() + self.wait_time

    def turn_on(self):
        self.button.config(relief='sunken')
        self.status = True
        self.start()

    def turn_off(self):
        self.button.config(relief='raised')
        self.status = False
        self.stop()

    def __repr__(self):
        self.name


class SelectedObject:
    def __init__(self, master, obj=None):
        self.master = master
        self.object = obj
        self.point = None  # the primary point
        self.points = []  # the secondary points

    def get_obj(self):
        return self.object

    def get_point(self):
        return self.point

    def is_selected(self):
        if self.object is None:
            return False
        else:
            return True

    def clear_points(self):
        for point in self.points:
            point.deselect()
        self.points = []

    def select_point(self, point, clear=True):
        if not isinstance(point, Point):  # then its an event object
            point = self.master.get_point_by_coords(point)
        if clear:
            self.clear_points()
            self.deselect_point()
        point.select()
        self.point = point

    def secondary_point(self, point):
        if self.point is not None:
            if point in self.points:  # if its a secondary point
                self.points.remove(point)
            self.points.append(self.point)
            self.point.set_secondary()
        self.select_point(point, False)

    def select_obj(self, obj):
        if not self.is_selected():
            self.object = obj
        else:
            self.deselect_obj()
            self.object = obj

    def deselect_obj(self):
        #self.object.deselect()
        self.object = None

    def deselect_point(self):
        if self.point is not None:
            self.point.deselect()
            self.point = None

    def get_type(self):
        if isinstance(self.object, Point):
            return 0
        elif isinstance(self.object, Line):
            return 1
        elif isinstance(self.object, Rectangle):
            return 2
        elif isinstance(self.object, Polygon):
            return 3


class Dialog:
    def __init__(self, master, name, index, width=200, height=100, text=None):
        self.master = master
        self.name = name
        self.status = False
        self.hidden = False
        self.index = index
        self.width = width
        self.height = height
        self.text = text
        self.frame = tk.Frame(master.root, bg='gray', highlightbackground='white', highlightcolor='white',
                              highlightthickness=1)
        self.title = tk.Label(self.frame, text=self.name)
        self.master.dialogs.append(self)
        self.buttons = []

    def add_button(self, btn):
        self.buttons.append(btn)

    def show_dialog(self):
        if self.status:  # if its already shown
            self.frame.lift()
        else:
            self.status = True
            self.frame.place(x=self.master.width//2-(self.width//2-50), y=self.master.height//2-self.height//2,
                             width=self.width, height=self.height)
            self.title.pack()

    def resume_dialog(self):
        self.show_dialog()
        self.hidden = False

    def end_dialog(self):
        self.status = False
        self.hidden = True
        self.frame.place_forget()

    def delete_dialog(self):
        self.master.dialogs.remove(self)
        self.frame.destroy()

    def get_status(self):
        return self.status

    def __repr__(self):
        return self.index

t = 0


class Point:
    def __init__(self, x_coord, y_coord, master):
        self.x = x_coord
        self.y = y_coord
        self.draw = None  # canvas.create_oval
        self.isSelected = False
        self.isSecondary = False
        self.localWidth = master.get_current_width()
        self.wasErased = False
        self.drawn = False
        self.master = master
        self.id = master.get_id()
        global t
        # print(t)  this will just print the instance number of the point
        t+=1

        master.points.append(self)

    def get_proper_width(self):
        if self.localWidth < 8:
            return 4
        elif self.localWidth < 10:
            return 5
        else:
            return 6

    def draw_point(self, color='#ffffff'):
        if not self.drawn:
            w = self.get_proper_width()
            x1, y1 = (self.x - w), (self.y - w)
            x2, y2 = (self.x + w), (self.y + w)
            if color == '#ffffff':  # this means that the color parameter wasn't chose
                if self.isSelected:
                    self.draw = self.master.canvas.create_oval(x1, y1, x2, y2, fill='red')
                elif self.isSecondary:
                    self.draw = self.master.canvas.create_oval(x1, y1, x2, y2, fill='orange')
                else:
                    self.draw = self.master.canvas.create_oval(x1, y1, x2, y2, fill='white')
            else:
                self.draw = self.master.canvas.create_oval(x1, y1, x2, y2, fill=color)
            self.drawn = True

    def update_position(self, x_coord, y_coord):
        self.x = x_coord
        self.y = y_coord

    def update_obj(self, coordinates=None):
        if coordinates is not None:
            self.update_position(coordinates.x, coordinates.y)
        if self.master.isShowingPoints:
            self.update('white')  # change color

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_pos(self):
        return self.get_x(), self.get_y()

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def hide_point(self):
        if self.draw is not None:
            self.master.canvas.delete(self.draw)
            self.draw = None
        self.drawn = False

    def update(self, color="white"):
        self.hide_point()
        self.draw_point(color)

    def set_secondary(self):
        self.isSelected = False
        self.isSecondary = True
        self.update('orange')

    def unset_secondary(self):
        if self.isSecondary:
            self.isSecondary = False
            self.update()

    def select(self, point=None):
        if point is None:
            self.update("red")
            self.isSelected = True
        else:
            if self.clicked_on_point(point):
                if self.isSelected:
                    self.deselect()
                else:
                    self.unset_secondary()
                    self.update("red")
                    self.isSelected = True
                    self.master.selection.deselect_point()
                    self.master.selection.select_point(self)

    def deselect(self):
        if self.isSecondary:
            self.unset_secondary()
        else:
            self.update("white")
            self.isSelected = False

    def clicked_on_point(self, point):
        if get_distance(self, point) < self.get_proper_width():
            return True
        else:
            return False

    def erase(self):
        self.wasErased = True
        self.undo()

    def delete(self):
        self.master.undo_points.append(self)
        self.master.points.remove(self)
        self.hide_point()

    def full_delete(self):
        self.hide_point()
        self.master.points.remove(self)

    def undo(self):
        self.hide_point()
        self.master.undo_points.append(self)
        self.master.points.remove(self)

    def redo(self):
        self.master.points.append(self)
        self.master.undo_points.remove(self)
        if self.master.isShowingPoints:
            self.draw_point()

    def get_data(self):
        return self.x, self.y, self.isSelected, self.localWidth, self.wasErased, self.drawn, self.id

    def set_data(self, data):
        self.x = data[0]
        self.y = data[1]
        self.isSelected = data[2]
        self.localWidth = data[3]
        self.wasErased = data[4]
        self.drawn = data[5]
        self.id = data[6]
        self.master.last_id -= 1  # because we had incremented it by creating the class


    def __repr__(self):
        return f"{self.x},{self.y}"


class Line:
    def __init__(self, point_a, point_b, master, loading=False):
        self.pointA = point_a
        self.pointB = point_b
        self.width = master.get_current_width()
        self.line = None
        master.history.append(self)
        master.lines.append(self)
        if not loading:
            master.clear_undo_list()  # we cant redo if we are already adding new things
        self.master = master
        self.id = master.get_id()

    def update_line(self):
        self.master.canvas.delete(self.line)
        self.draw()

    def end_update(self):
        if self.master.isShowingPoints:
            self.update_points()

    def draw(self):
        self.line = self.master.canvas.create_line(self.pointA.x, self.pointA.y, self.pointB.x, self.pointB.y,
                                                   width=self.width)

    def delete(self):
        self.master.canvas.delete(self.line)
        self.master.lines.remove(self)
        self.master.history.remove(self)
        self.delete_points

    def full_delete(self):
        if self.master.selection.get_point() != self.pointA:
            self.pointA.full_delete()
        self.pointB.full_delete()
        self.master.canvas.delete(self.line)
        self.master.lines.remove(self)
        self.master.history.remove(self)

    def set_width(self, width):  # I do not use this method, for now
        self.width = width

    def get_width(self):  # I do not use this method, for now
        return self.width

    def draw_points(self):
        self.pointA.draw_point()
        self.pointB.draw_point()

    def hide_points(self):
        self.pointA.hide_point()
        self.pointB.hide_point()

    def delete_points(self):
        self.pointA.delete()
        self.pointB.delete()

    def update_points(self):
        self.pointA.update()
        self.pointB.update()

    def get_length(self):
        return get_distance(self.pointA, self.pointB)

    def on_click(self, event):  # under construction
        item = self.canvas.find_withtag(tk.current)
        self.canvas.delete(item)

    def undo(self):
        self.pointA.undo()
        self.pointB.undo()
        self.master.undo_list.append(self)
        self.master.canvas.delete(self.line)
        self.master.lines.remove(self)
        self.master.history.remove(self)

    def redo(self):
        self.master.history.append(self)
        self.master.lines.append(self)
        self.master.undo_list.remove(self)
        self.draw()
        self.pointA.redo()
        self.pointB.redo()

    def get_data(self):
        return self.pointA.get_data()[-1], self.pointB.get_data()[-1], self.width, self.id

    def set_data(self, data):
        self.width = data[2]
        self.master.last_id -= 1  # because we had incremented it by creating the class


class Polygon:
    def __init__(self, points, master):
        self.points = points
        self.lines = []
        self.drawn = False
        self.polygon = None
        self.master = master
        self.width = master.CurrentWidth
        self.id = master.get_id()
        self.master.history.append(self)
        self.draw()

    def draw(self):
        if not self.drawn:
            points = []
            for i in self.points:
                points.append(i.x)
                points.append(i.y)
            self.polygon = self.master.canvas.create_polygon(points, fill='', outline='black')
            self.drawn = True
            self.draw_points()

    def draw_points(self):
        self.hide_points()
        if self.master.isShowingPoints:
            for i in self.points:
                i.draw_point()

    def hide_points(self):
        for i in self.points:
            i.hide_point()

    def get_lines(self):
        pass


class Rectangle:
    def __init__(self, point_a, point_d, master, point_b=None, point_c=None, loading=False):
        self.pointA = point_a
        if point_b is not None and point_c is not None:
            self.pointB = point_b
            self.pointC = point_c
        else:
            self.pointB = Point(point_d.x, point_a.y, master)
            self.pointC = Point(point_a.x, point_d.y, master)
        self.pointD = point_d
        self.width = master.get_current_width()
        self.rectangle = None
        self.lines = []
        self.master = master
        self.id = master.get_id()
        self.master.history.append(self)
        self.master.rectangles.append(self)
        if not loading:
            self.master.clear_undo_list()

    def update_rectangle(self, p):
        self.master.canvas.delete(self.rectangle)
        self.resettle_points(p)
        self.draw()

    def end_update(self):
        if self.master.isShowingPoints:
            self.update_points()

    def resettle_points(self, coordinates):
        self.pointA.hide_point()
        self.pointD.update_obj(coordinates)
        self.pointD.hide_point()
        self.pointB.set_x(coordinates.x)
        self.pointB.hide_point()
        self.pointC.set_y(coordinates.y)
        self.pointC.hide_point()

    def draw(self):
        self.rectangle = self.master.canvas.create_rectangle(self.pointA.x, self.pointA.y, self.pointD.x, self.pointD.y,
                                            width=self.width)
        if self.master.isShowingPoints:
            self.draw_points()

    def delete(self):
        self.master.canvas.delete(self.rectangle)
        self.master.rectangles.remove(self)
        self.master.history.remove(self)
        self.hide_points()
        self.delete_points()

    def full_delete(self):
        self.pointA.full_delete()
        self.pointB.full_delete()
        self.pointC.full_delete()
        self.pointD.full_delete()
        self.master.canvas.delete(self.rectangle)
        self.master.rectangles.remove(self)
        self.master.history.remove(self)

    def convert(self):
        self.pointA = None
        self.pointB = None
        self.pointC = None
        self.pointD = None
        self.master.canvas.delete(self.rectangle)
        self.master.rectangles.remove(self)
        self.master.history.remove(self)

    def set_width(self, width):  # im not using this method for now
        self.width = width

    def get_width(self):  # im not using this method for now
        return self.width

    def set_lines(self):  # im not using this method for now
        pass

    def get_lines(self):  # im not using this method for now
        pass

    def get_diagonal(self):
        return get_distance(self.pointA, self.pointD)

    def draw_points(self):
        self.pointA.draw_point()
        self.pointB.draw_point()
        self.pointC.draw_point()
        self.pointD.draw_point()

    def hide_points(self):
        self.pointA.hide_point()
        self.pointB.hide_point()
        self.pointC.hide_point()
        self.pointD.hide_point()

    def update_points(self):
        #self.pointA.update()
        self.pointB.update()
        self.pointC.update()
        self.pointD.update()

    def delete_points(self):
        self.pointA.delete()
        self.pointB.delete()
        self.pointC.delete()
        self.pointD.delete()

    def undo(self):
        self.pointA.undo()
        self.pointB.undo()
        self.pointC.undo()
        self.pointD.undo()
        self.master.undo_list.append(self)
        self.master.history.remove(self)
        self.master.canvas.delete(self.rectangle)
        self.master.rectangles.remove(self)

    def redo(self):
        self.master.history.append(self)
        self.master.rectangles.append(self)
        self.master.undo_list.remove(self)
        self.draw()
        self.pointA.redo()
        self.pointB.redo()
        self.pointC.redo()
        self.pointD.redo()

    def to_polygon(self):
        Polygon([self.pointA, self.pointB, self.pointD, self.pointC]
                , self.master)
        self.convert()

    def get_data(self):
        return self.pointA.get_data()[-1], self.pointB.get_data()[-1], self.pointC.get_data()[-1], \
               self.pointD.get_data()[-1], self.width, self.id

    def set_data(self, data):
        self.width = data[-2]
        self.id = data[-1]
        self.master.last_id -= 1  # because we had incremented it by creating the class


class Save:
    pass


class App:
    def __init__(self, width, height):
        # variables
        self.CurrentWidth = 3  # this is the width that you can select from tools
        self.isFree = True  # True means that is not using any tool
        self.saved_process = False
        self.isShowingPoints = False
        self.HiddenPoints = False
        self.is_drawing = False
        self.width = width
        self.height = height
        self.last_id = 0
        self.selection = SelectedObject(self)

        # lists
        self.dialogs = []
        self.tools = [False, False, False]  # 0 eraser, 1 line, 2 rectangle
        self.points = []  # here we will store the points
        self.lines = []  # here we will store the lines
        self.rectangles = []  # here we will store the rectangles
        self.history = []  # all the shapes created will be stored here
        self.undo_list = []  # all the undoes will be stored here
        self.undo_points = []  # we store here all the undo-ed points

        # tkinter
        self.root = tk.Tk()
        self.root.title("Plain Graphic App")
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        # menu part
        self.menu = tk.Frame(self.root, bg='red')
        self.menu.place(relx=0, rely=0, relwidth=.1, relheight=1)

        # environment part
        self.environment = tk.Frame(self.root, bg='blue')
        self.environment.place(relx=.1, rely=0, relwidth=.9, relheight=1)
        self.canvas = tk.Canvas(self.environment, height=height, width=width)
        self.canvas.pack()
        self.set_binds()

        # buttons

        self.new_btn = None
        self.save_btn = None
        self.load_btn = None
        self.settings_btn = None
        self.help_btn = None
        self.quit_btn = None
        self.tools_label = None
        self.eraser_btn = None
        self.draw_line_btn = None
        self.draw_rectangle_btn = None
        self.styles = None
        self.show_points_btn = None
        self.width_label = None
        self.width_entry = None
        self.set_buttons()

        self.root.mainloop()

    def set_buttons(self):
        self.new_btn = tk.Button(self.menu, anchor='n', text='New file', bg='gray', fg='white',
                                 command=lambda: self.new_file())
        self.new_btn.pack(fill='x')
        self.save_btn = tk.Button(self.menu, anchor='n', text='Save', bg='gray', fg='white',
                                  command=lambda: self.get_to_save())
        self.save_btn.pack(fill='x')
        self.load_btn = tk.Button(self.menu, anchor='n', text='Load', bg='gray', fg='white',
                                  command=lambda: self.get_to_load())
        self.load_btn.pack(fill='x')
        self.settings_btn = tk.Button(self.menu, anchor='n', text='Settings', bg='gray', fg='white',
                                      command=lambda: self.get_to_settings())
        self.settings_btn.pack(fill='x')
        self.help_btn = tk.Button(self.menu, anchor='n', text='Help', bg='gray', fg='white',
                                  command=lambda: self.get_help())
        self.help_btn.pack(fill='x')
        self.quit_btn = tk.Button(self.menu, anchor='n', text='Quit', bg='gray', fg='white',
                                  command=lambda: self.quit_app())
        self.quit_btn.pack(fill='x')

        self.set_tools()

        self.styles = tk.Label(self.menu, anchor='n', text='Styles', bg='gray', fg='white')
        self.styles.pack(fill='x')
        self.show_points_btn = tk.Button(self.menu, anchor='n', text='Show Points', bg='gray', fg='white',
                                         command=lambda: self.show_points())
        self.show_points_btn.pack(fill='x')
        self.width_label = tk.Label(self.menu, anchor='nw', text='Width:', bg='gray', fg='white')
        self.width_label.pack(fill='x')
        self.width_entry = tk.Entry(self.width_label, bg='gray', fg='white', width=7)
        self.width_entry.pack(side='right')
        self.set_width_entry()

    def set_tools(self):
        self.tools_label = tk.Label(self.menu, anchor='n', text='Tools', bg='gray', fg='white')
        self.tools_label.pack(fill='x')
        self.eraser_btn = tk.Button(self.menu, anchor='n', text='Eraser', bg='gray', fg='white',
                                    command=lambda: self.start_erase_tool())
        self.eraser_btn.pack(fill='x')
        self.draw_line_btn = tk.Button(self.menu, anchor='n', text='Draw line', bg='gray', fg='white',
                                       command=lambda: self.start_line_tool())
        self.draw_line_btn.pack(fill='x')
        self.draw_rectangle_btn = tk.Button(self.menu, anchor='n', text='Rectangle', bg='gray', fg='white',
                                            command=lambda: self.start_rectangle_tool())
        self.draw_rectangle_btn.pack(fill='x')

    def get_id(self):
        self.last_id += 1
        return self.last_id - 1

    def set_binds(self):
        self.canvas.focus_set()
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<Shift-Button-1>", self.shift_left_click)
        self.canvas.bind("<Control-z>", self.undo)
        self.canvas.bind("<Control-y>", self.redo)
        self.canvas.bind("<B1-Motion>", self.left_click_motion)
        self.canvas.bind("<ButtonRelease-1>", self.left_click_release)
        # hotkeys
        self.canvas.bind("<r>", self.start_rectangle_tool)
        self.canvas.bind("<l>", self.start_line_tool)
        self.canvas.bind("<e>", self.start_erase_tool)

    def block_buttons(self):
        self.new_btn.configure(command='')
        self.save_btn.configure(command='')
        self.load_btn.configure(command='')
        self.settings_btn.configure(command='')
        self.help_btn.configure(command='')
        self.quit_btn.configure(command='')
        self.eraser_btn.configure(command='')
        self.draw_line_btn.configure(command='')
        self.draw_rectangle_btn.configure(command='')
        self.show_points_btn.configure(command='')

    def unblock_buttons(self):
        self.new_btn.configure(command=lambda: self.new_file())
        self.save_btn.configure(command=lambda: self.get_to_save())
        self.load_btn.configure(command=lambda: self.get_to_load())
        self.settings_btn.configure(command=lambda: self.get_to_settings())
        self.help_btn.configure(command=lambda: self.get_help())
        self.quit_btn.configure(command=lambda: self.quit_app())
        self.eraser_btn.configure(command=lambda: self.start_erase_tool())
        self.draw_line_btn.configure(command=lambda: self.start_line_tool())
        self.draw_rectangle_btn.configure(command=lambda: self.start_rectangle_tool())
        self.show_points_btn.configure(command=lambda: self.show_points())

    def show_points(self):
        if not self.isShowingPoints:
            self.isShowingPoints = True
            self.HiddenPoints = False
            for i in self.history:
                i.draw_points()
                self.show_points_btn.config(relief='sunken')
        else:
            self.isShowingPoints = False
            self.show_points_btn.config(relief='raised')
            for i in self.history:
                i.hide_points()

    def hide_points(self):
        self.HiddenPoints = True
        self.show_points()

    # for saving
    def get_data(self):
        points = []
        for point in self.points:
            points.append(point.get_data())
        lines = []
        for line in self.lines:
            lines.append(line.get_data())
        rectangles = []
        for rectangular in self.rectangles:
            rectangles.append(rectangular.get_data())
        history = []
        for element in self.history:
            history.append(element.get_data()[-1])  # id
        undo_list = []
        for element in self.undo_list:
            undo_list.append(element.get_data())  # id
        undo_points = []
        for point in self.undo_points:
            undo_points.append(point.get_data())  # id
        selected_object = None
        if self.selection.is_selected():
            selected_object = self.selection.get_obj().get_data()[-1]
        return self.CurrentWidth, self.isFree, self.isShowingPoints, points, lines, rectangles, history, undo_list,\
               undo_points, selected_object

    # for loading
    def set_data(self, data):
        self.CurrentWidth = data[0]
        self.isFree = data[1]
        self.isShowingPoints = data[2]
        self.points = data[3]
        self.lines = data[4]
        self.rectangles = data[5]
        self.history = data[6]
        self.undo_list = data[7]
        self.undo_points = data[8]
        self.selection.select_obj(self.get_object(data[9]))

    # events
    # left click
    def left_click(self, event):
        if self.tools[0]:  # erase tool
            self.erase(event)
        elif self.tools[1]:  # line tool
            self.begin_line(event)
            self.update_line(event)
        elif self.tools[2]:  # rectangular tool
            self.clear_selection()
            self.begin_rectangle(event)
        else:
            if self.isShowingPoints:
                point = self.get_point_by_coords(event)
                if point is not None:
                    self.selection.select_point(point)

    def left_click_motion(self, event):
        if self.selection.is_selected():
            if self.tools[1]:
                self.update_line(event)
            elif self.tools[2]:
                self.update_rectangle(event)

    def left_click_release(self, event):
        if self.tools[1]:
            self.end_line()
        elif self.tools[2]:
            self.end_rectangle()

    # shift left click
    def shift_left_click(self, event):
        if self.isShowingPoints:
            if self.check_tool_status():  # if its free
                point = self.get_point_by_coords(event)
                if point is not None:
                    self.selection.secondary_point(point)
    # tools

    def reset_tools(self):
        for i in range(len(self.tools)):
            self.tools[i] = False
        self.isFree = True

    def check_which_tool_is_active(self):  # 0 eraser, 1 line, 2 rectangle
        for i in range(len(self.tools)):
            if self.tools[i]:
                return i
        return -1  # means that we have no tool active.

    def cancel_tool(self):
        a = self.check_which_tool_is_active()
        if a != -1:
            self.canvas.config(cursor='arrow')
            if a == 0:
                self.stop_erase_tool()
            elif a == 1:
                self.stop_line_tool()
            elif a == 2:
                self.stop_rectangle_tool()

    def set_tool_status(self):
        self.canvas.config(cursor='arrow')
        self.root.config(cursor='arrow')
        for i in self.tools:
            if i:
                self.isFree = False
                return 0  # this means that we got what we wanted so we can return anything to end the function
        self.isFree = True


    def check_tool_status(self):
        return self.isFree

    # erase part
    def start_erase_tool(self, event=None):
        if self.tools[0]:
            self.stop_erase_tool()
        else:
            if not self.check_tool_status():  # if is not using any tool
                self.cancel_tool()
            self.tools[0] = True
            self.eraser_btn.config(relief='sunken')
            self.set_tool_status()
            self.canvas.config(cursor='dotbox')

    def stop_erase_tool(self):
        if self.tools[0]:
            self.set_tool_status()
        self.tools[0] = False
        self.eraser_btn.config(relief='raised')

    def erase(self, element):
        canvas = element.widget
        x = canvas.canvasx(element.x)
        y = canvas.canvasy(element.y)
        area = canvas.find_overlapping(x, y, x+2, y+2)
        if len(area) > 0:
            for i in self.lines:
                if i.line == area[0]:
                    i.full_delete()
                    return 0
            for i in self.rectangles:
                if i.rectangle == area[0]:
                    i.full_delete()
                    return 0

    def undo(self, event):  # i have to add an undo_points_list
        if len(self.history) > 0:
            self.history[-1].undo()

    def redo(self, event):
        if len(self.undo_list) > 0:
            self.undo_list[-1].redo()

    def clear_undo_list(self):
        self.undo_list = []

    # drawings

    def draw_all(self):
        self.draw_rectangles()
        self.draw_lines()

    def draw_rectangles(self):
        for rectangle in self.rectangles:
            rectangle.draw()

    def draw_lines(self):
        for line in self.lines:
            line.draw()

    def get_object(self, item):
        for i in self.history:
            if i.id == item:
                return i

    def get_element(self, item):
        if len(item) == 4:  # line
            return Line(self.get_undo_point(item[0]), self.get_undo_point(item[1]), self, True)
        else:
            return Rectangle(self.get_undo_point(item[0]), self.get_undo_point(item[3]), self,
                             self.get_undo_point(item[1]), self.get_undo_point(item[2]), True)

    # selection part
    # to be deleted
    def select_point(self, element):
        if self.isShowingPoints:
            for point in self.points:
                point.select(element)

    def clear_selection(self):
        if self.selection.is_selected():  # we use this to prevent something being there
            self.selection.deselect_obj()

    # point part

    def get_point_by_coords(self, coords):
        for point in self.points:
            if point.clicked_on_point(coords):
                return point

    def get_point(self, index):
        for i in self.points:
            if i.id == index:
                return i
        return -1

    def get_undo_point(self, index):
        for point in self.undo_points:
            if point.id == index:
                return point
        return -1

    # line part
    def begin_line(self, start_point):
        point = self.selection.get_point()
        if point is not None:
            self.selection.select_obj(Line(self.selection.get_point(), Point(start_point.x + 1, start_point.y + 1, self)
                                                                                                                , self))
        else:
            self.selection.select_obj(Line(Point(start_point.x, start_point.y, self), Point(start_point.x + 1,
                                                                                        start_point.y + 1, self), self))

    def update_line(self, event):
        self.points[-1].update_position(event.x, event.y)
        self.selection.get_obj().update_line()
        self.points[-1].update_obj()
        self.points[-2].update_obj()

    def end_line(self, event=None):
        if self.selection.is_selected():
            if self.selection.get_obj().get_length() < 10:
                self.selection.get_obj().full_delete()
            else:
                self.selection.get_obj().end_update()
            self.selection.deselect_obj()
            self.tools[1] = False
            self.set_tool_status()
            self.draw_line_btn.config(relief='raised', command=self.start_line_tool)

    def start_line_tool(self, event=None):
        if not self.check_tool_status():
            self.cancel_tool()
        self.tools[1] = True
        self.draw_line_btn.config(relief='sunken', command=lambda: self.stop_line_tool())
        self.set_tool_status()
        self.root.config(cursor='plus')
        self.canvas.config(cursor='plus')

    def stop_line_tool(self):
        self.tools[1] = False
        self.draw_line_btn.config(relief='raised', command=lambda: self.start_line_tool())
        self.set_tool_status()

    def clear_lines(self):
        while len(self.lines) > 0:
            self.lines[0].full_delete()
        self.lines.clear()

    # rectangular part
    def begin_rectangle(self, start_point):
        Point(start_point.x, start_point.y, self)
        self.selection.select_obj(Rectangle(self.points[-1], Point(start_point.x + 5, start_point.y + 5, self), self))

    def update_rectangle(self, event):
        self.selection.get_obj().update_rectangle(event)

    def end_rectangle(self):
        if self.selection.is_selected():
            if self.selection.get_obj().get_diagonal() < 20:
                self.selection.get_obj().full_delete()
            else:
                self.selection.get_obj().to_polygon()
            self.tools[2] = False
            self.set_tool_status()
            self.selection.deselect_obj()
            self.draw_rectangle_btn.config(relief='raised', command=lambda: self.start_rectangle_tool())

    def start_rectangle_tool(self, event=None):
        if not self.check_tool_status():
            self.cancel_tool()
        if not self.tools[2]:
            self.tools[2] = True
            self.draw_rectangle_btn.config(relief='sunken', command=lambda: self.stop_rectangle_tool())
        self.root.config(cursor='cross')
        self.canvas.config(cursor='cross')

    def stop_rectangle_tool(self):
        self.tools[2] = False
        self.draw_rectangle_btn.config(relief='raised', command=lambda: self.start_rectangle_tool())
        self.set_tool_status()

    def clear_rectangles(self):
        while len(self.rectangles) > 0:
            self.rectangles[0].full_delete()
        self.rectangles.clear()

    def clear_points(self):
        while len(self.points) > 0:
            self.points[0].full_delete()
        self.points.clear()

    def clear_objects(self):
        self.clear_rectangles()
        self.clear_lines()
        self.clear_points()

    # dialogs
    def new_file(self):
        if 10 not in self.dialogs:
            Dialog(self, "New File", 10, 200, 100)
            self.dialogs[-1].show_dialog()
            back_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Back', bg='gray', fg='white',
                                 command=lambda: self.dialogs[-1].delete_dialog())
            back_btn.pack(side='right', padx=(20, 20))
            new_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='New', bg='gray', fg='white',
                                command=lambda: self.reset())
            new_btn.pack(side='left', padx=(20, 20))
        else:
            index = self.get_dialog(10)
            self.dialogs[index].lift()
        if not self.saved_process:
            messagebox.showwarning('Warning', 'You haven\'t saved!')

    def get_to_save(self):
        if 11 not in self.dialogs:
            Dialog(self, "Save", 11, 200, 100)
            self.dialogs[-1].show_dialog()
            back_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Back', bg='gray', fg='white',
                                 command=lambda: self.dialogs[-1].delete_dialog())
            back_btn.pack(side='right', padx=(20, 20))
            save_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Save', bg='gray', fg='white',
                                command=lambda: self.save_all())
            save_btn.pack(side='left', padx=(20, 20))
        else:
            index = self.get_dialog(11)
            self.dialogs[index].lift()

    def get_to_load(self):
        if 12 not in self.dialogs:
            Dialog(self, "Load", 12, 200, 100)
            self.dialogs[-1].show_dialog()
            back_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Back', bg='gray', fg='white',
                                 command=lambda: self.dialogs[-1].delete_dialog())
            back_btn.pack(side='right', padx=(20, 20))
            load_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Load', bg='gray', fg='white',
                                 command=lambda: self.load_file())
            load_btn.pack(side='left', padx=(20, 20))
        else:
            index = self.get_dialog(12)
            self.dialogs[index].lift()

    def get_to_settings(self):
        if 13 not in self.dialogs:
            Dialog(self, "Settings", 13, 200, 100)
            self.dialogs[-1].show_dialog()
            back_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Back', bg='gray', fg='white',
                                 command=lambda: self.dialogs[-1].delete_dialog())
            back_btn.pack(side='right', padx=(20, 20))
            set_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Set', bg='gray', fg='white',
                                 command='')
            set_btn.pack(side='left', padx=(20, 20))
        else:
            index = self.get_dialog(13)
            self.dialogs[index].lift()

    def get_help(self):
        if 14 not in self.dialogs:
            Dialog(self, "Help", 14, 200, 160)
            self.dialogs[-1].show_dialog()
            content = tk.Label(self.dialogs[-1].frame, text='ctrl-z undo\nctrl-y redo\nr rectangle tool\nl line tool\n'
                                                            'e eraser')
            content.pack(side='top', pady=(5, 5))
            back_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Back', bg='gray', fg='white',
                                 command=lambda: self.dialogs[-1].delete_dialog())
            back_btn.pack(side='bottom', pady=(5, 15))
        else:
            index = self.get_dialog(14)
            self.dialogs[index].lift()

    def quit_app(self):
        if 15 not in self.dialogs:
            Dialog(self, "Quit", 15, 200, 100)
            self.dialogs[-1].show_dialog()
            quit_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Quit', bg='gray', fg='white',
                                 command=lambda: self.root.quit())
            quit_btn.pack(side='left', padx=(20, 20))
            back_btn = tk.Button(self.dialogs[-1].frame, anchor='s', text='Back', bg='gray', fg='white',
                                 command=lambda: self.dialogs[-1].delete_dialog())
            back_btn.pack(side='right', padx=(20, 20))

        else:
            index = self.get_dialog(15)
            self.dialogs[index].lift()

    def clear_app(self):
        self.hide_dialogs()
        self.clear_objects()
        self.cancel_tool()

    def reset(self):
        self.clear_app()
        # reset the canvas
        self.canvas.delete("all")

    def get_dialog(self, index):
        for i in self.dialogs:
            if i == index:
                return i
        return -1

    def hide_dialogs(self):
        for dialog in self.dialogs:
            dialog.end_dialog()
        if self.isShowingPoints:
            self.hide_points()

    def resume_dialogs(self):
        for i in range(len(self.dialogs)):
            if self.dialogs[i]:
                self.dialogs[i].resume_dialog()
        if self.HiddenPoints:
            self.show_points()

    def show_dialog(self, index):
        if index == 0:
            self.new_file()
        elif index == 1:
            self.get_to_save()
        elif index == 2:
            self.get_to_load()
        elif index == 3:
            self.get_to_settings()
        elif index == 4:
            self.get_help()
        elif index == 5:
            self.quit_app()

    # save
    def save_project_file(self, name):
        info = self.get_data()
        data={
            'width': info[0], 'isfree': info[1], 'showpoints': info[2], 'points': info[3], 'lines': info[4],
            'rectangles': info[5], 'history': info[6], 'undolist': info[7], 'undopoints': info[8], 'selected': info[9]
            }
        with open(name, 'w') as f:
            json.dump(data, f, indent=1)
            f.close()

    def save_image(self, name):
        x = self.canvas.winfo_rootx() + self.canvas.winfo_x() + 2
        y = self.canvas.winfo_rooty() + self.canvas.winfo_y() + 2
        x1 = self.canvas.winfo_rootx() + self.canvas.winfo_width() - 2
        y1 = self.canvas.winfo_rooty() + self.canvas.winfo_height() - 2
        PIL.ImageGrab.grab().crop((x, y, x1, y1)).save(name)

    def save_all(self):

        self.hide_dialogs()
        file = filedialog.asksaveasfilename(defaultextension='.pga',
                                            filetypes=[('PGA file', '*.pga'), ('JPG file', '*.jpg'),
                                                       ('PNG file', '*.png')], initialdir=os.getcwd())
        if file:
            name, ext = get_name(os.path.splitext(file)[0]), os.path.splitext(file)[1]
            if file.endswith('pga'):
                self.save_project_file(file)
            else:
                self.save_image(file)
            self.resume_dialogs()
            self.saved_process = True

    # load
    def load_file(self):
        file = filedialog.askopenfilename(filetypes=[('PGA file', '*.pga')])
        if file:
            self.reset()
            with open(file, 'r') as f:
                data = json.load(f)
                self.CurrentWidth = data['width']
                self.isFree = data['isfree']
                if data['showpoints']:
                    self.show_points()
                self.load_points(data['points'])
                self.load_lines(data['lines'])
                self.load_rectangles(data['rectangles'])
                self.load_undo_points(data['undopoints'])
                self.load_undo_list(data['undolist'])
            self.draw_all()

    def load_points(self, points):
        for point in points:
            p = Point(point[0], point[1], self)
            p.set_data(point)

    def load_lines(self, lines):
        for line in lines:
            l = Line(self.get_point(line[0]), self.get_point(line[1]), self)
            l.set_data(line)

    def load_rectangles(self, rectangles):
        for rectangle in rectangles:
            r = Rectangle(self.get_point(rectangle[0]), self.get_point(rectangle[3]), self, self.get_point(rectangle[1])
                          , self.get_point(rectangle[2]))
            r.set_data(rectangle)

    def load_undo_list(self, undolist):
        for item in undolist:
            i = self.get_element(item)
            i.set_data(item)
            if i in self.lines:
                self.lines.remove(i)
            else:
                self.rectangles.remove(i)
            self.history.remove(i)
            self.undo_list.append(i)

    def load_undo_points(self, undopoints):
        for point in undopoints:
            p = Point(point[0], point[1], self)
            p.set_data(point)
            self.points.remove(p)
            self.undo_points.append(p)

    # settings
    def set_settings(self):
        pass

    # width
    def bind_width(self, event):
        self.width_entry.bind("<Return>", self.set_width)
        self.canvas.unbind("<w>")
        self.width_entry.focus_set()
        self.block_buttons()

    def unbind_width(self, event):
        self.width_entry.unbind("<Return>")
        self.unblock_buttons()

    def set_width_entry(self):
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, self.CurrentWidth)
        self.width_entry.bind("<FocusIn>", self.bind_width)
        self.width_entry.bind("<FocusOut>", self.unbind_width)
        self.canvas.bind("<w>", self.bind_width)

    def set_width(self, event):
        w = self.width_entry.get()
        #print(w)
        try:
            int(w)
        except:
            self.set_width_entry()
        else:
            w = int(w)
            if 0 < w < 11:
                self.CurrentWidth = w
                self.canvas.focus_set()
                self.set_width_entry()

    # get
    def get_current_width(self):
        return self.CurrentWidth


app = App(WIDTH, HEIGHT)
