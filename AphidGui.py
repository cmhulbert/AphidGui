#!/usr/bin/env python

'''
Created on Aug 5, 2015

@author: ch635
'''

import csv
from Tkinter import Tk, W, E, Label, Button, Canvas, OptionMenu, StringVar
from ttk import Frame, Style
from ttk import Entry
import string
import tkFileDialog

class AphidGUI(Frame):
    '''
    Opens a window for visualization of the movement of Aphid data, over time, based
    on data from a csv file
    '''
    
    widget_dict = {}
    dataList = []
    csvFile = ''
    currentTime = None
    FlatList = []
    Rep = 0
    Flat = ''
    Time = 0
    ms = 0
    
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()
    
    def getfile(self):
        '''
        opens a window that allows the user to select a csv
        file
        '''
        Tk().withdraw()
        path = tkFileDialog.askopenfile('r')
        return path.name
    
    def get_headers(self,file):
        '''
        given a csv file, it will return the headers
        (first row), as a list
        '''
        with open(file, 'r') as csv:
            header_string = csv.readline()
            return header_string.split(',')

    def get_data_list(self,file):
        '''
        Given a csv file, this will return a 2d list,
        data_list, where data_list has an index for each
        header in row one. Each of these headers in turn
        is a list, which contains all the data in their
        column.
        '''
        list = []
        with open(file, 'r') as csv:
            list_of_lines = csv.readlines()
        for i in range(len(list_of_lines)):
            list.append(list_of_lines[i].split(','))
        return list
    
    def get_chess_value(self,list, letter_number_pair):
        '''
        Given an input which follows the same rules as
        naming a space on a chess board (ie, "A2") it will
        return the value that is in that Column and Row in
        the csv file which the list was made from.
        '''
        letter = letter_number_pair[0:1]
        number = letter_number_pair[1:]
        row = int(number) - 1
        col = string.ascii_uppercase[:13].find(letter.upper()) -1
        if row > len(list):
            print "Row not in range"
        return list[row][col]
    
    def get_row(self, datalist, row):
        '''
        Returns a list of data which represents a specified
        row in the csv file
        '''
        return datalist[row]
    
    def get_col(self, datalist, letter):
        '''
        Returns a list of data which represents aspecified
        column in the csv file
        '''
        col = string.ascii_uppercase[:13].find(letter.upper()) -1
        column = []
        for i in datalist:
            column.append(i[col])
        return column
    
    def sort_data_by_RepAndFlat(self, list, rep, flat):
        '''
        Returns a sublist of list, which is sorted first by
        Rep, and then by flat.
        '''
        tempList = []
        for i in list:
            if i[0] == str(rep).upper() and i[1] == str(flat):
                tempList.append(i)
        return tempList
    
    def set_csv_file(self):
        '''
        sets the csv file AphidGUI uses.
        '''
        self.csvFile = self.getfile()
        
    def set_dataList(self,event):
        '''
        Sets the data list from the csv file. Also sets the
        "Rep", "Flat", and "Time" option lists, such that
        only possible choices from the data list can be
        chosen
        '''
        self.set_csv_file()
        self.dataList = self.get_data_list(self.csvFile)
        
        repOptionList = self.get_option_list(0)
        repVar = StringVar()
        rep = apply(OptionMenu, (self,repVar) + repOptionList)
        repVar.set(repOptionList[0])
        rep.grid(row = 10, column=1, sticky= "we")
        self.widget_dict["rep"] = repVar
        
        flatOptionList = self.get_option_list(1)
        flatVar = StringVar()
        flat = apply(OptionMenu, (self,flatVar) + flatOptionList)
        flatVar.set(flatOptionList[0])
        flat.grid(row=10,column=2, sticky= "we")
        self.widget_dict["flat"] = flatVar
        
        timeOptionList = ("Hour",1,3,6,24)
        timeVar = StringVar()
        time = apply(OptionMenu, (self,timeVar) + timeOptionList)
        timeVar.set(timeOptionList[0])
        time.grid(row=10,column=3, sticky= "we")
        self.widget_dict["time"] = timeVar
        
        self.pack()
        
    def chessValue(self, letNum):
        '''
        Return the same value as get_chess_value, but
        assumes there is a data list set in AphidGUI
        '''
        return self.get_chess_value(self.dataList, letNum)
    
    def print_value(self, returnStatementToPrint):
        '''
        Used for testing, prints a function output, which
        allows for testing within the gui
        '''
        print returnStatementToPrint
    
    def print_value_event(self, event):
        '''
        Used for testing. When set to a button, the button
        can be pressed, and then a command typed in the
        terminal as a string, which will then be executed
        '''
        returnStatementToPrint = raw_input("Statement to print:")
        exec returnStatementToPrint
        
    def change_time_forward(self,event):
        '''
        Sets the time being displayed on the gui forward
        to the next time slot.
        '''
        times = ['1','3','6','24']
        time = self.widget_dict["time"]
        index = times.index(time.get())
        if index < 3:
            index+=1
        time.set(int(times[index]))
        self.draw_circles()
        
    def change_time_backward(self,event):
        '''
        Set the time being displayed on the gui backward
        to the previous time slot.
        '''
        times = ['1','3','6','24']
        time = self.widget_dict["time"]
        index = times.index(time.get())
        if index > 0:
            index-=1
        time.set(int(times[index]))
        self.draw_circles()
    
    def set_current_flat(self):
        '''
        Sets the Rep, Flat, and Time attributes for the gui
        '''
        self.Rep = self.widget_dict["rep"].get()
        self.Flat = self.widget_dict["flat"].get()
        self.Time = int(self.widget_dict["time"].get())
        flatList = self.sort_data_by_RepAndFlat(self.dataList, self.Rep, self.Flat)
        self.FlatList = flatList
    
    def get_option_list(self, column):
        '''
        Returns a list of possible option from a given
        column in the data list
        '''
        list = ()
        for i in self.dataList:
            if i[column] not in list:
                list += (i[column],)
        return list
    
    def createOval(self, size, canvas):
        '''
        creates a circle, sized relative to the number of
        aphids on that spot at that time
        '''
        if size != 0:
            ul = 35 - size*32
            br = 30 + size*32
            canvas.create_oval((ul,ul),(br,br),fill = "green")
    
    def draw_circles(self, event=None):
        '''
        Draws all the circles for the Flat.
        '''
        self.clear_canvas()
        self.set_current_flat()
        time = int(self.Time)
        timeCol = {1:9, 3:10, 6:11,24:12}
        maxSize = float(max(self.FlatList, key = lambda x:int(x[timeCol[time]]))[timeCol[time]])
        self.ms = maxSize
        for i in self.FlatList:
            location = str(i[3]) + str(i[2])
            widget = self.widget_dict[location]
            size = float(i[timeCol[time]])/maxSize
            self.createOval(size,widget)
                        
    def clear_canvas(self):
        '''
        Erases all the circles from each canva on the flat.
        '''
        for i in self.FlatList:
            location = str(i[3]) + str(i[2])
            widget = self.widget_dict[location]
            widget.delete("all")
                        
    def initUI(self):
        '''
        Initializes the interface
        '''
        AtoH = {}
        for x, y in zip(range(1, 10), string.ascii_uppercase):
            AtoH[x] = y
        AtoH[9] = ''
            
        self.parent.title("Aphid Visualizer")
        
        Style().configure("TButton", padding=(0, 5, 0, 5),
            font='serif 10')
        
        for i in range(5):
            self.columnconfigure(i, pad=3)
            if i > 0:
                label = str(i)
                widget = Label(self, text=label)
                widget.grid(row=0, column=i)
                self.widget_dict["0,%s" % label] = widget
        
        for i in range(10):
            self.rowconfigure(i, pad=5)
            if i > 0:
                label = AtoH[i]
                widget = Label(self, text=label)
                widget.grid(row=i, column=0)
                self.widget_dict["%s,0" % label] = widget
        self.rowconfigure(9, pad = 25)
        
        entry = Entry(self)
        
        for r in range(1, 9):
            for c in range(1, 5):
                lbl = Canvas(self, width=64,height=64)
                lbl.grid(row=r, column=c)
                self.widget_dict["%s%s" % (AtoH[r], c)] = lbl         
        
        
        newFile = Button(self, text="New File")
        newFile.grid(row=9, column=1, sticky= "we")
        newFile.bind("<Button-1>", self.set_dataList)
        self.widget_dict["newFile"] = newFile
        next = Button(self, text="Next")
        next.grid(row=9, column=3, sticky= "we")
        next.bind("<1>", self.change_time_forward)
        self.widget_dict["next"] = next
        previous = Button(self, text="Previous")
        previous.grid(row=9, column=2, sticky= "we")
        previous.bind("<1>", self.change_time_backward)
        draw = Button(self,text="Draw")
        #draw.grid(row=9, column = 4, sticky= "we")
        draw.bind("<1>", self.draw_circles)
        self.widget_dict["draw"] = draw
        testprint = Button(self, text="testprint")
        testprint.grid(row=9, column=4, sticky= "we")
        testprint.bind('<1>', self.print_value_event)
        self.widget_dict["testprint"] = testprint
        self.pack()
        
                   

def main():  
    root = Tk()
    app = AphidGUI(root)
    root.mainloop() 
 


if __name__ == '__main__':
    main()