import sys
import os
import subprocess
from PIL import Image, ImageSequence
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import TkinterDnD

# Function to create a GIF from a folder of images
def create_gif_from_images(folder_path, output_folder, output_name, gif_speed, dissolve, resample, colors):
    images = []

    # Load images from the folder
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
            image_path = os.path.join(folder_path, filename)
            image = Image.open(image_path)
            if colors:
                colors = int(colors)  # Convert the colors value to an integer
                image = image.quantize(colors=colors)
            # Resample the image
            new_size = (int(image.width * resample), int(image.height * resample))
            image = image.resize(new_size, resample=Image.BOX)

            # Convert image to RGBA
            image = image.convert('RGBA')
            # Limit the number of colors
            image = image.quantize(colors=colors)
            # Convert image back to RGBA
            image = image.convert('RGBA')
            images.append(image)

            # Apply dithering based on the selected option
            dither_method = dither_method_var.get()
            if dither_method == 'DITHER OPTIONS':
                image = image.convert('P', dither=Image.NONE)
            elif dither_method == 'NONE':
                image = image.convert('P', dither=Image.NONE)
            elif dither_method == 'FLOYDSTEINBERG':
                image = image.convert('P', dither=Image.FLOYDSTEINBERG)
            elif dither_method == 'RATERIZE':
                image = image.convert('P', dither=Image.RATERIZE)
            elif dither_method == 'ORDERED':
                image = image.convert('P', dither=Image.ORDERED)
            
    # Add dissolve effect between each image
    dissolved_images = []
    if dissolve == 0:
        dissolved_images = images.copy()
    else:
        for i in range(len(images) - 1):
            for j in range(dissolve):
                alpha = j / dissolve
                blend = Image.blend(images[i], images[i+1], alpha)
                dissolved_images.append(blend)
        dissolved_images.append(images[-1])

    # Save images as GIF
    if not output_name:
        output_name = os.path.basename(folder_path)
    output_path = os.path.join(output_folder, output_name + '.gif')
    dissolved_images[0].save(output_path,
               save_all=True,
               append_images=dissolved_images[1:],
               duration=gif_speed,
               loop=0)
    
