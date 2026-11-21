
import zlib
import struct
import os
import base64
import customtkinter as ctk
from tkinter import filedialog, messagebox


# ==========================================
# CONFIGURATION
# ==========================================

BDY_BASE64 = "ikzTNFVVVV0XnuZ5pmmaqqqqrgvPE0XTNE1VdV3XheeJ"


# ==========================================
# FILE PROCESSING
# ==========================================

def ensure_directories(base_dir, create_bdy=True):
    """Create output directory structure."""

    os.makedirs(os.path.join(base_dir, "ABM"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "Sound"), exist_ok=True)

    if create_bdy:
        os.makedirs(
            os.path.join(base_dir, "Sound", "bdy"),
            exist_ok=True
        )

        os.makedirs(
            os.path.join(base_dir, "Sound", "body"),
            exist_ok=True
        )


def process_file(ogg_path, create_bdy=True):

    base_dir = os.path.dirname(ogg_path) or "."
    filename, _ = os.path.splitext(ogg_path)
    base_filename = os.path.basename(filename)

    ensure_directories(base_dir, create_bdy)

    if not os.path.isfile(ogg_path):
        print(f"Could not open {ogg_path}")
        return False

    with open(ogg_path, "rb") as f:
        ogg_data = f.read()

    if len(ogg_data) > 0x600000:
        print(f"File {ogg_path} is too big.")
        return False

    # Calculate Adler-32 checksum
    magic = zlib.adler32(ogg_data)
    magic &= 0xFFFFFFFF

    if magic & 0x80000000:
        magic -= 0x100000000

    # Compress first 2500 bytes
    compressed_data = zlib.compress(ogg_data[:2500], 9)

    # ======================================
    # CREATE HD
    # ======================================

    hd_path = os.path.join(
        base_dir, "Sound", f"{base_filename}.hd"
    )

    with open(hd_path, "wb") as f:
        f.write(struct.pack("<i", magic))
        f.write(compressed_data)

    print(f"Created {hd_path}")

    # ======================================
    # CREATE ABM
    # ======================================

    abm_path = os.path.join(
        base_dir, "ABM", f"{base_filename}.abm"
    )

    with open(abm_path, "wb") as f:
        f.write(b"AuditionMusic\x12\x34\x00")
        f.write(struct.pack("<i", magic))
        f.write(b"\x00" * 2480)
        f.write(ogg_data[2500:])

    print(f"Created {abm_path}")

    # ======================================
    # CREATE BDY (OPTIONAL)
    # ======================================

    if create_bdy:

        bdy_data = base64.b64decode(BDY_BASE64)

        # Original BDY directory
        bdy_path = os.path.join(
            base_dir, "Sound", "bdy",
            f"{base_filename}.bdy"
        )

        # Clone BDY directory
        body_path = os.path.join(
            base_dir, "Sound", "body",
            f"{base_filename}.bdy"
        )

        # Write original BDY
        with open(bdy_path, "wb") as f:
            f.write(bdy_data)

        print(f"Created {bdy_path}")

        # Write cloned BDY
        with open(body_path, "wb") as f:
            f.write(bdy_data)

        print(f"Created {body_path}")

    return True


# ==========================================
# GUI FUNCTIONS
# ==========================================

selected_files = []


def select_files():

    global selected_files

    file_paths = filedialog.askopenfilenames(
        filetypes=[("OGG files", "*.ogg")]
    )

    if file_paths:
        selected_files = file_paths

        selected_files_label.configure(
            text=f"Selected files: {len(selected_files)}"
        )


def process_files():

    if not selected_files:
        messagebox.showerror(
            "Error",
            "No files selected!"
        )
        return

    create_bdy = bdy_checkbox.get()

    success_count = 0

    for file in selected_files:

        try:
            if process_file(file, create_bdy):
                success_count += 1

        except Exception as e:
            print(f"Error processing {file}: {e}")

    messagebox.showinfo(
        "Result",
        f"Processed {success_count}/{len(selected_files)} "
        f"files successfully."
    )


# ==========================================
# GUI SETUP
# ==========================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("OGG2ABM Audition Converter")
app.geometry("420x340")
app.resizable(False, False)


# Title
title_label = ctk.CTkLabel(
    app,
    text="OGG to HD/ABM/BDY Converter",
    font=("Arial", 16, "bold")
)

title_label.pack(pady=(25, 15))


# Select files
select_button = ctk.CTkButton(
    app,
    text="Select OGG Files",
    command=select_files
)

select_button.pack(pady=10)


# Selected files counter
selected_files_label = ctk.CTkLabel(
    app,
    text="Selected files: 0"
)

selected_files_label.pack(pady=8)


# BDY option
bdy_checkbox = ctk.CTkCheckBox(
    app,
    text="Generate BDY (bdy + body)",
    onvalue=1,
    offvalue=0
)

bdy_checkbox.select()
bdy_checkbox.pack(pady=12)


# Start button
process_button = ctk.CTkButton(
    app,
    text="START",
    command=process_files,
    height=38
)

process_button.pack(pady=15)


# Footer
footer = ctk.CTkLabel(
    app,
    text="© 2025 TKAQN • All Rights Reserved",
    font=("Segoe UI", 10),
    text_color="#b0b0b0"
)

footer.place(
    relx=0.5,
    rely=0.96,
    anchor="center"
)


app.mainloop()
