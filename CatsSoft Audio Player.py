#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Andruska
#
# Created:     13.03.2024
# Copyright:   (c) Andruska 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# Importăm modulele necesare
import tkinter as tk
import customtkinter as ctk
import customtkinter
from tkinter import Tk, Frame, Entry, Toplevel, Button, Canvas, Label, Listbox, Scrollbar, RIGHT, LEFT, TOP, Y, X, BOTH, END, Menu, PhotoImage, filedialog, ttk, messagebox, N, S, E, W
from tkinter import StringVar, TOP
from tkinter import DISABLED, NORMAL
from tkinter import filedialog
from tkinter import BOTH
from tkinter.messagebox import showinfo
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageFilter
from customtkinter import CTkEntry, CTkButton, CTkLabel, CTkImage, CTkComboBox, CTk
from customtkinter import *
import tkinter.ttk as ttk  # Import the ttk module
from tktooltip import ToolTip
from customtkinter.windows.widgets.image import CTkImage
from CTkListbox import *
import sys
import os
import struct
import time
import requests
import platform
import ctypes
import ctypes as ct
from ctypes import c_float, c_ulong, c_void_p, c_buffer, POINTER, pointer
from ctypes.wintypes import BOOL
from ctypes import windll
from ctypes import *

import numpy
import numpy as np
import numpy.fft as fftw
from numpy.random import normal
from numpy import random
import pandas as pd  # Add this line for pandas

from scipy.ndimage import gaussian_filter1d
from scipy.stats import norm
from scipy import signal
from scipy.fft import fft
from scipy.signal import find_peaks

import math  # Import the math module
import time
import os
import json
import configparser
from configparser import ConfigParser

# --- for example data --
import random
from random import randint
import pickle
import webbrowser

#  BASS_ChannelGetData flags
BASS_DATA_AVAILABLE = 0         # query how much data is buffered
BASS_DATA_FLOAT = 0x40000000    # flag: return floating-point sample data
BASS_DATA_FFT512 = 0x80000000   # 512 sample FFT
BASS_DATA_FFT1024 = 0x80000001  # 1024 FFT
BASS_DATA_FFT2048 = 0x80000002  # 2048 FFT
BASS_DATA_FFT4096 = 0x80000003  # 4096 FFT
BASS_DATA_FFT8192 = 0x80000004  # 8192 FFT
BASS_DATA_FFT_INDIVIDUAL = 0x10 # FFT flag: FFT for each channel, else all combined
BASS_DATA_FFT_NOWINDOW = 0x20   # FFT flag: no Hanning window

#  BASS_ChannelGetTags types : what's returned
BASS_TAG_ID3 = 0    # ID3v1 tags : 128 byte block
BASS_TAG_ID3V2 = 1  # ID3v2 tags : variable length block
BASS_TAG_OGG = 2    # OGG comments : array of null-terminated UTF-8 strings
BASS_TAG_HTTP = 3   # HTTP headers : array of null-terminated ANSI strings
BASS_TAG_ICY = 4    # ICY headers : array of null-terminated ANSI strings
BASS_TAG_META = 5   # ICY metadata : ANSI string
BASS_TAG_VENDOR = 9    # OGG encoder : UTF-8 string
BASS_TAG_LYRICS3 = 10  # Lyric3v2 tag : ASCII string
BASS_TAG_RIFF_INFO = 0x100 # RIFF/WAVE tags : array of null-terminated ANSI strings
BASS_TAG_MUSIC_NAME = 0x10000    # MOD music name : ANSI string
BASS_TAG_MUSIC_MESSAGE = 0x10001 # MOD message : ANSI string
BASS_TAG_MUSIC_INST = 0x10100    #  + instrument #, MOD instrument name : ANSI string
BASS_TAG_MUSIC_SAMPLE = 0x10300  #  + sample #, MOD sample name : ANSI string

system_architecture = platform.architecture()[0]
if system_architecture == "32bit":
    BASS_DLL_PATH = os.path.join(os.getcwd(), "bass/x86/bass.dll")
else:
    BASS_DLL_PATH = os.path.join(os.getcwd(), "bass/x64/bass.dll")

# Încarcă biblioteca BASS
bass_dll = ctypes.cdll.LoadLibrary(BASS_DLL_PATH)

default_song_file = "music/Nemuritorii - Viata-i viata.mp3"
song_file = None

# Modificare pentru citirea din fișierul de configurare
def read_song_file_configuration():

    # Define the path where you want to create the folder
    song_history_path = 'history'

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Try to read from an existing INI file
    config_history_file_path = os.path.join(song_history_path, "config.ini")
    # print(f"Trying to read config file: {config_file_path}")

    if not os.path.exists(config_history_file_path):
        # print(f"Config file does not exist at {config_file_path}")
        return None

    config.read(config_history_file_path)

    # Try to get the value from the configuration file
    try:
        song_file = config["History"]["song_history"]
        if not song_file:  # Verifică dacă song_file este gol
            song_file = default_song_file  # Dacă este gol, folosește default_song_file
    except (configparser.NoSectionError, configparser.NoOptionError):
        song_file = default_song_file
    return song_file

# Use the `read_config_file` function to set the `output_path` variable
song_file = read_song_file_configuration()

if song_file is not None:
    print("Paleta citită din fișierul de configurare:")
    print(song_file)
