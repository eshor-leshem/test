#! /usr/bin/python3

"""
Installing python packages on client environment to use Etool
"""

import pip
from  tkinter import *


class SetupGui:
    """
    DISABLED AT THE MOMENT
    """
    def __init__(self, master):
        self.master = master
        master.title("Etool setup")

        self.label = Label(master, text="Etool setup")
        self.label.pack()

        self.install_button = Button(master, text="Start Setup", command=self.install)
        self.install_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    # @staticmethod
    def install(self):
        for package in ['boto3', 'requests', 'paramiko', 'sshtunnel', 'flask']:
            print("Installing {}".format(package))
            pip.main(['install', package])


if __name__ == '__main__':
    for package in ['boto3', 'requests', 'paramiko', 'sshtunnel']:
        print("Installing {}".format(package))
        pip.main(['install', package])
    # root = Tk()
    # my_gui = SetupGui(root)
    # root.mainloop()
