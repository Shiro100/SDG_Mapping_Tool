import re
import os
import PyPDF2
import customtkinter as ctk
from tkinter import filedialog, messagebox, Frame, Label, Button, PhotoImage
from PIL import Image, ImageTk
import pywinstyles
from customtkinter import CTkImage
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

SDG_KEYWORDS_FOLDER = "SDG Keywords"
RESIZE_DELAY = 200  #Delay in milliseconds
multiple_window = None #Track the multiple mode window instance

#load SDG keywords
def load_sdg_keywords():
    sdg_keywords = {}
    for i in range(1, 18):  
        file_path = os.path.join(SDG_KEYWORDS_FOLDER, f"SDG{i:02}.txt")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                keywords = [line.strip().strip('",').lower() for line in f if line.strip()]
                sdg_keywords[i] = keywords
    return sdg_keywords

sdg_keywords = load_sdg_keywords()

#extract Abstract from PDF
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            title = os.path.splitext(os.path.basename(file_path))[0]
            return title, text.lower()
    except Exception as e:
        return "Error in extracting text", f"Failed to read PDF: {str(e)}"

#SDG Analysis
def process_sdg_analysis(text):
    if not text.strip():
        messagebox.showwarning("Input Error", "No text found for analysis.")
        return
    
    text = re.sub(r'\s+', ' ', text)
    sdg_counts = {sdg: 0 for sdg in sdg_keywords.keys()}

    for sdg, keyword_list in sdg_keywords.items():
        for keyword in keyword_list:
            pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
            matches = pattern.findall(text)
            if matches:
                sdg_counts[sdg] += len(matches)

    total_matches = sum(sdg_counts.values())
    if total_matches == 0:
        messagebox.showinfo("No SDGs Found", "No relevant SDG keywords detected.")
        return

    sdg_percentages = {sdg: (count / total_matches) * 100 for sdg, count in sdg_counts.items()}
    sorted_sdgs = sorted(sdg_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
    display_top_sdgs(sorted_sdgs)

#display top 3 SDGs
def display_top_sdgs(sorted_sdgs):
    for widget in sdg_frame.winfo_children():
        widget.destroy()

    frame_width = 500 # Adjust width as needed
    frame_height = 105 # Adjust height as needed

    for sdg, percentage in sorted_sdgs:
        frame = ctk.CTkFrame(sdg_frame, fg_color="white", width=frame_width, height=frame_height)
        frame.pack_propagate(False)  # Prevent automatic resizing
        frame.pack(pady=5)

        icon_path = sdg_keyword_group_logos.get(sdg)
        img = Image.open(icon_path).resize((100, 100), Image.Resampling.LANCZOS)
        img_photo = ImageTk.PhotoImage(img)

        icon_label = ctk.CTkLabel(frame, image=img_photo, text="")
        icon_label.image = img_photo
        icon_label.pack(side="left", padx=10)

        text_label = ctk.CTkLabel(frame, text=f"SDG {sdg} - {percentage:.1f}%", font=("Arial", 14, "bold"))
        text_label.pack(side="left", padx=10)

#upload PDF and Process
def upload_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        title, text = extract_text_from_pdf(file_path)
        title_entry.delete(0, "end")
        title_entry.insert(0, title)
        abstract_text.delete("1.0", "end")
        abstract_text.insert("1.0", text[:400])
        process_sdg_analysis(title + " " + text)

def update_bg_image(event=None):
    global bg_photo, bg_image
    bg_image = Image.open(r"assets\\SchoolBg\\Single.png").resize((root.winfo_width(), root.winfo_height()), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label.configure(image=bg_photo)

def delayed_update_bg():
    if hasattr(root, "resize_after_id"):
        root.after_cancel(root.resize_after_id)
    root.resize_after_id = root.after(RESIZE_DELAY, update_bg_image)

from functools import partial

def open_multiple_mode():
    global multiple_window

    if multiple_window and multiple_window.winfo_exists():
        multiple_window.lift()
        multiple_window.attributes("-topmost", True)
        return

    multiple_window = ctk.CTkToplevel(root)
    multiple_window.title("Multiple Mode")
    multiple_window.geometry("1280x720")
    multiple_window.resizable(False, False)
    multiple_window.attributes("-topmost", True)

    multiple_bg_image = CTkImage(light_image=Image.open(r"assets\\SchoolBg\\Multiple.png"), size=(1280, 720))
    multiple_bg_label = ctk.CTkLabel(multiple_window, image=multiple_bg_image, text="")
    multiple_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    title_entries = []
    abstract_texts = []
    sdg_frames = []

    def upload_pdf_multiple(index):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            title, text = extract_text_from_pdf(file_path)
            title_entries[index].delete(0, "end")
            title_entries[index].insert(0, title)
            abstract_texts[index].delete("1.0", "end")
            abstract_texts[index].insert("1.0", text[:400])  

    def submit_sdg_analysis(index):
        if index >= len(title_entries) or index >= len(abstract_texts) or index >= len(sdg_frames):
            messagebox.showerror("Index Error", "Invalid index for SDG analysis.")
            return

        text_content = title_entries[index].get() + " " + abstract_texts[index].get("1.0", "end-1c")
        text_content = re.sub(r'\s+', ' ', text_content)
        sdg_counts = {sdg: 0 for sdg in sdg_keywords.keys()}

        for sdg, keyword_list in sdg_keywords.items():
            for keyword in keyword_list:
                pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
                matches = pattern.findall(text_content)
                if matches:
                    sdg_counts[sdg] += len(matches)

        total_matches = sum(sdg_counts.values())

        if total_matches == 0:
            messagebox.showinfo("No SDGs Found", "No relevant SDG keywords detected.")
            return

        sdg_percentages = {sdg: (count / total_matches) * 100 for sdg, count in sdg_counts.items()}
        sorted_sdgs = sorted(sdg_percentages.items(), key=lambda x: x[1], reverse=True)[:3]

        display_top_sdgs_multiple(sorted_sdgs, sdg_frames[index])  

    def display_top_sdgs_multiple(sorted_sdgs, sdg_frame):
        for widget in sdg_frame.winfo_children():
            widget.destroy()
            
        scrollable_frame = ctk.CTkScrollableFrame(sdg_frame, width=320, height=180, fg_color="#FFF8DC", corner_radius=3)
        scrollable_frame.pack(expand=True, fill="both", padx=5, pady=5)

        frame_width = 380  
        frame_height = 70

        for sdg, percentage in sorted_sdgs:
            frame = ctk.CTkFrame(scrollable_frame, fg_color="white", width=frame_width, height=frame_height)
            frame.pack_propagate(False)  
            frame.pack(pady=3)

            icon_path = sdg_keyword_group_logos.get(sdg)
            img = Image.open(icon_path).resize((60, 60), Image.Resampling.LANCZOS)
            img_photo = ImageTk.PhotoImage(img)

            icon_label = ctk.CTkLabel(frame, image=img_photo, text="")
            icon_label.image = img_photo
            icon_label.pack(side="left", padx=10)

            text_label = ctk.CTkLabel(frame, text=f"SDG {sdg} - {percentage:.1f}%", font=("Arial", 14, "bold"))
            text_label.pack(side="left", padx=10)

        return scrollable_frame

    for i in range(3):
        x_offset = 50 + (i * 420)  

        title_entry = ctk.CTkEntry(multiple_window, width=350, height=40, 
                                   fg_color="#FFF8DC", 
                                   bg_color="#000001",
                                   border_color="#FFD700",
                                   border_width=2,
                                   corner_radius=5,
                                   text_color="black",
                                   font=("Helvetica", 13))
        title_entry.place(x=x_offset, y=115)
        pywinstyles.set_opacity(title_entry, color="#000001")

        abstract_text = ctk.CTkTextbox(multiple_window, width=350, height=220, 
                                       fg_color="#FFF8DC",
                                       bg_color="#000001",
                                       border_color="#FFD700",
                                       border_width=2,
                                       corner_radius=5,
                                       text_color="black",
                                       font=("Helvetica", 13))
        abstract_text.place(x=x_offset, y=167)
        pywinstyles.set_opacity(abstract_text, color="#000001")

        sdg_frame = ctk.CTkFrame(multiple_window, width=350, height=218,
                                 fg_color="#FFF8DC",
                                 bg_color="#000001",
                                 border_color="#FFD700",
                                 border_width=2,
                                 corner_radius=5)
        sdg_frame.place(x=x_offset, y=400)
        pywinstyles.set_opacity(sdg_frame, color="#000001")

        # Store widgets correctly (fixed issue of double appends)
        title_entries.append(title_entry)
        abstract_texts.append(abstract_text)
        sdg_frames.append(sdg_frame)

        # Fix button command binding
        upload_button = ctk.CTkButton(multiple_window, text="Upload PDF", width=120, 
                                      fg_color="#FFD700", text_color="black", bg_color="#000001", 
                                      command=partial(upload_pdf_multiple, i))
        upload_button.place(x=x_offset, y=630)
        pywinstyles.set_opacity(upload_button, color="#000001")

        submit_button = ctk.CTkButton(multiple_window, text="Submit", width=120, 
                                      fg_color="#FFD700", text_color="black", bg_color="#000001", 
                                      command=partial(submit_sdg_analysis, i))
        submit_button.place(x=x_offset + 230, y=630)
        pywinstyles.set_opacity(submit_button, color="#000001")

    footer_frame = Frame(multiple_window, bg="#333333", height=40)
    footer_frame.pack(side="bottom", fill="x")
    Label(footer_frame, text="Developed by Group GUI 2025", font=("Helvetica", 10), bg="#333333", fg="white").pack(pady=10)

    multiple_window.protocol("WM_DELETE_WINDOW", lambda: close_multiple_mode())

#close the Multiple Mode Window
def close_multiple_mode():
    global multiple_window
    multiple_window.destroy()
    multiple_window = None  #Reset the variable

#mainframe (GUI Initialization)
ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title("SDG Mapping Tool")
root.geometry("1280x720")
root.resizable(False, False)
root.bind("<Configure>", update_bg_image)
root.bind("<Configure>", lambda event: delayed_update_bg())

def display_pie_chart(sdg_percentages, piechart_frame):
    # Clear previous content in the pie chart frame
    for widget in piechart_frame.winfo_children():
        widget.destroy()

    # Create a scrollable frame inside the pie chart frame for consistency
    scrollable_pie_frame = ctk.CTkScrollableFrame(piechart_frame, width=370, height=340, fg_color="#FFF8DC", corner_radius=3)
    scrollable_pie_frame.pack(expand=True, fill="both", padx=5, pady=5)

    # Create a frame to hold the pie chart (matching SDG frame style)
    frame_width = 340
    frame_height = 340  # Adjusted for pie chart display
    pie_frame = ctk.CTkFrame(scrollable_pie_frame, fg_color="white", width=frame_width, height=frame_height)
    pie_frame.pack_propagate(False)
    pie_frame.pack(pady=3, padx=5, fill="x")

    # Create figure and axis for pie chart
    fig, ax = plt.subplots(figsize=(4.5, 4.5))  # Slightly reduced for better UI fitting

    # Extract labels and values for the pie chart
    labels = [f"SDG {sdg}" for sdg in sdg_percentages.keys()]
    sizes = list(sdg_percentages.values())

    # Plot the pie chart
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Embed the pie chart in the Tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=pie_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill='both')

    return scrollable_pie_frame  # Return for consistency with other UI elements

def upload_pdf_mapping(title_entry, abstract_text):
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        title, text = extract_text_from_pdf(file_path)
        title_entry.delete(0, "end")
        title_entry.insert(0, title)
        abstract_text.delete("1.0", "end")
        abstract_text.insert("1.0", text[:400])  # Display part of the text

def process_sdg_analysis_mapping(title_entry, abstract_text, sdg_frame, piechart_frame):
    text_content = title_entry.get() + " " + abstract_text.get("1.0", "end-1c")
    if not text_content.strip():
        messagebox.showwarning("Input Error", "No text found for analysis.")
        return

    text_content = re.sub(r'\s+', ' ', text_content)
    sdg_counts = {sdg: 0 for sdg in sdg_keywords.keys()}

    for sdg, keyword_list in sdg_keywords.items():
        for keyword in keyword_list:
            pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
            matches = pattern.findall(text_content)
            if matches:
                sdg_counts[sdg] += len(matches)

    total_matches = sum(sdg_counts.values())
    if total_matches == 0:
        messagebox.showinfo("No SDGs Found", "No relevant SDG keywords detected.")
        return

    sdg_percentages = {sdg: (count / total_matches) * 100 for sdg, count in sdg_counts.items() if count > 0}
    sorted_sdgs = sorted(sdg_percentages.items(), key=lambda x: x[1], reverse=True)
    
    display_top_sdgs_mapping(sorted_sdgs, sdg_frame)
    display_pie_chart(sdg_percentages, piechart_frame)

def display_top_sdgs_mapping(sorted_sdgs, mapping_sdg_frame):
    # Clear previous content in the SDG frame
    for widget in mapping_sdg_frame.winfo_children():
        widget.destroy()

    # Create a scrollable frame inside the mapping SDG frame
    scrollable_frame = ctk.CTkScrollableFrame(mapping_sdg_frame, width=370, height=340, fg_color="#FFF8DC", corner_radius=3)
    scrollable_frame.pack(expand=True, fill="both", padx=5, pady=5)

    frame_width = 340
    frame_height = 60
    
    # Loop through all SDGs with matches and display them in the scrollable frame
    for sdg, percentage in sorted_sdgs:
        frame = ctk.CTkFrame(scrollable_frame, fg_color="white", width=frame_width, height=frame_height)
        frame.pack_propagate(False)
        frame.pack(pady=3, padx=5, fill="x")

        # Load SDG icon
        icon_path = sdg_keyword_group_logos.get(sdg, "default_icon.png")  # Fallback in case SDG icon is missing
        img = Image.open(icon_path).resize((50, 50), Image.Resampling.LANCZOS)
        img_photo = ImageTk.PhotoImage(img)

        # SDG Icon
        icon_label = ctk.CTkLabel(frame, image=img_photo, text="")
        icon_label.image = img_photo
        icon_label.pack(side="left", padx=10)

        # SDG Text Label
        text_label = ctk.CTkLabel(frame, text=f"SDG {sdg} - {percentage:.1f}%", font=("Arial", 14, "bold"))
        text_label.pack(side="left", padx=10)

    return scrollable_frame

def open_mapping_window():
    mapping_window = ctk.CTkToplevel(root)
    mapping_window.title("Mapping")
    mapping_window.geometry("1280x720")
    mapping_window.resizable(False, False)
    mapping_window.attributes("-topmost", True)  # This ensures it appears in front

    # Background image for the mapping window 
    mapping_bg_image = CTkImage(light_image=Image.open(r"assets\\SchoolBg\\Mapping.png"), size=(1280, 720))
    mapping_bg_label = ctk.CTkLabel(mapping_window, image=mapping_bg_image, text="")
    mapping_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    title_entry = ctk.CTkEntry(mapping_window, width=370, height=40, 
                                fg_color="#FFF8DC", 
                                bg_color="#000001",
                                border_color="#FFD700",
                                border_width=2,
                                corner_radius=5,
                                text_color="black",
                                font=("Helvetica", 13))
    title_entry.place(x=35, y=240)
    pywinstyles.set_opacity(title_entry, color="#000001")

    abstract_text = ctk.CTkTextbox(mapping_window, width=370, height=275, 
                                   fg_color="#FFF8DC",
                                   bg_color="#000001",
                                   border_color="#FFD700",
                                   border_width=2,
                                   corner_radius=5,
                                   text_color="black",
                                   font=("Helvetica", 13))
    abstract_text.place(x=35, y=320)
    pywinstyles.set_opacity(abstract_text, color="#000001")

    sdg_frame = ctk.CTkFrame(mapping_window, width=400, height=355, 
                             fg_color="#FFF8DC", 
                             bg_color="#000001",
                             border_color="#FFD700",
                             border_width=2,
                             corner_radius=5)
    sdg_frame.place(x=440, y=240)
    pywinstyles.set_opacity(sdg_frame, color="#000001")

     # New Pie Chart Frame
    piechart_frame = ctk.CTkFrame(mapping_window, width=400, height=355,
                                  fg_color="#FFF8DC",
                                  bg_color="#000001",
                                  border_color="#FFD700",
                                  border_width=2,
                                  corner_radius=5)
    piechart_frame.place(x=860, y=240)  # Adjusted position for placement
    pywinstyles.set_opacity(piechart_frame, color="#000001")

    footer_frame = Frame(mapping_window, bg="#333333", height=40)
    footer_frame.pack(side="bottom", fill="x")
    Label(footer_frame, text="Developed by Group GUI 2025", font=("Helvetica", 10), bg="#333333", fg="white").pack(pady=10)

    upload_button = ctk.CTkButton(mapping_window, text="Upload PDF", command=lambda: upload_pdf_mapping(title_entry, abstract_text), width=120, bg_color="#000001", fg_color="#FFD700", text_color="black")
    upload_button.place(x=35, y=620)
    pywinstyles.set_opacity(upload_button, color="#000001")

    submit_button = ctk.CTkButton(mapping_window, text="Submit", command=lambda: process_sdg_analysis_mapping(title_entry, abstract_text, sdg_frame, piechart_frame), width=120, bg_color="#000001", fg_color="#FFD700", text_color="black")
    submit_button.place(x=180, y=620)
    pywinstyles.set_opacity(submit_button, color="#000001")

    # Assign the function to the mapping button
    mapping_button.configure(command=open_mapping_window)

#load Logo
"""def load_logo():
    logo_img = Image.open("assets/sdg_mapping_Image.png").resize((250, 100), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    Label(root, image=logo_photo, bg="#228B22").place(x=50, y=10)
    root.logo = logo_photo

load_logo()"""

sdg_keyword_group_logos = {i: f"assets/SDG Logo/E_Web_{str(i).zfill(2)}.png" for i in range(1, 18)}

#background
bg_image = CTkImage(light_image=Image.open("assets\\SchoolBg\\Single.png"), size=(1280, 720))
bg_label = ctk.CTkLabel(root, image=bg_image, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

#textbox
title_entry = ctk.CTkEntry(root, width=650, height=40, 
                           fg_color="#FFF8DC", 
                           bg_color="#000001",
                           border_color="#FFD700",
                           border_width=2,
                           corner_radius=5,
                           text_color="black",
                           font=("Helvetica", 13))
title_entry.place(x=50, y=240)
pywinstyles.set_opacity(title_entry, color="#000001")

abstract_text = ctk.CTkTextbox(root, width=650, height=250, 
                            fg_color="#FFF8DC",
                            bg_color="#000001",
                            border_color="#FFD700",
                            border_width=2,
                            corner_radius=5,
                            text_color="black",
                            font=("Helvetica", 13))
abstract_text.place(x=50, y=335)
pywinstyles.set_opacity(abstract_text, color="#000001")

#buttons
upload_button = ctk.CTkButton(master=root, text="Upload PDF", command=upload_pdf, width=120, bg_color="#000001", fg_color="#FFD700", text_color="black")
upload_button.place(x=50, y=620)
pywinstyles.set_opacity(upload_button, color="#000001")

submit_button = ctk.CTkButton(root, text="Submit", command=lambda: process_sdg_analysis(title_entry.get() + " " + abstract_text.get("1.0", "end-1c")), width=120, bg_color="#000001", fg_color="#FFD700", text_color="black")
submit_button.place(x=200, y=620)
pywinstyles.set_opacity(submit_button, color="#000001")

multiple_mode_button = ctk.CTkButton(root, text="Multiple Mode", font=("Helvetica", 12), width=120, fg_color="#FFD700", text_color="black", bg_color="#000001")
multiple_mode_button.place(x=970, y=620)
multiple_mode_button.configure(command=open_multiple_mode) # Assign function to button
pywinstyles.set_opacity(multiple_mode_button, color="#000001")

mapping_button = ctk.CTkButton(root, text="Mapping", font=("Helvetica", 12), width=120, fg_color="#FFD700", text_color="black", bg_color="#000001")
mapping_button.place(x=1115, y=620)
mapping_button.configure(command=open_mapping_window)
pywinstyles.set_opacity(mapping_button, color="#000001")

#top 3 sdg frame
sdg_frame = ctk.CTkFrame(master=root, width=500, height=345, 
                         fg_color="#FFF8DC", 
                         bg_color="#000001",
                         border_color="#FFD700",
                         border_width=2,
                        corner_radius=5)
sdg_frame.place(x=735, y=240)
pywinstyles.set_opacity(sdg_frame, color="#000001")

#Footer
footer_frame = Frame(root, bg="#333333", height=40)
footer_frame.pack(side="bottom", fill="x")
Label(footer_frame, text="Developed by Group GUI 2025", font=("Helvetica", 10), bg="#333333", fg="white").pack(pady=10)

root.mainloop()
