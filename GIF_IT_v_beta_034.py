import os
from PIL import Image, ImageSequence
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import TkinterDnD

# Function to create a GIF from a folder of images
def create_gif_from_images(folder_path, output_folder, output_name, speed=100, dissolve=0, resample=1, colors=256):
    images = []

    # Load images from the folder
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
            image_path = os.path.join(folder_path, filename)
            image = Image.open(image_path)

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
    
    # Add dissolve effect between each image
    dissolved_images = []
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
        dissolve = int(dissolve_entry.get())
        resample = float(resample_value_label.cget("text"))
        colors = int(colors_value_label.cget("text"))
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
window.iconbitmap('GIF_IT_ICON2.ico')
window.resizable(width=False, height=False)
window.geometry("+300+300")  # set position on the screen
window.geometry("225x625")
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
output_name_entry = tk.Entry(window)
output_name_entry.insert(tk.END, "")
output_name_entry.config(justify="center", validate='all')
output_name_entry.pack()
output_name_entry.focus()

# Function to update the label of a custom slider
def update_slider_label(label, value, scale):
    value = round(scale * value, 1) if scale == 10 else int(scale * value)
    label.config(text=str(value))

# Function to create a custom slider
def create_custom_slider(text, from_, to, initial):
    scale = to - from_
    label = tk.Label(window, text=text, bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
    label.pack()
    value_label = tk.Label(window, text=str(initial), bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
    value_label.pack()
    canvas = tk.Canvas(window, width=200, height=50, bg='powder blue', highlightthickness=0)
    canvas.pack()
    line = canvas.create_line(50, 25, 150, 25)
    circle = canvas.create_oval(45 + 100 * (initial - from_) / scale, 20, 55 + 100 * (initial - from_) / scale, 30, fill='black')
    def update_circle(event):
        x = event.x
        if 50 <= x <= 150:
            canvas.coords(circle, x-5, 20, x+5, 30)
            update_slider_label(value_label, (x - 50) / 100, scale)
    canvas.bind("<B1-Motion>", update_circle)
    return value_label

# Add a label and custom slider for resample
resample_value_label = create_custom_slider("RESIZE IT", 0.1, 10, 1)

# Add a label and custom slider for colors
colors_value_label = create_custom_slider("COLOR IT", 1, 256, 256)

# Add a label and entry for gif speed
# photo2 = tk.PhotoImage(file="TIME_IT.png")
speed_label = tk.Label(window, text="TIME IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
speed_label.pack(pady=2)
speed_entry = tk.Entry(window)
speed_entry.insert(tk.END, "100")
speed_entry.config(justify="center")
speed_entry.pack()

# Add a label and entry for dissolve effect
dissolve_label = tk.Label(window, text="DISSOLVE IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
dissolve_label.pack(pady=2)
dissolve_entry = tk.Entry(window)
dissolve_entry.insert(tk.END, "0")
dissolve_entry.config(justify="center")
dissolve_entry.pack()

# Add a frame for the widgets
widget_frame = tk.Frame(window, bg='powder blue')
widget_frame.pack(pady=15)

# Add a label for dithering method
dither_methods = ['DITHER OPTIONS', '      NONE       ', '       8-BIT       ', '     ORDERED     ', '    RASTERIZE    ', 'FLOYDSTEINBERG']
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
