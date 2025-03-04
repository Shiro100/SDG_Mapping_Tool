import re
import PyPDF2
import os
import tkinter as tk
from tkinter import Label, Entry, Button, Frame, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

SDG_KEYWORDS_FOLDER = "SDG Keywords"

# SDG Text File Keywords
def load_sdg_keywords():
    sdg_keywords = {}

    for i in range(1, 18):  
        file_path = os.path.join(SDG_KEYWORDS_FOLDER, f"SDG{i:02}.txt")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                keywords = [line.strip().strip('",').lower() for line in f if line.strip()]
                sdg_keywords[i] = keywords  # Store in dictionary

    return sdg_keywords

# Load SDG keywords at the start
sdg_keywords = load_sdg_keywords()

# Function to extract the abstract from PDF
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

            # Use file name as the title
            title = os.path.splitext(os.path.basename(file_path))[0]

            lower_text = text.lower()
            abstract_text = "Abstract not found."

            if "abstract" in lower_text:
                abstract_index = lower_text.find("abstract") + len("abstract")
                abstract_text = text[abstract_index:].strip()

                # Limit to first 400 words after the word "Abstract"
                words = abstract_text.split()
                abstract_text = " ".join(words[:400])

            return title, abstract_text

    except Exception as e:
        return "Error in extracting text", f"Failed to read PDF: {str(e)}"


# Function to upload and process a PDF file
def upload_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        title, abstract = extract_text_from_pdf(file_path)
        title_entry.delete(0, tk.END)
        title_entry.insert(0, title) 
        abstract_text.delete("1.0", tk.END)
        abstract_text.insert("1.0", abstract)
        process_sdg_analysis(title + " " + abstract)

# SDG Keyowrd Function
def process_sdg_analysis(text):
    if not text.strip():
        messagebox.showwarning("Input Error", "No text found for analysis.")
        return

    # Normalize text 
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)  # Replace newlines with a single space

    sdg_counts = {sdg: 0 for sdg in sdg_keywords.keys()}  # Initialize SDG count dictionary

    for sdg, keyword_list in sdg_keywords.items():
        for keyword in keyword_list:
            keyword_clean = keyword.strip().lower() 

            #Keyword Match
            pattern = re.compile(rf"\b{re.escape(keyword_clean)}\b", re.IGNORECASE)
            matches = pattern.findall(text)

            #SDG Ketword Counter
            if matches:
                sdg_counts[sdg] += len(matches)  
                print(f"Matched keyword: '{keyword_clean}' under SDG {sdg}")  

    total_matches = sum(sdg_counts.values())

    if total_matches == 0:
        messagebox.showinfo("No SDGs Found", "No relevant SDG keywords detected. Please refine your input.")
        return

    #Computation for Top 3 SDG
    sdg_percentages = {sdg: (count / total_matches) * 100 for sdg, count in sdg_counts.items()}
    sorted_sdgs = sorted(sdg_percentages.items(), key=lambda x: x[1], reverse=True)[:3]

    # Display results in the SDG panel
    display_top_sdgs(sorted_sdgs)

# Display Top 3 SDG 
def display_top_sdgs(sorted_sdgs):
    for widget in sdg_frame.winfo_children():
        widget.destroy()  

    for index, (sdg, percentage) in enumerate(sorted_sdgs):
        frame = Frame(sdg_frame, bg="white")
        frame.pack(pady=5, fill="x")

        icon_path = sdg_keyword_group_logos.get(sdg)
        img = Image.open(icon_path).resize((110, 110), Image.Resampling.LANCZOS)
        img_photo = ImageTk.PhotoImage(img)

        icon_label = Label(frame, image=img_photo, bg="white")
        icon_label.image = img_photo
        icon_label.pack(side="left", padx=10)

        text_label = Label(frame, text=f"SDG {sdg} - {percentage:.1f}%", font=("Helvetica", 12, "bold"), bg="white")
        text_label.pack(side="left", padx=10)

# GUI Functions
root = tk.Tk()
root.title("SDG Mapping Tool")
root.geometry("1280x720")
root.resizable(False, False)
root.configure(bg="#228B22")  


sdg_keyword_group_logos = {
    i: f"assets/SDG Logo/E_Web_{str(i).zfill(2)}.png" for i in range(1, 18)
}

def load_logo():
    logo_img = Image.open("assets/sdg_mapping_Image.png").resize((250, 100), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    Label(root, image=logo_photo, bg="#228B22").pack(pady=10)
    root.logo = logo_photo

load_logo()
#Title Text Box
Label(root, text="Title", font=("Helvetica", 14, "bold"), bg="#228B22", fg="white").place(x=50, y=130)
title_entry = Entry(root, font=("Helvetica", 30), width=30, highlightbackground="#FFD700", highlightthickness=2, bg="#FFF8DC")
title_entry.place(x=50, y=160)
#Abstract Text Box
Label(root, text="Abstract", font=("Helvetica", 14, "bold"), bg="#228B22", fg="white").place(x=50, y=220)
abstract_text = ScrolledText(root, font=("Helvetica", 30), width=30, height=7, highlightbackground="#FFD700", highlightthickness=2, wrap="word", borderwidth=0, bg="#FFF8DC")
abstract_text.place(x=50, y=250)

abstract_text.config(yscrollcommand=lambda *args: None)  

# Buttons
Button(root, text="Upload PDF", font=("Helvetica", 12), bg="#FFD700", fg="black", width=12, command=upload_pdf).place(x=50, y=620)
Button(root, text="Submit", font=("Helvetica", 12), bg="#FFD700", fg="black", width=12, command=lambda: process_sdg_analysis(title_entry.get() + " " + abstract_text.get("1.0", "end-1c"))).place(x=200, y=620)
Button(root, text="Multiple Mode", font=("Helvetica", 12), bg="#FFD700", fg="black", width=15).place(x=900, y=620)
Button(root, text="Mapping", font=("Helvetica", 12), bg="#FFD700", fg="black", width=15).place(x=1078, y=620)

# Right Section
sdg_container = Frame(root, bg="#FFD700", highlightbackground="black", highlightthickness=0)
sdg_container.place(x=750, y=155, width=470, height=415)

Label(sdg_container, text="Top 3 SDGs", font=("Helvetica", 16, "bold"), fg="white",bg="#228B22").pack(fill="x")
sdg_frame = Frame(sdg_container, bg="#f0f0e6")
sdg_frame.pack(fill="both", expand=True, padx=5, pady=5)

# Footer
footer_frame = Frame(root, bg="#333333", height=40)
footer_frame.pack(side="bottom", fill="x")
Label(footer_frame, text="Developed by Group GUI 2025", font=("Helvetica", 10), bg="#333333", fg="white").pack(pady=10)

root.mainloop()