else:
    print("Nu s-a putut citi numele melodiei din fișierul de configurare.")

# Initialize the DLL
def onInit_Lib():
    # Define arg types
    bass_dll.BASS_Init.argtypes = [ct.c_int, ct.c_uint, ct.c_uint, ct.c_uint, ct.c_uint]
    # Define result types
    bass_dll.BASS_Init.restype = ct.c_int
    # Call function with args
    c = bass_dll.BASS_Init(-1, 44100, 0, 0, 0)
    print(c)

def onStream():
    # Arg definitions
    # HSTREAM BASS_StreamCreateFile(BOOL mem, void *file, QWORD offset, QWORD length, DWORD flags);
    bass_dll.BASS_StreamCreateFile.argtypes = [BOOL, ct.c_char_p, ct.c_int64, ct.c_int64, ct.c_uint]
    # Define restypes
    bass_dll.BASS_StreamCreateFile.restype = ct.c_uint
    # path = os.getcwd()
    # full = os.path.join(path, "music/Nemuritorii - Viata-i viata.mp3")
    # print(full)
    stream = bass_dll.BASS_StreamCreateFile(False, song_file.encode("utf-8"), 0, 0, 0)
    if stream == 0:
        error_code = bass_dll.BASS_ErrorGetCode()
        print(f"Error creating stream: {error_code}")
    else:
        print(f"Stream created successfully: {stream}")

    return stream

def onPlay(stream):
    # Define args
    # BASS_ChannelPlay(stream, FALSE); // play the stream
    bass_dll.BASS_ChannelPlay.argtypes = [ct.c_uint, BOOL]
    # Call function
    bass_dll.BASS_ChannelPlay(stream, False)
    get_meta_tags(stream)

def onPause(stream):
    # Define args
    # BASS_ChannelPause(stream); // pause the stream
    bass_dll.BASS_ChannelPause.argtypes = [ct.c_uint]
    # Call function
    bass_dll.BASS_ChannelPause(stream)

def onStop(stream):
    # Define args
    # BASS_ChannelStop(stream); // stop the stream
    bass_dll.BASS_ChannelStop.argtypes = [ct.c_uint]
    # Call function
    bass_dll.BASS_ChannelStop(stream)

def get_tag(stream, tag_type):
    try:
        result = bass_dll.BASS_ChannelGetTags(stream, tag_type)
        if result:
            return ctypes.c_char_p(result).value.decode("utf-8")
    except Exception as e:
        print(f"Error getting tag {tag_type}: {e}")
    return None

def extract_tag_ID3(stream):
    tag_ID3 = "Unknown Stream Info"

    ID3 = bass_dll.BASS_ChannelGetTags(stream, BASS_TAG_ID3)

    if ID3 != -1:
        tag_ID3 = ctypes.c_char_p(ID3).value.decode("utf-8")

        print(f"Stream Title: {tag_ID3}")
        stream_info_title.configure(text=f"{tag_ID3}")

    return tag_ID3

def get_meta_tags(stream):

    # Set ctypes function types for BASS_ChannelGetTags
    bass_dll.BASS_ChannelGetTags.argtypes = [ctypes.c_uint, ctypes.c_ulong]
    bass_dll.BASS_ChannelGetTags.restype = ctypes.c_void_p

    # Initialize tag variables
    tag_ID3 = None

    # Attempt to retrieve tags
    tag_ID3 = get_tag(stream, BASS_TAG_ID3)

    # Process tags based on format and reliability
    if tag_ID3:
        extract_tag_ID3(stream)

        # Periodically update tags (optional)
    app.after(10000, lambda: get_meta_tags(stream))

# System Settings
customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("black")  # Themes: blue (default), dark-blue, green