# Open the GIF file immediately if the checkbutton is selected
    if open_gif.get():
        if os.name == 'nt':  # Windows
            os.startfile(output_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', output_path])
        elif os.name == 'posix':  # Linux
            subprocess.run(['xdg-open', output_path])
            
# Progress bar reset
    def reset_progress():
            progress_bar['value'] = 0
            progress_label.config(text="")

    # Schedule reset_progress to run after 12000 milliseconds (12 seconds)
    window.after(12000, reset_progress)
    
# Function to handle button click event
def create_gif(folder_path=None):
    status_label.config(text="Creating GIF...")
    images = []
    if not folder_path:
        folder_path = filedialog.askdirectory(title="Select Image Folder")
    if folder_path:
        output_name = output_name_entry.get()
        gif_speed = int(speed_entry.get())
        dissolve = int(dissolve_entry.get())
        resample = resample_slider.get()
        colors = colors_slider.get()
        total_images = len([name for name in os.listdir(folder_path) if (name.endswith('.png') or name.endswith('.jpg') or name.endswith('.jpeg'))])
        progress_bar['maximum'] = total_images
        progress_bar['value'] = 0
        progress_label.config(text="0%")
        for i, filename in enumerate(sorted(os.listdir(folder_path))):
            if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                image_path = os.path.join(folder_path, filename)
                image = Image.open(image_path)
                images.append(image)
                progress_bar['value'] = i + 1
                progress = (i + 1) / total_images * 99
                progress_label.config(text="%.0f%%" % progress)
                window.update_idletasks()
        output_folder = os.path.dirname(folder_path)
        create_gif_from_images(folder_path, output_folder, output_name, gif_speed, dissolve, resample, colors)
        status_label.config(text="Great Success!")
        progress_bar['value'] = 100
        progress_label.config(text="100%")

# Function to handle drop event
def drop(event):
    status_label.config(text="")
    folder_path = event.data
    if os.path.isdir(folder_path):
        create_gif(folder_path)

# Create a simple GUI using tkinter
window = TkinterDnD.Tk()
icon = tk.PhotoImage(master=window, file='icon_32.png')
window.wm_iconphoto(True, icon)
window.resizable(width=False, height=False)
window.geometry("+300+300")  # set position on the screen
window.geometry("225x550")
window.configure(bg='powder blue')
window.title("GIF IT")

# Add a label for formats
top_label = tk.Label(window, text="", bg='powder blue', borderwidth=0)
image = tk.PhotoImage(file="GIF_IT.png", width=200, height=100)
image_label = tk.Label(top_label, image=image)
top_label.pack(padx=0, pady=0)
image_label.configure(borderwidth=0, highlightthickness=0)
image_label.pack(padx=5, pady=5)

# Add a label and entry for output name
# photo1 = tk.PhotoImage(file="NAME_IT.png")
output_name_label = tk.Label(window, text="NAME IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
output_name_label.pack(pady=2)
output_name_entry = tk.Entry(window, bg='#E5F5F9')
output_name_entry.insert(tk.END, "")
output_name_entry.config(justify="center", validate='all', highlightthickness=0)
output_name_entry.pack(pady=2)
output_name_entry.focus()

# Add a label and entry for gif speed
# photo2 = tk.PhotoImage(file="TIME_IT.png")
speed_label = tk.Label(window, text="TIME IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
speed_label.pack(pady=2)
speed_entry = tk.Entry(window, bg='#E5F5F9')
speed_entry.insert(tk.END, "100")
speed_entry.config(justify="center", highlightthickness=0)
speed_entry.pack(pady=2)

# Add a label and entry for dissolve effect
dissolve_label = tk.Label(window, text="DISSOLVE IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
dissolve_label.pack(pady=2)
dissolve_entry = tk.Entry(window, bg='#E5F5F9')
dissolve_entry.insert(tk.END, "0")
dissolve_entry.config(justify="center", highlightthickness=0)
dissolve_entry.pack(pady=2)

# Create a style
style = ttk.Style()
style.theme_use('clam')
style.configure("blue.Horizontal.TScale", background='#B0E0E6', troughcolor='#B0E0E6', bordercolor='#B0E0E6', border=0)

# Create a StringVar to hold the resample value
resample_value = tk.StringVar()
resample_value.set("1.0")

# Create a frame to hold the resample label, entry, and slider
resample_frame = tk.Frame(window, bg='powder blue')
resample_frame.pack(pady=2)

# Add a label for resample
resample_label = tk.Label(resample_frame, text="                  SIZE", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
resample_label.config(justify="right")
resample_label.grid(row=0, column=0, sticky="e")

# Add an entry for resample
resample_value_entry = tk.Entry(resample_frame, textvariable=resample_value, highlightthickness=0, bg='powder blue', relief='flat', font=('TkDefaultFont', 9, 'bold'))
resample_label.config(justify="left")
resample_value_entry.grid(row=0, column=1, sticky="w")

# Add a label for resample
resample_label = tk.Label(resample_frame, text="X                      ", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
resample_label.config(justify="center")
resample_label.grid(row=0, column=1)

# Add the slider 
resample_slider = ttk.Scale(window, from_=0.1, to=8, length=125, style="blue.Horizontal.TScale", command=lambda value: resample_value.set("{:.2f}".format(float(value))))  # Use the ttk.Scale widget1 with the custom style
resample_slider.set(1)
resample_slider.pack(pady=2)

# Function to update the slider when return is pressed in the entry
def update_slider(event):
    new_value = float(resample_value_entry.get())
    resample_slider.set(new_value)

# Bind the return key to the update_slider function
resample_value_entry.bind('<Return>', update_slider)

# Create a frame to hold the colors label, entry, and slider
colors_frame = tk.Frame(window, bg='powder blue')
colors_frame.pack(pady=2)

# Create a StringVar to hold the resample value
colors_value = tk.StringVar()
colors_value.set("256")

# Add a label and slider for colors
colors_label = tk.Label(colors_frame, text="                 COLORS", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
colors_label.config(justify="right")
colors_label.grid(row=0, column=0, pady=0)
colors_value_entry = tk.Entry(colors_frame, textvariable=colors_value, bg='powder blue', highlightthickness=0, border=0, relief='flat', font=('TkDefaultFont', 9, 'bold'))
colors_value_entry.grid(row=0, column=1)

colors_slider = ttk.Scale(window, from_=1, to=256, length=125, style="blue.Horizontal.TScale", command=lambda value: colors_value.set("{:.0f}".format(float(value)))) # fix with (int(colors))
colors_slider.set(256)
colors_slider.pack(pady=2)

# Function to update the slider when return is pressed in the entry
def update_slider(event):
    new_value = int(colors_value_entry.get())
    colors_slider.set(new_value)

# Bind the return key to the update_slider function
colors_value_entry.bind('<Return>', update_slider)

# Create a BooleanVar to hold the state of the checkbutton
open_gif = tk.BooleanVar()
open_gif.set(False)  # Set the initial state to False

# Add a checkbutton for opening the GIF
open_gif_checkbutton = tk.Checkbutton(window, text=" OPEN IT", variable=open_gif, bg='powder blue', highlightthickness=0, selectcolor='powder blue', activebackground='powder blue', relief='flat', font=('TkDefaultFont', 9, 'bold'))
open_gif_checkbutton.pack(ipady=0)

# Add a frame for the widgets
widget_frame = tk.Frame(window, bg='powder blue')
widget_frame.pack(pady=5)

# Add a label for dithering method
dither_methods = ['DITHER OPTIONS', '      NONE       ', '     ORDERED     ', '    RASTERIZE    ', 'FLOYDSTEINBERG']
dither_method_var = tk.StringVar(value=dither_methods[0])
dither_method_label = tk.Label(widget_frame, textvariable=dither_method_var, bg='pale turquoise', relief='raised', font=('TkDefaultFont', 9, 'bold'))
dither_method_label.grid(row=0, column=0, ipadx=15, ipady=5)

# Add a menu for selecting the dithering method
dither_method_menu = tk.Menu(window, tearoff=0)
for method in dither_methods:
    dither_method_menu.add_command(label=method, command=lambda m=method: dither_method_var.set(m))

# Bind a click event to the label to show the menu
def show_menu(event):
    dither_method_menu.post(event.x_root, event.y_root)
dither_method_label.bind("<Button-1>", show_menu)

# Add a button to choose the folder
photo3 = tk.PhotoImage(file="GIF_IT_UP.png")
choose_folder_button = tk.Button(window, text="GIF IT UP", command=create_gif, border=2, bg='powder blue', image = photo3, relief='raised')
choose_folder_button.pack(pady=5)

# Add drag and drop functionality to the button
choose_folder_button.drop_target_register('DND_Files')
choose_folder_button.dnd_bind('<<Drop>>', drop)

# Add a progress bar
style = ttk.Style()
style.theme_use('clam')
style.configure("bar.Horizontal.TProgressbar", troughcolor ='powder blue', background ='red', bordercolor='powder blue')
progress_bar = ttk.Progressbar(window, mode="determinate", maximum=100, style="bar.Horizontal.TProgressbar")
progress_bar.pack()
progress_label = tk.Label(window, text="", bg='powder blue')
progress_label.pack()

# Add a status label
status_label = tk.Label(window, text="", bg='powder blue')
status_label.pack(pady=2.5)

# Add a credit label
credit_label = tk.Label(window, text="Code by C1t1zen & CodeGPT", bg='powder blue')
credit_label.pack(pady=2.5)

# Start the GUI event loop
window.mainloop()
