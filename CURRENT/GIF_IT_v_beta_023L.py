import os
from PIL import Image, ImageSequence
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import TkinterDnD

# Function to create a GIF from a folder of images
def create_gif_from_images(folder_path, output_folder, output_name, speed=100):
    images = []

    # Load images from the folder
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
            image_path = os.path.join(folder_path, filename)
            image = Image.open(image_path)

            # Apply dithering based on the selected option
            dither_method = dither_method_var.get()
            if dither_method == 'DITHER OPTIONS':
                images.append(image)
            elif dither_method == 'NONE':
                images.append(image)
            elif dither_method == 'FLOYDSTEINBERG':
                image = image.convert('P', dither=Image.FLOYDSTEINBERG)
            elif dither_method == 'RATERIZE':
                image = image.convert('P', dither=Image.RATERIZE)
            elif dither_method == 'ORDERED':
                image = image.convert('P', dither=Image.ORDERED)
            elif dither_method == '8-BIT':
                image = image.convert('P', dither=Image.NONE)

            images.append(image)

    # Save images as GIF
    if not output_name:
        output_name = os.path.basename(folder_path)
    output_path = os.path.join(output_folder, output_name + '.gif')
    images[0].save(output_path,
                   save_all=True,
                   append_images=images[1:],
                   duration=speed,
                   loop=0)

# Function to handle button click event
def create_gif(folder_path=None):
    status_label.config(text="Creating GIF...")
    images = []
    if not folder_path:
        folder_path = filedialog.askdirectory(title="Select Image Folder")
    if folder_path:
        output_name = output_name_entry.get()
        gif_speed = int(speed_entry.get())
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
        create_gif_from_images(folder_path, output_folder, output_name, gif_speed)
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
icon = tk.PhotoImage(master=window, file='/home/debian/code/icon_16.png')
window.wm_iconphoto(True, icon)
window.resizable(width=False, height=False)
window.geometry("+300+300")  # set position on the screen
window.geometry("225x400")
window.configure(bg='powder blue')
window.title("GIF IT")

# Add a label for formats
top_label = tk.Label(window, text="", bg='powder blue', borderwidth=0)
image = tk.PhotoImage(file="/home/debian/code/GIF_IT.png", width=200, height=100)
image_label = tk.Label(top_label, image=image)
top_label.pack(padx=0, pady=0)
image_label.configure(borderwidth=0, highlightthickness=0)
image_label.pack(padx=5, pady=5)

# Add a label and entry for output name
photo1 = tk.PhotoImage(file="/home/debian/code/NAME_IT.png")
output_name_label = tk.Label(window, text="NAME IT:", bg='powder blue', image = photo1)
output_name_label.pack(pady=2.5)
output_name_entry = tk.Entry(window)
output_name_entry.insert(tk.END, "")
output_name_entry.config(justify="center", validate='all')
output_name_entry.pack()
output_name_entry.focus()

# Add a label and entry for gif speed
photo2 = tk.PhotoImage(file="/home/debian/code/TIME_IT.png")
speed_label = tk.Label(window, text="TIME IT", bg='powder blue', image = photo2)
speed_label.pack(pady=2.5)
speed_entry = tk.Entry(window)
speed_entry.insert(tk.END, "100")
speed_entry.config(justify="center")
speed_entry.pack()

# Add a frame for the widgets
widget_frame = tk.Frame(window, bg='powder blue')
widget_frame.pack(pady=15)

# Add a label for dithering method
dither_methods = [' DITHER OPTIONS ', '          NONE           ', '           8-BIT           ', '       ORDERED       ', '      RASTERIZE      ', 'FLOYDSTEINBERG']
dither_method_var = tk.StringVar(value=dither_methods[0])
dither_method_label = tk.Label(widget_frame, textvariable=dither_method_var, bg='pale turquoise', relief='raised')
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
photo3 = tk.PhotoImage(file="/home/debian/code/GIF_IT_UP.png")
choose_folder_button = tk.Button(window, text="GIF IT UP", command=create_gif, border=2, bg='powder blue', image = photo3, relief='raised')
choose_folder_button.pack(pady=0)

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
