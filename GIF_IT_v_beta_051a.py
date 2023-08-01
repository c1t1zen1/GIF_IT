import os
from PIL import Image, ImageSequence
import tkinter as tk
from tkinter import filedialog, ttk
from tkinterdnd2 import TkinterDnD
import math
from PIL import ImageFont, ImageDraw

# Constants for file extensions and dithering methods
FILE_EXTENSIONS = (".png", ".jpg", ".jpeg")

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

def create_watermark_image(text, font_name, font_size, position):
    # Create a new image with mode 'RGBA' for transparency and size large enough for the text
    watermark_image = Image.new('RGBA', (500, 500))

    # Create a Draw object
    draw = ImageDraw.Draw(watermark_image)

    # Load the font
    font = ImageFont.truetype(font_name, font_size)

    # Get the width and height of the text
    text_width, text_height = draw.textsize(text, font)

    # Calculate the x and y coordinates for the text
    if position == 'top':
        x = (watermark_image.width - text_width) / 2
        y = 0
    elif position == 'center':
        x = (watermark_image.width - text_width) / 2
        y = (watermark_image.height - text_height) / 2
    elif position == 'bottom':
        x = (watermark_image.width - text_width) / 2
        y = watermark_image.height - text_height

    # Draw the text with a bold outline
    draw.text((x-2, y), text, fill='black', font=font)
    draw.text((x+2, y), text, fill='black', font=font)
    draw.text((x, y-2), text, fill='black', font=font)
    draw.text((x, y+2), text, fill='black', font=font)

    # Draw the text
    draw.text((x, y), text, fill='white', font=font)

    # Make the image semi-transparent
    watermark_image = watermark_image.point(lambda p: p * 0.7)

    return watermark_image

def apply_watermark(images, watermark_image):
    # Create a new list to hold the watermarked images
    watermarked_images = []

    # Loop over each image
    for image in images:
        # Convert the image to 'RGBA' mode to handle transparency
        image = image.convert('RGBA')

        # Paste the watermark image onto the original image
        image.paste(watermark_image, (0, 0), watermark_image)

        # Add the watermarked image to the list
        watermarked_images.append(image)

    return watermarked_images