def setup_interface(app):
    frame = Frame(app)
    frame.pack()

    # Configurare dimensiuni și poziționare fereastră
    window_height = 700
    window_width = 1008
    x_position = (app.winfo_screenwidth() // 2) - (window_width // 2)
    y_position = (app.winfo_screenheight() // 4) - (window_height // 4)
    app.geometry('{}x{}+{}+{}'.format(window_width, window_height, x_position, y_position))
    app.resizable(width=False, height=False)
    app.config(background="#2b2c2e")

def load_images():
    # Încărcare imagini și iconi
    app_icon_path = get_image_path("images/app.ico")
    app.iconbitmap(app_icon_path)

    # Încărcare imagine de fundal
    background_image = Image.open(get_image_path("images/background_image.jpg"))
    background_image = background_image.resize((1260, 875), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(background_image)
    app.background_photo = background_photo  # Menține referința globală la imagine

def get_image_path(filename):
    import os
    import sys
    from os import chdir
    from os.path import join
    from os.path import dirname
    from os import environ

    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        chdir(sys._MEIPASS)
        filename = join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        chdir(environ['_MEIPASS2'])
        filename = join(environ['_MEIPASS2'], filename)
    else:
        chdir(dirname(sys.argv[0]))
        filename = join(dirname(sys.argv[0]), filename)

    return filename

# ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Crearea ferestrei principale
app = customtkinter.CTk()  # create a Tk window
# app.tk.call('tk', 'scaling', 2.0)
app.title('CatsSoft Audio Player')

# Configurare interfață și încărcare imagini
setup_interface(app)
load_images()

# Creare etichetă pentru imaginea de fundal
background_label = tk.Label(app, image=app.background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Inițializează biblioteca BASS
onInit_Lib()

# Creează un flux audio din fișierul MP3
stream = onStream()

# Font
my_font = customtkinter.CTkFont(family="sans-serif", size=12)

# Creeăm un text pentru a afișa detalii despre postul radio
stream_info_title = customtkinter.CTkLabel(app, text="", font=("Helvetica", 12, "normal"), width=650, height=20, text_color="#259B9A", bg_color="#161619", fg_color="#161619")
stream_info_title.place(relx=0.170, rely=0.83, anchor="nw")

# Previous button play
img_prev_button_normal = Image.open(get_image_path("images/prev_play_btn_normal.png"))  # Înlocuiți cu calea către imaginea dvs.
img_prev_button_normal = img_prev_button_normal.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_prev_button_normal = ImageTk.PhotoImage(img_prev_button_normal)

img_prev_button_hover = Image.open(get_image_path("images/prev_play_btn_press.png"))  # Load hover image
img_prev_button_hover = img_prev_button_hover.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_prev_button_hover = ImageTk.PhotoImage(img_prev_button_hover)

def on_hover_prev(event):
    prev_button.configure(image=img_prev_button_hover)  # Switch to hover image

def on_leave_prev(event):
    prev_button.configure(image=img_prev_button_normal)  # Reset to normal image

# Define the Button
prev_button = tk.Button(app, image=img_prev_button_normal, width=42, height=42, bd=0, bg="#161619", activebackground="#161619", cursor="hand2", command=lambda: onPrev())
prev_button.image = img_prev_button_normal
prev_button.place(relx=0.400, rely=0.95, anchor="center")

# prev_button = customtkinter.CTkButton(app, width=10, height=10, text="<<", text_color="#F2F2F2", font=("Helvetica", 10, "normal"), command=lambda: onPrev(stream))
# prev_button.place(relx=0.400, rely=0.95, anchor="center")

# Atașați funcțiile de eveniment la eticheta de descărcare
prev_button.bind("<Enter>", on_hover_prev)
prev_button.bind("<Leave>", on_leave_prev)

# Play button
img_play_button_normal = Image.open(get_image_path("images/play_btn_normal.png"))  # Înlocuiți cu calea către imaginea dvs.
img_play_button_normal = img_play_button_normal.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_play_button_normal = ImageTk.PhotoImage(img_play_button_normal)

img_play_button_hover = Image.open(get_image_path("images/play_btn_press.png"))  # Load hover image
img_play_button_hover = img_play_button_hover.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_play_button_hover = ImageTk.PhotoImage(img_play_button_hover)

def on_hover_play(event):
    play_button.configure(image=img_play_button_hover)  # Switch to hover image

def on_leave_play(event):
    play_button.configure(image=img_play_button_normal)  # Reset to normal image

# play_button = customtkinter.CTkButton(app, width=10, height=10, text="Play", text_color="#F2F2F2", font=("Helvetica", 10, "normal"), command=lambda: onPlay(stream))
# play_button.place(relx=0.450, rely=0.95, anchor="center")

play_button = tk.Button(app, image=img_play_button_normal, width=42, height=42, bd=0, bg="#161619", activebackground="#161619", cursor="hand2", command=lambda: onPlay(stream))
play_button.image = img_play_button_normal
play_button.place(relx=0.450, rely=0.95, anchor="center")

# Atașați funcțiile de eveniment la eticheta de descărcare
play_button.bind("<Enter>", on_hover_play)
play_button.bind("<Leave>", on_leave_play)

# Pause button
img_pause_button_normal = Image.open(get_image_path("images/pause_btn_normal.png"))  # Înlocuiți cu calea către imaginea dvs.
img_pause_button_normal = img_pause_button_normal.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_pause_button_normal = ImageTk.PhotoImage(img_pause_button_normal)

img_pause_button_hover = Image.open(get_image_path("images/pause_btn_press.png"))  # Load hover image
img_pause_button_hover = img_pause_button_hover.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_pause_button_hover = ImageTk.PhotoImage(img_pause_button_hover)

def on_hover_pause(event):
    pause_button.configure(image=img_pause_button_hover)  # Switch to hover image

def on_leave_pause(event):
    pause_button.configure(image=img_pause_button_normal)  # Reset to normal image

# pause_button = customtkinter.CTkButton(app, width=10, height=10, text="Pause", text_color="#F2F2F2", font=("Helvetica", 10, "normal"), command=lambda: onPause(stream))
# pause_button.place(relx=0.500, rely=0.95, anchor="center")

pause_button = tk.Button(app, image=img_pause_button_normal, width=42, height=42, bd=0, bg="#161619", activebackground="#161619", cursor="hand2", command=lambda: onPause(stream))
pause_button.image = img_pause_button_normal
pause_button.place(relx=0.500, rely=0.95, anchor="center")

# Atașați funcțiile de eveniment la eticheta de descărcare
pause_button.bind("<Enter>", on_hover_pause)
pause_button.bind("<Leave>", on_leave_pause)

# Stop button
img_stop_button_normal = Image.open(get_image_path("images/stop_btn_normal.png"))  # Înlocuiți cu calea către imaginea dvs.
img_stop_button_normal = img_stop_button_normal.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_stop_button_normal = ImageTk.PhotoImage(img_stop_button_normal)

img_stop_button_hover = Image.open(get_image_path("images/stop_btn_press.png"))  # Load hover image
img_stop_button_hover = img_stop_button_hover.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_stop_button_hover = ImageTk.PhotoImage(img_stop_button_hover)

def on_hover_stop(event):
    stop_button.configure(image=img_stop_button_hover)  # Switch to hover image

def on_leave_stop(event):
    stop_button.configure(image=img_stop_button_normal)  # Reset to normal image

# stop_button = customtkinter.CTkButton(app, width=10, height=10, text="Stop", text_color="#F2F2F2", font=("Helvetica", 10, "normal"), command=lambda: onStop(stream))
# stop_button.place(relx=0.550, rely=0.95, anchor="center")

stop_button = tk.Button(app, image=img_stop_button_normal, width=42, height=42, bd=0, bg="#161619", activebackground="#161619", cursor="hand2", command=lambda: onStop(stream))
stop_button.image = img_stop_button_normal
stop_button.place(relx=0.550, rely=0.95, anchor="center")

# Atașați funcțiile de eveniment la eticheta de descărcare
stop_button.bind("<Enter>", on_hover_stop)
stop_button.bind("<Leave>", on_leave_stop)

# Next button
img_next_button_normal = Image.open(get_image_path("images/next_play_btn_normal.png"))  # Înlocuiți cu calea către imaginea dvs.
img_next_button_normal = img_next_button_normal.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_next_button_normal = ImageTk.PhotoImage(img_next_button_normal)

img_next_button_hover = Image.open(get_image_path("images/next_play_btn_press.png"))  # Load hover image
img_next_button_hover = img_next_button_hover.resize((42, 42), Image.LANCZOS)  # Redimensionați imaginea la dimensiunea dorită
img_next_button_hover = ImageTk.PhotoImage(img_next_button_hover)

def on_hover_next(event):
    next_button.configure(image=img_next_button_hover)  # Switch to hover image

def on_leave_next(event):
    next_button.configure(image=img_next_button_normal)  # Reset to normal image

# next_button = customtkinter.CTkButton(app, width=10, height=10, text=">>", text_color="#F2F2F2", font=("Helvetica", 10, "normal"), command=lambda: onNext(stream))
# next_button.place(relx=0.600, rely=0.95, anchor="center")

next_button = tk.Button(app, image=img_next_button_normal, width=42, height=42, bd=0, bg="#161619", activebackground="#161619", cursor="hand2", command=lambda: onNext())
next_button.image = img_next_button_normal
next_button.place(relx=0.600, rely=0.95, anchor="center")

# Atașați funcțiile de eveniment la eticheta de descărcare
next_button.bind("<Enter>", on_hover_next)
next_button.bind("<Leave>", on_leave_next)

# Lista cu fișierele selectate anterior
lista_repro = []
audio_files = []
# Variabile pentru player
current = 0

def get_audio_files(directory):
    global lista_repro # Declare lista_repro as global
    audio_files = []
    for app_, dirs, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1] == ".mp3" or ".wav" or ".ogg" or ".xm" or ".mod":
                path = (app_ + '/' + file).replace('\\','/')
                # Citirea numelui fișierului cu codificarea Unicode utf-8
                audio_files.append(path.encode('utf-8').decode('utf-8'))
    history_path = "history"
    with open(os.path.join(history_path, 'history.m3u'), 'wb') as writehistoryfile:
        pickle.dump(audio_files, writehistoryfile)
    lista_repro = audio_files  # Assign to the global variable lista_repro
    song_frame['text'] = f'Total files: -{str(len(lista_repro))}'
    playlist.delete(0, tk.END)
    enumerate_songs(playlist, audio_files)

    return audio_files

# Funcție pentru a enumera și afișa fișierele într-o listă
def enumerate_songs(playlist, audio_files):
    playlist.delete(0, tk.END)
    for index, song in enumerate(audio_files):
        playlist.insert(index, os.path.basename(song))

def open_folder():
    global history_path, directory
    directory = filedialog.askdirectory()
    if directory:
        history_path = directory
        load_audio_files_history()  # Încărcăm istoricul anterior
        audio_files = get_audio_files(directory)
        song_frame['text'] = f'Total files: -{str(len(lista_repro))}'
        enumerate_songs(playlist, audio_files)

# Funcție pentru a încărca istoricul fișierelor selectate anterior
def load_audio_files_history():
    global lista_repro

    history_path = "history"

    history_file_path = os.path.join(history_path, "history.m3u")
    if os.path.exists(history_file_path):
        with open(history_file_path, 'rb') as fb:
            lista_repro = pickle.load(fb)
    else:
        lista_repro = []

load_audio_files_history()

# Dimensiuni fereastră
song_frame = tk.LabelFrame(app, text=f'Total Fisiere: {str(len(lista_repro))}',font=("comic sans",15), bg='#161619', fg="#259B9A", bd=0, highlightthickness=0)
song_frame.config(width=820,height=200)
song_frame.place(relx=0.170, rely=0.47, anchor="nw")

scrollbar = customtkinter.CTkScrollbar(song_frame, height=2, bg_color="#161619", fg_color="#161619", button_color="#04706d", orientation="vertical")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

playlist = tk.Listbox(song_frame, height=12, width=88, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, font=("Helvetica", 12, "normal"), activestyle='dotbox', highlightcolor="#3c3d45", selectbackground="#141414", bg='#161619', fg="#259B9A", bd=0, highlightthickness=0, borderwidth=0, selectborderwidth=0, relief="flat")
history_path = "history"
history_file_path = os.path.join(history_path, "history.m3u")
if os.path.exists(history_file_path):
    with open(history_file_path, 'rb') as fb:
        lista_repro = pickle.load(fb)
    playlist.delete(0, tk.END)
    for index, song in enumerate(lista_repro):
        playlist.insert(index, os.path.basename(song))
else:
    enumerate_songs(playlist, audio_files)

# enumerate_songs(playlist, audio_files)
# playlist.config(height=15, width=130)

scrollbar.bind("<Configure>", lambda e: playlist.yview_moveto(0))

playlist.pack(padx=0.1, pady=0.1, side="top", anchor="center", fill=BOTH)

# Buton pentru a deschide dosarul cu fișiere audio
# open_folder_button = tk.Button(app, text="Deschide dosar", font=("Helvetica", 10, "normal"), bd=0, bg="#1D8261", fg="#161619", activebackground="#161619", cursor="hand2", command=open_folder)
# open_folder_button.place(relx=0.20, rely=0.85, anchor="center")

def play(event=None):  # Receives the event object
    global stream, current
    print("Playing track")
    if event is not None:
        current = playlist.curselection()[0]
        for i in range(len(lista_repro)):
            playlist.itemconfigure(i, bg='#161619')

            # Stop previous stream if it exists
            onStop(stream)

            play_song(current)

def play(event=None):
    global current
    current = playlist.curselection()
    if current:
        current = int(current[0])
        play_song(current)
        # Verificăm dacă indicele este valid înainte de a configura elementul
        if current < playlist.size():
            playlist.itemconfigure(current, bg='#161619')

            # Stop previous stream if it exists
            onStop(stream)

            play_song(current)
        else:
            print("Index out of range")
    else:
        print("No song selected")

def onPrev():
    global current
    print("Începe redarea fisierului anterior...")
    if current > 0:
        playlist.itemconfigure(current, bg='#161619')  # Update the color before moving to the previous track
        playlist.selection_clear(first=current)  # Deselect the previous selected item
        current -= 1
    else:
        current = len(lista_repro) - 1
    # Call play_song with the updated current
    play_song(current)

def onNext():
    global current
    print("Începe redarea următorului fisier...")
    if current < len(lista_repro) - 1:
        playlist.itemconfigure(current, bg='#161619')  # Update the color before moving to the next track
        playlist.selection_clear(first=current)  # Deselect the previous selected item
        current += 1
    else:
        current = 0
    # Call play_song with the updated current
    play_song(current)

# Funcție pentru a porni redarea melodiei
def play_song(current):
    global stream, stop_thread, song_length
    print("Playing track")
    for i in range(len(lista_repro)):
        playlist.itemconfigure(i, bg='#161619')

    # Stop previous stream if it exists
    onStop(stream)

    # Obțineți calea fișierului
    filepath = lista_repro[current]

    # Utilizează codificarea Unicode (utf-8) pentru numele fișierului
    stream = bass_dll.BASS_StreamCreateFile(False, filepath.encode("utf-8"), 0, 0, 0)
    if stream == 0:
        error_code = bass_dll.BASS_ErrorGetCode()
        print(f"Error creating stream: {error_code}")
        stream_info_title.configure(text=f"Error creating stream: {error_code}")
    else:
        print(f"Stream created successfully: {stream}")
        stream_info_title.configure(text=f"Stream created successfully: {stream}")

        bass_dll.BASS_ChannelPlay(stream, False)

        stream_info_title['text'] = os.path.basename(lista_repro[current])
        stream_info_title.configure(text=os.path.basename(lista_repro[current]))

        playlist.activate(current)
        playlist.itemconfigure(current, bg='#141414')

        # Define the path where you want to create the folder
        history_path = 'history'

        # Check if the folder exists already
        if not os.path.exists(history_path):
            os.makedirs(history_path)

        # Create the ConfigParser object
        config = configparser.ConfigParser()

        # If the section 'Settings' doesn't exist, add it
        if 'History' not in config.sections():
            config.add_section('History')

        # Add the settings to the ini file
        config.set('History', 'song_history', filepath)  # Salvați numele paletelor în fișierul de configurare

        # Write to the ini file
        with open(os.path.join(history_path, 'config.ini'), 'w') as confighistoryfile:
            config.write(confighistoryfile)

playlist.bind('<Double-1>', play)

# Add files

image_select_files_button = PhotoImage(
    file=get_image_path("images/add_icon.png")
)
select_files_button = Button(
    cursor="hand2",
    image=image_select_files_button,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_folder(),
    activebackground="#161619",
    relief="flat",
    fg="#161619",
    bg="#161619",
    text="Folder"
)
select_files_button.place(
    x=175.2235107421875,
    y=744.71820068359375,
    width=32,
    height=32
)
ToolTip(select_files_button, msg="Add files...", delay=0)

# Open directory

directory = history_path

def open_output_directory():
    global history_path, directory
    try:
        if directory:
            if directory and os.path.exists(directory):  # Verifică dacă directory nu este None și există pe disc
                if sys.platform.startswith('win'):
                    os.startfile(directory)
                elif sys.platform.startswith('darwin'):
                    webbrowser.open('file://' + directory)
                elif sys.platform.startswith('linux'):
                    webbrowser.open(directory)
        else:
            print("Error: Directory is not set or does not exist.")
    except Exception as e:
        print(f"Error opening directory: {str(e)}")

image_open_directory_button = PhotoImage(
    file=get_image_path("images/folder_icon.png")
)
open_directory_button = Button(
    cursor="hand2",
    image=image_open_directory_button,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: open_output_directory(),
    activebackground="#161619",
    relief="flat",
    fg="#161619",
    bg="#161619",
    text="Settings",
    state=NORMAL
)
open_directory_button.place(
    x=225.2235107421875,
    y=744.71820068359375,
    width=32,
    height=32
)
ToolTip(open_directory_button, msg="Open output directory...", delay=0)

# Trash files
def trash_files():
    global history_path

    stream_info_title.configure(text="")
    playlist.delete(0, tk.END)

    song_frame.configure(text=f"Total Fisiere: ")

    history_path = "history"
    # Construim calea completă către fișierul istoric
    myfile = os.path.join(history_path, "history.m3u")

    # Verificăm dacă fișierul există și îl ștergem dacă este cazul
    if os.path.isfile(myfile):
        os.remove(myfile)
        print(f"File {myfile} successfully removed.")
    else:
        print(f"Error: File {myfile} not found.")

image_trash_files_button = PhotoImage(
    file=get_image_path("images/trash_icon.png")
)
trash_files_button = Button(
    cursor="hand2",
    image=image_trash_files_button,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: trash_files(),
    activebackground="#161619",
    relief="flat",
    fg="#161619",
    bg="#161619",
    text="Trash",
    state=NORMAL
)
trash_files_button.place(
    x=275.2235107421875,
    y=744.71820068359375,
    width=32,
    height=32
)
ToolTip(trash_files_button, msg="Remove...", delay=0)

running = True

BASS_POS_BYTE = 0

BASS_DATA_FFT256 = 256
BASS_DATA_FFT512 = 512
BASS_DATA_FFT1024 = 1024
BASS_DATA_FFT2048 = 2048
BASS_DATA_FFT4096 = 4096
BASS_DATA_FFT8192 = 8192
BASS_DATA_FFT16384 = 16384
BASS_DATA_FFT32768 = 32768

# Variabile globale
NUM_BARS = 100
bar_width = 2
bar_height = 200

# Dimensiuni fereastră
WIDTH = 820
HEIGHT = 200

# Dimensiuni fereastră
main_frame = tk.Frame(app, bg='#161619', width=WIDTH, height=HEIGHT)
main_frame.place(relx=0.170, rely=0.13, anchor="nw")

# Canvas pentru vizualizare
waveform_canvas = tk.Canvas(main_frame, width=WIDTH, height=HEIGHT, bg="#161619", bd=0, highlightthickness=0)
waveform_canvas.pack(padx=0.1, pady=0.1, side="top", anchor="center", fill=BOTH)

fft_data = np.zeros(2048)
# Pre-calculati valorile trigonometrice pentru scalarea logaritmica
log_scale_factors = np.log1p(np.arange(2048)) / np.log1p(2047)

# In update_spectrum function:
fft_data = fft_data * log_scale_factors

sample_rate = 44100
intensity = 2048

# Variabile pentru animație
threshold = 0.1  # Define the threshold value
distance = 10  # Define the distance value
zoom_level = 1.0  # Valoarea inițială a zoom-ului
peaks = []  # Add this line to define peaks

# Generarea gradientului de culori
frequencies = np.fft.fftfreq(len(fft_data), d=1/sample_rate)[:len(fft_data)//2]
bar_ids = []

sample_rate = 44100
intensity = 2048
audio_data = None

default_path = "settings"
default_file = "spectrum_color.ini"

path = None
default_color = "#ffffff"  # White2

options_var = tk.StringVar()
options_var.set(default_color)

# Modificare pentru citirea din fișierul de configurare
def read_configuration():
    global default_path

    # Define the path where you want to create the folder
    path = default_path

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Try to read from an existing INI file
    config_file_path = os.path.join(path, "spectrum_color.ini")
    # print(f"Trying to read config file: {config_file_path}")

    if not os.path.exists(config_file_path):
        # print(f"Config file does not exist at {config_file_path}")
        return None

    config.read(config_file_path)

    # Try to get the value from the configuration file
    try:
        palette = config["Settings"]["spectrum_color"]
        # print(palette)
        options_var.set(palette if palette else default_color)  # Setare valoare implicita daca savedir este None
    except (configparser.NoSectionError, configparser.NoOptionError):
        # If the section or key doesn't exist, set the default value
        options_var.set(default_color)  # Setare valoare implicita daca sectiunea sau cheia nu exista
    return options_var.get()  # Return the value from output_var

# Use the `read_config_file` function to set the `output_path` variable
palette = read_configuration()

if palette is not None:
    print("Paleta citită din fișierul de configurare:")
    print(palette)
else:
    print("Nu s-a putut citi paleta de culori din fișierul de configurare.")

color_presets = {
    "Cool": ["#95d5b2", "#52b788", "#0081a7", "#005f73", "#0a9396"],
    "Vibrant": ["#ff0000", "#ff8000", "#ffff00", "#00ff00", "#0000ff"],
    "Grayscale": ["#f8f9fa", "#dee2e6", "#ced4da", "#adb5bd", "#6c757d", "#343a40"],
    "Rainbow": ["#c9184a", "#ff9f1c", "#ffca3a", "#560bad", "#3a0ca3", "#480ca8"],
    "Earth Tones": ["#8b4513", "#a0522d", "#deb887", "#bc8f8f", "#f4a460"],
    "Pastel": ["#E40C2B", "#c9ada7", "#8ecae6", "#219ebc", "#fb8500", "#d4a373"],
    "Ocean": ["#03045e", "#0077b6", "#00b4d8", "#90e0ef", "#caf0f8"],
    "Sunset": ["#ff7f50", "#ff6347", "#ff4500", "#dc143c", "#b22222"],
    "Amour": ["#590d22", "#800f2f", "#a4133c", "#c9184a", "#ff4d6d", "#ff758f", "#ff8fa3"],
    "Festival": ["#ABF62D", "#ABF62D", "#ABF62D"],
    "Bankyfy": ["#d9ed92", "#b5e48c", "#99d98c", "#76c893", "#34a0a4","#168aad","#1e6091","#184e77"],
    "Persoo": ["#259B9A", "#259B9A", "#259B9A"],
    "Drinks": ["#00ABE1", "#00ABE1", "#00ABE1"],
    "Omega": ["#F7F7F7", "#F7F7F7", "#F7F7F7"],
    "Farm": ["#004b23", "#006400", "#007200", "#008000", "#38b000", "#70e000", "#9ef01a", "#ccff33"],
}

initial_palette = read_configuration()  # Set initial value
current_palette = color_presets[initial_palette]  # Set initial palette
options_var.set(current_palette)

def change_color(palette_name):
    global current_palette, color_presets, default_path

    if palette_name in color_presets:
        current_palette = color_presets[palette_name]  # Setează paleta curentă cu paleta selectată
        print(palette_name)

        # Define the path where you want to create the folder
        path = default_path

        # Check if the folder exists already
        if not os.path.exists(path):
            os.makedirs(path)

        # Create the ConfigParser object
        config = configparser.ConfigParser()

        # If the section 'Settings' doesn't exist, add it
        if 'Settings' not in config.sections():
            config.add_section('Settings')

        # Add the settings to the ini file
        config.set('Settings', 'spectrum_color', palette_name)  # Salvați numele paletelor în fișierul de configurare

        # Write to the ini file
        with open(os.path.join(path, 'spectrum_color.ini'), 'w') as configfile:
            config.write(configfile)

# Create OptionMenu

appearance_mode_optionemenu = customtkinter.CTkOptionMenu(app, values=["Cool","Vibrant","Grayscale","Rainbow","Earth Tones","Pastel","Ocean","Sunset","Amour","Festival","Bankyfy","Persoo","Drinks","Omega","Farm"], text_color="#04706d", dropdown_text_color="#04706d", fg_color="#191919", dropdown_fg_color="#191919", dropdown_hover_color="#202020", button_color="#1A1A1A", command=change_color)
appearance_mode_optionemenu.place(relx=0.18, rely=0.40, anchor='nw')

def smooth_fft(fft_data, alpha=0.5):
    smoothed_fft = np.empty_like(fft_data)
    smoothed_fft[0] = fft_data[0]
    for i in range(1, len(fft_data)):
        smoothed_fft[i] = alpha * fft_data[i] + (1 - alpha) * smoothed_fft[i - 1]
    return smoothed_fft

# Funcția get_color trebuie să utilizeze paleta globală current_palette
def get_color(smoothed_fft, intensity):
    initial_palette = read_configuration()  # Set initial value
    current_palette = color_presets[initial_palette]  # Set initial palette
    color_indices = (np.floor(smoothed_fft * intensity / 10)).astype(int)
    color_indices = np.clip(color_indices, 0, len(current_palette) - 1)
    colors = [current_palette[index] for index in color_indices]
    return colors

def get_color(smoothed_fft, intensity, palette):
    global current_palette
    colors = []

    # Calculați numărul de culori în paletă și numărul total de bare
    num_colors = len(palette)
    num_bars = NUM_BARS

    # Calculați pasul variabil pentru a selecta culorile din paletă
    step = num_colors / num_bars

    # Selectați culorile din paletă pentru fiecare bară folosind un gradient uniform
    for i in range(num_bars):
        color_index = min(int(i * step), num_colors - 1)  # Asigurați-vă că indicele culorii este în limitele paletelor
        colors.append(palette[color_index])

    return colors

def update_spectrum():
    global waveform_canvas, bar_ids, peaks, threshold, distance, smooth_fft, zoom_level, current_palette

    length = 2048

    fft = (ctypes.c_float * length)()

    # Set ctypes function types for BASS_ChannelGetData
    bass_dll.BASS_ChannelGetData.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_float), ctypes.c_ulong]
    bass_dll.BASS_ChannelGetData.restype = ctypes.c_ulong

    # Obtaining spectrum data from the audio channel (stream)
    spectrum_data = bass_dll.BASS_ChannelGetData(stream, fft, BASS_DATA_FFT4096)

    # Verificare dacă datele de spectru sunt valide
    if spectrum_data != -1:
        # Convertirea datelor spectrului într-un array NumPy
        audio_data = np.frombuffer(fft, dtype=np.float32)

        # Verificare pentru valori NaN și Infinite
        if np.any(np.isnan(audio_data)) or np.any(np.isinf(audio_data)):
            # Tratare valori NaN și Infinite (înlocuire cu zero în acest exemplu)
            audio_data[np.isnan(audio_data)] = 0
            audio_data[np.isinf(audio_data)] = 0

        # Calcularea FFT
        fft_result = np.fft.fft(audio_data)
        fft_data = np.abs(fft_result)[:length]
        fft_data = smooth_fft(fft_data)

        # Calculul intensității globale
        intensity = np.sum(fft_data) / len(fft_data)

        # Desenarea spectrului
        draw_waveform(fft_data, zoom_level, current_palette)

        # Identify peaks in the spectrum
        peaks, _ = find_peaks(fft_data, height=threshold, distance=distance)

    # Repetarea actualizării
    app.after(30, update_spectrum)

def draw_waveform(fft_data, zoom_level, palette):
    global waveform_canvas, bar_ids, intensity

    # Calculul parametrilor formei de undă
    max_amplitude = np.max(fft_data)
    min_amplitude = np.min(fft_data)

    # Aplicarea scalei logaritmice și conversia în decibeli
    fft_data_db = 20 * np.log10(fft_data + 1e-6)  # Adăugăm o valoare mică pentru a evita log(0)

    # Normalizarea valorilor FFT
    max_db = np.max(fft_data_db)
    min_db = max_db - 60  # Afișăm un interval dinamic de 60 dB
    normalized_fft = (fft_data_db - min_db) / (max_db - min_db)

    # Lisarea valorilor FFT
    smoothed_fft = smooth_fft(normalized_fft)

    waveform_canvas.delete("all")

    colors = get_color(smoothed_fft, intensity, palette)  # Obțineți culorile pentru toate barele

    for i in range(NUM_BARS):
        start_index = i * (len(fft_data) // NUM_BARS)
        end_index = (i + 1) * (len(fft_data) // NUM_BARS)

        # Asigurați-vă că end_index este în limitele dimensiunii fft_data
        end_index = min(end_index, len(fft_data))

        x1 = i * (WIDTH / NUM_BARS) * zoom_level
        x2 = (i + 1) * (WIDTH / NUM_BARS) * zoom_level

        # Calculul valorii medii a FFT pentru bara curentă
        mean_fft = np.mean(fft_data[start_index:end_index])

        if max_amplitude != 0 and min_amplitude != 0:  # Verificăm dacă max_amplitude este nenul
            # Înălțimea barei
            y = (mean_fft / max_amplitude) * HEIGHT
        else:
            y = 0

        # Obținerea culorii pentru bara curentă din paletă
        color = colors[i]

        bar_id = waveform_canvas.create_line(x1, HEIGHT, x1, HEIGHT - y, width=bar_width, fill=color)
        bar_id = waveform_canvas.create_line(x1, HEIGHT - y, x2, HEIGHT - y, width=bar_width, fill=color)
        bar_id = waveform_canvas.create_line(x2, HEIGHT - y, x2, HEIGHT, width=bar_width, fill=color)
        bar_ids.append(bar_id)

        # Adaugă efectul de transparență
        waveform_canvas.itemconfig(bar_id, stipple="gray50")
        waveform_canvas.lower("transparent")  # Asigură că obiectele transparente sunt în spatele celorlalte

# Actualizare spectru
update_spectrum()

# Definiți constantele Windows
HWND_BROADCAST = 0xFFFF
WM_COMMAND = 0x0111
WM_SETTEXT = 0x000C

def update_volume(volume):
    # Convertiți volumul în intervalul 0.0 - 1.0
    volume_float = float(volume) / 100.0
    volume_ctypes = ctypes.c_float(volume_float)
    # Setați volumul utilizând BASS_SetVolume
    success = bass_dll.BASS_SetVolume(volume_ctypes)

    if success != 0:
        # Dacă setarea volumului a avut succes, actualizați bara de progres și textul
        volume_percent = int(volume_float * 100)
        volume_var.set(volume_percent)
        Percentage.configure(text=f"{volume_percent}%")
    else:
        # Dacă setarea volumului a eșuat, obțineți volumul actual
        current_volume = bass_dll.BASS_GetVolume()
        print(f"Failed to set volume. Current volume: {current_volume * 100}%")

# Creare variabilă Tkinter pentru a urmări volumul
volume_var = tk.IntVar()

# Progress percentage
Percentage = customtkinter.CTkLabel(app, text="0%", width=50, height=12, text_color="#259B9A", fg_color="#161619")
Percentage.place(relx=0.850, rely=0.88, anchor="center")

# Creare slider pentru ajustarea volumului
volume_slider = customtkinter.CTkSlider(app, from_=0, to=100, orientation=HORIZONTAL,state="normal", width=120, command=update_volume,
fg_color="#161619", bg_color="#161619", progress_color="#006a6c", button_color="#006a6c", button_hover_color="#37bf7b")
volume_slider.place(relx=0.740, rely=0.88, anchor="center")

# Setare inițială a volumului și afișare
initial_volume = 50
volume_slider.set(initial_volume)
update_volume(initial_volume)

def on_close():
    global running
    running = False
    # Opriți fluxul de date audio
    bass_dll.BASS_ChannelStop(stream)
    # Eliberați dispozitivul audio
    bass_dll.BASS_Free()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_close)

# Rularea aplicației
app.mainloop()
