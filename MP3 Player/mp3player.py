#Import necessary libraries.

from tkinter import * #This imports everything that tkinter has to offer.
from tkinter import filedialog #Importing filedialog from tkinter will provide classes and factory functions for creating file/directory selection windows.
from pygame import mixer #Import mixer() from pygame to help control the music.

#BASIC FUNCTIONS

mixer.init() #Initialize the mixer.
mixer.music.load('o-come-all-ye-faithful.mp3') #Mixer.music.load.() is where the music file is loaded.
mixer.music.play() #For playing the music.
mixer.music.pause() #Pause music file.
mixer.music.unpause() #Unpause musice file.
mixer.music.stop() # This will stop music from playing, then the loaded music will be cleared in the pygame memory.

#Now, we can implement our class & bluttons for the application.

class MusicPlayer:
    def __init__(self, window ): #Initiate the MusicPlayer. Self allows access to all the instances defined within a class, including its methods and attributes.
        #Window represent the boxes/buttons.
        window.geometry('320x100'); window.title('VanFossen Music Player'); window.resizable(0,0); window.configure(background = "yellow") #This will determine the size and title of the window.
        Load = Button(window, text = 'Load', width = 10, font = ('Times', 10), command = self.load)
        Play = Button(window, text = 'Play', width = 10, font = ('Times', 10), command = self.play)
        Pause = Button(window, text = 'Pause', width = 10, font = ('Times', 10), command = self.pause)
        Stop = Button(window, text = 'Stop', width = 10, font = ('Times', 10), command = self.stop)
        Load.place(x = 0, y = 20); Play.place(x = 110, y = 20); Pause.place(x = 220, y = 20); Stop.place(x = 110, y = 60)  #The X and Y axises determine the placement of the buttons within the window.
        self.music_file = False
        self.playing_state = False

    def load(self):
        self.music_file = filedialog.askopenfilename() #You will be asked to choose the music file to be loaded.

#Now that the file is loaded, a function must be implemented to play the music file.
    
    def play(self): #Define function of Play button.
        if self.music_file:
            mixer.init() #Initiate music controls
            mixer.music.load(self.music_file) #Load music file
            mixer.music.play() #Play music.
    def pause(self): #Define function of Pause button.
        if not self.playing_state:
            mixer.music.pause() #Pause music if music is playing.
            self.playing_state = True
        else:
            mixer.music.unpause() #Unpause music if it is not playing.
            self.playing_state = False
    def stop(self): #Definie function of Stop button.
        mixer.music.stop() #stop music all-together.

root = Tk() #The main, empty application window is created. 
app = MusicPlayer(root) #Root is passed to the MusicPlayer class.
root.mainloop() #This is where the event handling starts. All events are received from the window system and dispatch to the application widgets. Then, it ids terminated when we click the x or call the quit() method.

       