def create_gif_from_images(images, output_folder, output_name, speed, dissolve, resample, colors, watermark_text, watermark_font, watermark_size, watermark_location):
    # Convert images to RGB
    images = [image.convert('RGB') if image.mode != 'RGB' else image for image in images]

    # Add dissolve effect between each image
    dissolved_images = []
    for i in range(len(images) - 1):
        for j in range(dissolve):
            alpha = j / dissolve
            blend = Image.blend(images[i], images[i+1], alpha)
            dissolved_images.append(blend)
    dissolved_images.append(images[-1])

    # Apply dithering based on the selected option       
    dither_method = dither_method_var.get()
    
    if dither_method == 'NO DITHER':
        dissolved_images = [img.convert('P', dither=Image.NONE) for img in dissolved_images]
    elif dither_method == 'ORDERED':
        dissolved_images = [img.convert('P', dither=Image.ORDERED) for img in dissolved_images]
    elif dither_method == 'RASTERIZE':
        dissolved_images = [img.convert('P', dither=Image.RASTERIZE) for img in dissolved_images]
    elif dither_method == 'FLOYDSTEINBERG':
        dissolved_images = [img.convert('P', dither=Image.FLOYDSTEINBERG) for img in dissolved_images]
        
    # Add watermark to each image
    for i in range(len(dissolved_images)):
        image = dissolved_images[i]
        watermark_image = Image.new('RGB', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_image)
        font_path = "C:/Windows/Fonts/impact.ttf"
        font = ImageFont.truetype(font_path, watermark_size)
        text_width, text_height = draw.textsize(watermark_text, font)
        if watermark_location == 'Top':
            position = (image.width//2 - text_width//2, 10)
        elif watermark_location == 'Center':
            position = (image.width//2 - text_width//2, image.height//2 - text_height//2)
        else:  # Bottom
            position = (image.width//2 - text_width//2, image.height - text_height - 10)
        draw.text(position, watermark_text, font=font, fill=(255, 255, 255, 128))
        dissolved_images[i] = Image.alpha_composite(image, watermark_image)

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
        watermark_text = watermark_text_entry.get()
        watermark_font = watermark_font_var.get()
        watermark_size = watermark_size_slider.get()
        watermark_location = watermark_location_var.get()
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
        output_path = os.path.join(output_folder, output_name + '.gif')
        create_gif_from_images(images, output_folder, output_name, gif_speed, dissolve, resample, colors, watermark_text, watermark_font, watermark_size, watermark_location)
        status_label.config(text="Great Success!")
        progress_bar['value'] = 100
        progress_label.config(text="100%")
        # Open the GIF file immediately if the checkbutton is selected
        if open_gif.get():
            if os.name == 'nt':  # Windows
                os.startfile(output_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open', output_path])

        # Progress bar reset
        def reset_progress():
            progress_bar['value'] = 0
            progress_label.config(text="")

        create_gif_from_images(images, output_folder, output_name, folder_path, gif_speed, dissolve, resample, colors)
        status_label.config(text="Great Success!")
        progress_bar['value'] = 100
        progress_label.config(text="100%")

        # Schedule reset_progress to run after 12000 milliseconds (12 seconds)
        window.after(12000, reset_progress)

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
window.geometry("+400+200")  # set position on the screen
window.geometry("225x710")
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
output_name_entry = tk.Entry(window, relief='sunken')
output_name_entry.insert(tk.END, "")
output_name_entry.config(justify="center", validate='all', bg='powder blue')
output_name_entry.pack()
output_name_entry.focus()

# Add a label and entry for gif speed
speed_label = tk.Label(window, text="TIME IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
speed_label.pack(pady=2)
speed_entry = tk.Entry(window, relief='sunken')
speed_entry.insert(tk.END, "100")
speed_entry.config(justify="center", bg='powder blue')
speed_entry.pack()

# Add a label and entry for dissolve effect
dissolve_label = tk.Label(window, text="DISSOLVE IT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
dissolve_label.pack(pady=2)
dissolve_entry = tk.Entry(window, relief='sunken')
dissolve_entry.insert(tk.END, "0")
dissolve_entry.config(justify="center", bg='powder blue')
dissolve_entry.pack()

# Create a style
style = ttk.Style()
style.theme_use('clam')
style.configure("blue.Horizontal.TScale", background='#B0E0E6', troughcolor='#B0E0E6', bordercolor='#B9E6E9')

# Create a StringVar to hold the resample value
resample_value = tk.StringVar()
resample_value.set("1.0")

# Create a frame to hold the resample label, entry, and slider
resample_frame = tk.Frame(window, bg='powder blue')
resample_frame.pack()

# Add a label for resample
resample_label = tk.Label(resample_frame, text="SIZE", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
resample_label.config(justify="right")
resample_label.grid(row=0, column=0, sticky="e")

# Add an entry for resample
resample_value_entry = tk.Entry(resample_frame, textvariable=resample_value, width=5, bg='powder blue', relief='flat', font=('TkDefaultFont', 9, 'bold'))
resample_label.config(justify="center")
resample_value_entry.grid(row=0, column=1, sticky="w")

# Add a label for resample
resample_label = tk.Label(resample_frame, text="X", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
resample_label.config(justify="left")
resample_label.grid(row=0, column=1, sticky="n")

# Define the minimum and maximum values for the logarithmic scale
min_value = 0.1
max_value = 10

# Function to convert the slider value to a logarithmic scale
def convert_to_log(value):
    return min_value * math.pow(max_value / min_value, float(value))

# Function to convert the logarithmic scale value back to the slider value
def convert_from_log(value):
    return math.log(float(value) / min_value, max_value / min_value)

# Add the slider with a logarithmic scale
resample_slider = ttk.Scale(resample_frame, from_=convert_from_log(min_value), to=convert_from_log(max_value),
                            length=125, style="blue.Horizontal.TScale",
                            command=lambda value: resample_value.set("{:.2f}".format(convert_to_log(float(value)))))
resample_slider.set(convert_from_log(1))  # Set the initial value on the logarithmic scale
resample_slider.grid(row=1, column=0, columnspan=2)  # Make the slider span 2 columns

# Function to update the slider when return is pressed in the entry
def update_slider(event):
    new_value = float(resample_value_entry.get())
    resample_slider.set(convert_from_log(new_value))

# Bind the return key to the update_slider function
resample_value_entry.bind('<Return>', update_slider)
# Create a frame to hold the colors label, entry, and slider
colors_frame = tk.Frame(window, bg='powder blue')
colors_frame.pack()

# Add an entry for colors
colors_value_entry = tk.Entry(colors_frame, width=5, bg='powder blue', relief='flat', font=('TkDefaultFont', 9, 'bold'))
colors_value_entry.grid(row=0, column=0, sticky="e")
colors_value_entry.config(justify="right")
colors_value_entry.insert(0, "256")  # Default value

# Add a label for colors
colors_label = tk.Label(colors_frame, text="COLORS", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
colors_label.grid(row=0, column=1, sticky="w")

# Add a slider for colors
colors_slider = ttk.Scale(colors_frame, from_=1, to=256, length=125, style="blue.Horizontal.TScale", command=lambda value: colors_value_entry.delete(0, 'end') or colors_value_entry.insert(0, str(int(float(value)))))  # Use the ttk.Scale widget
colors_slider.set(256)
colors_slider.grid(row=1, column=0, columnspan=2) 

# Function to update the slider when return is pressed in the entry
def update_slider(event):
    new_value = int(colors_value_entry.get())
    colors_slider.set(new_value)

# Bind the return key to the update_slider function
colors_value_entry.bind('<Return>', update_slider)

# Add a frame for the widgets
widget_frame = tk.Frame(window, bg='powder blue')
widget_frame.pack(pady=5)

# Add a label for dithering method
DITHER_METHODS = ['     NO DITHER     ', '     ORDERED     ', '    RASTERIZE    ', 'FLOYDSTEINBERG']
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

# Create a BooleanVar to hold the state of the checkbutton
open_gif = tk.BooleanVar()
open_gif.set(False)  # Set the initial state to False

# Add a checkbutton for opening the GIF
open_gif_checkbutton = tk.Checkbutton(window, text=" OPEN IT", variable=open_gif, bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
open_gif_checkbutton.pack(ipady=5)

# Add a label and entry for watermark text
watermark_text_label = tk.Label(window, text="WATERMARK TEXT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
watermark_text_label.pack(pady=2)
watermark_text_entry = tk.Entry(window, bg='powder blue')
watermark_text_entry.pack()

# Add a label and dropdown for watermark font
watermark_font_label = tk.Label(window, text="WATERMARK FONT", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
watermark_font_label.pack(pady=2)
watermark_font_var = tk.StringVar(window)
watermark_font_var.set("Arial")  # default value
watermark_font_dropdown = tk.OptionMenu(window, watermark_font_var, "impact.ttf", "Helvetica.ttf", "Times New Roman")
watermark_font_dropdown.pack()

# Add a label and slider for watermark size
watermark_size_label = tk.Label(window, text="WATERMARK SIZE", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
watermark_size_label.pack(pady=2)
watermark_size_slider = tk.Scale(window, from_=10, to=100, orient=tk.HORIZONTAL, length=125, bg='powder blue')
watermark_size_slider.set(50)
watermark_size_slider.pack()

# Add a label and dropdown for watermark location
watermark_location_label = tk.Label(window, text="WATERMARK LOCATION", bg='powder blue', font=('TkDefaultFont', 9, 'bold'))
watermark_location_label.pack(pady=2)
watermark_location_var = tk.StringVar(window)
watermark_location_var.set("Center")  # default value
watermark_location_dropdown = tk.OptionMenu(window, watermark_location_var, "Top", "Center", "Bottom")
watermark_location_dropdown.pack()

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
status_label.pack(pady=2)

# Add a credit label
credit_label = tk.Label(window, text="Code by C1t1zen & CodeGPT", bg='powder blue')
credit_label.pack(pady=2)

# Start the GUI event loop
window.mainloop()
