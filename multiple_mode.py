import re
import os
import PyPDF2
import customtkinter as ctk
from tkinter import filedialog, messagebox, Label, Frame
from PIL import Image, ImageTk
import pywinstyles
from functools import partial


SDG_KEYWORDS_FOLDER = "SDG Keywords"
RESIZE_DELAY = 200  #Delay in milliseconds
sdg_keyword_group_logos = {i: f"assets/SDG Logo/E_Web_{str(i).zfill(2)}.png" for i in range(1, 18)}
multiple_window = None  # Track multiple mode window instance

# Load SDG keywords
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

# Extract text from PDF
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            title = os.path.splitext(os.path.basename(file_path))[0]
            return title, text.lower()
    except Exception as e:
        return "Error in extracting text", f"Failed to read PDF: {str(e)}"

# Open Multiple Mode Window
def open_multiple_mode():
    global multiple_window

    if multiple_window and multiple_window.winfo_exists():
        multiple_window.lift()
        multiple_window.attributes("-topmost", True)
        return

    ctk.set_appearance_mode("light")
    multiple_window = ctk.CTkToplevel()
    multiple_window.title("Multiple Mode")
    multiple_window.geometry("1280x720")
    multiple_window.resizable(False, False)
    multiple_window.attributes("-topmost", True)
    multiple_window.protocol("WM_DELETE_WINDOW", close_multiple_mode)

    multiple_bg_image = ctk.CTkImage(light_image=Image.open(r"assets\\SchoolBg\\Multiple.png"), size=(1280, 720))
    multiple_bg_label = ctk.CTkLabel(multiple_window, image=multiple_bg_image, text="")
    multiple_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    title_entries = []
    abstract_texts = []
    sdg_frames = []

    # Upload PDF
    def upload_pdf_multiple(index):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            title, text = extract_text_from_pdf(file_path)
            title_entries[index].delete(0, "end")
            title_entries[index].insert(0, title)
            abstract_texts[index].delete("1.0", "end")
            abstract_texts[index].insert("1.0", text[:400])  

    # Submit Analysis
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

def close_multiple_mode():
    global multiple_window
    multiple_window.destroy()
    multiple_window = None  # Reset the variable when closed

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()  # Hide the main window
    open_multiple_mode()
    root.mainloop()  # Keep the program running