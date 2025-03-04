import os
import re
import PyPDF2
import customtkinter as ctk
from tkinter import filedialog, messagebox, Label, Frame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import pywinstyles

SDG_KEYWORDS_FOLDER = "SDG Keywords"
RESIZE_DELAY = 200  # Delay in milliseconds
sdg_keyword_group_logos = {i: f"assets/SDG Logo/E_Web_{str(i).zfill(2)}.png" for i in range(1, 18)}
mapping_window = None  # Global variable to track the window instance

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

# Display Pie Chart
def display_pie_chart(sdg_percentages, piechart_frame):
    for widget in piechart_frame.winfo_children():
        widget.destroy()

    scrollable_pie_frame = ctk.CTkScrollableFrame(piechart_frame, width=370, height=340, fg_color="#FFF8DC", corner_radius=3)
    scrollable_pie_frame.pack(expand=True, fill="both", padx=5, pady=5)

    frame_width = 340
    frame_height = 340  
    pie_frame = ctk.CTkFrame(scrollable_pie_frame, fg_color="white", width=frame_width, height=frame_height)
    pie_frame.pack_propagate(False)
    pie_frame.pack(pady=3, padx=5, fill="x")

    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    labels = [f"SDG {sdg}" for sdg in sdg_percentages.keys()]
    sizes = list(sdg_percentages.values())

    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    ax.axis('equal')

    canvas = FigureCanvasTkAgg(fig, master=pie_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill='both')

    return scrollable_pie_frame

def upload_pdf_mapping(title_entry, abstract_text):
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        title, text = extract_text_from_pdf(file_path)
        title_entry.delete(0, "end")
        title_entry.insert(0, title)
        abstract_text.delete("1.0", "end")
        abstract_text.insert("1.0", text[:400])  # Display part of the text

# Display SDG Mapping
def display_top_sdgs_mapping(sorted_sdgs, mapping_sdg_frame):
    for widget in mapping_sdg_frame.winfo_children():
        widget.destroy()

    scrollable_frame = ctk.CTkScrollableFrame(mapping_sdg_frame, width=370, height=340, fg_color="#FFF8DC", corner_radius=3)
    scrollable_frame.pack(expand=True, fill="both", padx=5, pady=5)

    frame_width = 340
    frame_height = 60
    
    for sdg, percentage in sorted_sdgs:
        frame = ctk.CTkFrame(scrollable_frame, fg_color="white", width=frame_width, height=frame_height)
        frame.pack_propagate(False)
        frame.pack(pady=3, padx=5, fill="x")

        icon_path = sdg_keyword_group_logos.get(sdg, "default_icon.png")
        img = Image.open(icon_path).resize((50, 50), Image.Resampling.LANCZOS)
        img_photo = ImageTk.PhotoImage(img)

        icon_label = ctk.CTkLabel(frame, image=img_photo, text="")
        icon_label.image = img_photo
        icon_label.pack(side="left", padx=10)

        text_label = ctk.CTkLabel(frame, text=f"SDG {sdg} - {percentage:.1f}%", font=("Arial", 14, "bold"))
        text_label.pack(side="left", padx=10)

    return scrollable_frame

# Open Mapping Window
def open_mapping_window():
    global mapping_window

    if mapping_window and mapping_window.winfo_exists():
        mapping_window.lift()
        mapping_window.attributes("-topmost", True)
        return

    ctk.set_appearance_mode("light")
    mapping_window = ctk.CTkToplevel()
    mapping_window.title("Mapping Mode")
    mapping_window.geometry("1280x720")
    mapping_window.resizable(False, False)
    mapping_window.attributes("-topmost", True)

    mapping_window.protocol("WM_DELETE_WINDOW", close_mapping_mode)
    
    # Background image for the mapping window 
    mapping_bg_image = ctk.CTkImage(light_image=Image.open("assets/SchoolBg/Mapping.png"), size=(1280, 720))
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
    

def close_mapping_mode():
    global mapping_window
    mapping_window.destroy()
    mapping_window = None  # Reset the variable when closed

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    open_mapping_window()
    root.mainloop()