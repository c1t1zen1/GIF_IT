import os
from PIL import Image, ImageSequence
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import TkinterDnD
from PIL import ImageFont, ImageDraw
from tkinter import font as tkFont

# Constants for file extensions and dithering methods
FILE_EXTENSIONS = (".png", ".jpg", ".jpeg")
DITHER_METHODS = ['DITHER OPTIONS', 'NONE', '8-BIT', 'ORDERED', 'RASTERIZE', 'FLOYDSTEINBERG']
DITHER_DICT = {
    'DITHER OPTIONS': None,
    'NONE': None,
    '8-BIT': Image.NONE,
    'ORDERED': Image.ORDERED,
    'RASTERIZE': Image.RASTERIZE,
    'FLOYDSTEINBERG': Image.FLOYDSTEINBERG
}

# Function to load images from a folder, resample them, limit the number of colors, and convert them to RGBA mode
def load_images_from_folder(folder_path, resample, colors):
    images = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(FILE_EXTENSIONS):
            image_path = os.path.join(folder_path, filename)
            try:
                image = Image.open(image_path)
            except IOError:
                print(f"Unable to open image file {image_path}. Skipping.")
                continue
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
    return images

# Function to create a gif from images, add dissolve effect between each image, apply dithering method, and save images as GIF
def create_gif_from_images(images, output_folder, output_name, speed=100, dissolve=0, resample=1, colors=256, dither=None, watermark_text=None, watermark_font=None, watermark_size=None, watermark_location=None):
    # Add dissolve effect between each image
    dissolved_images = []
    for image_index in range(len(images) - 1):
        for dissolve_index in range(dissolve):
            alpha = dissolve_index / dissolve
            blend = Image.blend(images[image_index], images[image_index+1], alpha)
            dissolved_images.append(blend)
    dissolved_images.append(images[-1])

    # Apply dithering method
    if dither and dither != 'None' and dither != 'Dither Options':
        dither = DITHER_DICT[dither]
        dissolved_images = [image.convert('P', dither=dither) for image in dissolved_images]

    # Add watermark to each image
    if watermark_text:
        watermark_font = ImageFont.truetype(watermark_font, watermark_size)
        draw = ImageDraw.Draw(image)
        text_width, text_height = draw.textsize(watermark_text, font=watermark_font)
        if watermark_location == "TOP":
            position = (image.width - text_width) / 2, 0
        elif watermark_location == "CENTER":
            position = (image.width - text_width) / 2, (image.height - text_height) / 2
        else:  # BOTTOM
            position = (image.width - text_width) / 2, image.height - text_height
        draw.text(position, watermark_text, font=watermark_font, fill="white")

    # Save images as GIF
    if not output_name:
        output_name = os.path.basename(output_folder)
    output_path = os.path.join(output_folder, output_name + '.gif')
    try:
        dissolved_images[0].save(output_path,
                   save_all=True,
                   append_images=dissolved_images[1:],
                   duration=speed,
                   loop=0)
    except IOError:
        print(f"Unable to save GIF file {output_path}.")

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
        dither = dither_method_var.get()
        watermark_text = watermark_entry.get()
        watermark_font = font_var.get()
        watermark_size = int(font_size_entry.get())
        watermark_location = location_var.get()
        total_images = len([name for name in os.listdir(folder_path) if (name.endswith('.png') or name.endswith('.jpg') or name.endswith('.jpeg'))])
        progress_bar['maximum'] = total_images
        progress_bar['value'] = 0
        progress_label.config(text="0%")
        for i, filename in enumerate(sorted(os.listdir(folder_path))):
            if filename.endswith(FILE_EXTENSIONS):
                image_path = os.path.join(folder_path, filename)
                image = Image.open(image_path)
                images.append(image)
                progress_bar['value'] = i + 1
                progress = (i + 1) / total_images * 99
                progress_label.config(text="%.0f%%" % progress)
                window.update_idletasks()
        output_folder = os.path.dirname(folder_path)
        create_gif_from_images(images, output_folder, output_name, gif_speed, dissolve, resample, colors, dither, watermark_text, watermark_font, watermark_size, watermark_location)
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
window.geometry("225x750")
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
output_name_label = tk.Label(window, text="NAME IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
output_name_label.pack(pady=2)
output_name_entry = tk.Entry(window)
output_name_entry.insert(tk.END, "")
output_name_entry.config(justify="center", validate='all')
output_name_entry.pack()
output_name_entry.focus()

# Add a label and entry for watermark text
watermark_label = tk.Label(window, text="WATERMARK IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
watermark_label.pack(pady=2)
watermark_entry = tk.Entry(window)
watermark_entry.insert(tk.END, "")
watermark_entry.config(justify="center")
watermark_entry.pack()

# Add a label and option menu for font selection
font_label = tk.Label(window, text="FONT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
font_label.pack(pady=2)
font_var = tk.StringVar()
font_var.set(tkFont.families()[0])  # set the default option
font_option = tk.OptionMenu(window, font_var, *tkFont.families())
font_option.pack()

# Add a label and entry for font size
font_size_label = tk.Label(window, text="FONT SIZE", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
font_size_label.pack(pady=2)
font_size_entry = tk.Entry(window)
font_size_entry.insert(tk.END, "20")
font_size_entry.config(justify="center")
font_size_entry.pack()

# Add a label and option menu for watermark location
location_label = tk.Label(window, text="LOCATION", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
location_label.pack(pady=2)
location_var = tk.StringVar()
location_var.set("CENTER")  # set the default option
location_option = tk.OptionMenu(window, location_var, "TOP", "CENTER", "BOTTOM")
location_option.pack()

# Create a style
style = ttk.Style()
style.configure("blue.Horizontal.TScale", foreground='#B0E0E6', background='#B0E0E6', troughcolor='#B0E0E6', slidercolor='#B0E0E6')

# Function to update the label of a scale widgets
def update_scale_label1(label, value):
    label.config(text="{:.1f}".format(float(value)))

def update_scale_label2(label, value):
    label.config(text="{}".format(int(value)))

# Add a label and slider for resample
resample_label = tk.Label(window, text="SIZE IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
resample_label.pack(pady=0)
resample_value_label = tk.Label(window, text="1.0", bg='powder blue')
resample_value_label.pack()
resample_slider = ttk.Scale(window, from_=0.1, to=10, length=125, style="blue.Horizontal.TScale", command=lambda value: update_scale_label1(resample_value_label, value))  # Use the ttk.Scale widget1 with the custom style
resample_slider.set(1)
resample_slider.pack()

# Add a label and slider for colors
colors_label = tk.Label(window, text="COLOR IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
colors_label.pack(pady=0)
colors_value_label = tk.Label(window, text="256", bg='powder blue')
colors_value_label.pack()
colors_slider = ttk.Scale(window, from_=1, to=256, length=125, command=lambda value: update_scale_label2(colors_value_label, int(float(value))))
colors_slider.set(256)
colors_slider.pack()

# Add a label and entry for gif speed
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
dither_method_var = tk.StringVar(value=DITHER_METHODS[0])
dither_method_label = tk.Label(widget_frame, textvariable=dither_method_var, bg='pale turquoise', relief='raised', font=('TkDefaultFont', 9, 'bold'))
dither_method_label.grid(row=0, column=0, ipadx=15, ipady=5)

# Add a menu for selecting the dithering method
dither_method_menu = tk.Menu(window, tearoff=0)
for method in DITHER_METHODS:
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
