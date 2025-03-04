import re
import os
import PyPDF2
import customtkinter as ctk
from tkinter import filedialog, messagebox, Frame, Label, Button, PhotoImage
from PIL import Image, ImageTk
import pywinstyles
from customtkinter import CTkImage
import threading

SDG_KEYWORDS_FOLDER = "SDG Keywords"
RESIZE_DELAY = 200  # Delay in milliseconds

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
    bg_image = Image.open("SchoolBg/Title (2).png").resize((root.winfo_width(), root.winfo_height()), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label.configure(image=bg_photo)

def delayed_update_bg():
    if hasattr(root, "resize_after_id"):
        root.after_cancel(root.resize_after_id)
    root.resize_after_id = root.after(RESIZE_DELAY, update_bg_image)

#mainframe (GUI Initialization)
ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title("SDG Mapping Tool")
root.geometry("1280x720")
root.resizable(False, False)
root.bind("<Configure>", update_bg_image)
root.bind("<Configure>", lambda event: delayed_update_bg())

#load Logo
"""def load_logo():
    logo_img = Image.open("assets/sdg_mapping_Image.png").resize((250, 100), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    Label(root, image=logo_photo, bg="#228B22").place(x=50, y=10)
    root.logo = logo_photo

load_logo()"""

sdg_keyword_group_logos = {i: f"assets/SDG Logo/E_Web_{str(i).zfill(2)}.png" for i in range(1, 18)}

#background
bg_image = CTkImage(light_image=Image.open("SchoolBg/Title (2).png"), size=(1280, 720))
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
                           font=("Helvetica", 18))
title_entry.place(x=50, y=240)
pywinstyles.set_opacity(title_entry, color="#000001")

abstract_text = ctk.CTkTextbox(root, width=650, height=250, 
                            fg_color="#FFF8DC",
                            bg_color="#000001",
                            border_color="#FFD700",
                            border_width=2,
                            corner_radius=5,
                            text_color="black",
                            font=("Helvetica", 18))
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
pywinstyles.set_opacity(multiple_mode_button, color="#000001")

mapping_button = ctk.CTkButton(root, text="Mapping", font=("Helvetica", 12), width=120, fg_color="#FFD700", text_color="black", bg_color="#000001")
mapping_button.place(x=1115, y=620)
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

# Footer
footer_frame = Frame(root, bg="#333333", height=40)
footer_frame.pack(side="bottom", fill="x")
Label(footer_frame, text="Developed by Group GUI 2025", font=("Helvetica", 10), bg="#333333", fg="white").pack(pady=10)

root.mainloop()
