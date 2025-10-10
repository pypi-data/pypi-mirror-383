# -*- coding: utf-8 -*-
#
# Author: G. Benabdellah
# Departement of physic
# University of Tiaret , Algeria
# E-mail ghlam.benabdellah@gmail.com
#
# this program is part of VAMgui 
# first creation 28-05-2024
#  
#
# License: GNU General Public License v3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#  log change:
#
#
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, Text, Scrollbar, Button
import subprocess
import os
import platform
import sys
import webbrowser
from PIL import Image
from vampgui.helpkey import  show_help

class VisuaVDC:
    def __init__(self, tab):
        self.Canvas, self.frame = self.canvas(tab)
        self.tmp_path = self.create_vampire_dir()
        self.command_running = False
        self.create_vdc_path_section()
        self.load_config()
        self.create_vdc_flags_section()
        self.create_vesta_section()
        self.load_vesta_config()
        self.create_povray_section()

    #==========================
    def canvas(self,tab):
        # Create a canvas
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        canvas = tk.Canvas(tab)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)
        v_scrollbar = tk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview, bg='black')
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=v_scrollbar.set)
        h_scrollbar = tk.Scrollbar(tab, orient=tk.HORIZONTAL, command=canvas.xview, bg='black')
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.config(xscrollcommand=h_scrollbar.set)
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(-1 * int(event.delta / 120), "units"))
        canvas.bind_all("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(-1 * int(event.delta / 120), "units"))
        frame.bind("<Configure>", configure_scroll_region)
        return canvas, frame

    def create_vampire_dir(self):
        """Create the vampire directory if it doesn't exist"""
        home_dir = os.path.expanduser("~")
        vampire_dir = os.path.join(home_dir, "vampire_tmp" if sys.platform == "win32" else ".vampire")
        os.makedirs(vampire_dir, exist_ok=True)
        return vampire_dir


    def create_vdc_path_section(self):
        """Create the VDC program path section"""
        frame = tk.LabelFrame(self.frame, text="vdc Program Path: ", font=("Helvetica", 14, "bold"))
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(8, 8))
        tk.Label(frame, text="VDC Path:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.path_entry = ttk.Entry(frame, width=50)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(frame, text="Browse", command=self.browse_vdc).grid(row=0, column=2, padx=5, pady=5)

    def browse_vdc(self):
        """Browse for VDC executable"""
        if path := filedialog.askopenfilename(title="Select VDC executable"):
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.save_config()
            
    # def browse_vdc(self):
    #     filepath = filedialog.askopenfilename(title="Select vdc executable")
    #     if filepath:
    #         self.path_entry.delete(0, tk.END)
    #         self.path_entry.insert(0, filepath) 

    def save_config(self):
        """Save VDC configuration"""
        try:
            with open(os.path.join(self.tmp_path, "config_vdc.txt"), "w") as f:
                f.write(self.path_entry.get() + "\n")
        except Exception as e:
            print(f"Error saving VDC config: {e}")

 
    def load_config(self):
        """Load VDC configuration"""
        try:
            with open(os.path.join(self.tmp_path, "config_vdc.txt"), "r") as f:
                if path := f.readline().strip():
                    self.path_entry.insert(0, path)
        except FileNotFoundError:
            pass

    def create_vdc_flags_section(self):
        """Create the VDC flags section with checkboxes and help buttons"""
        flag_frame = tk.LabelFrame(self.frame, text="VDC Converter Flags: ", font=("Helvetica", 14, "bold"))
        flag_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(8, 8))

        self.flags = {
            "--xyz ": "none",
            "--povray ": "none",
            "--povray-cells ": "none",
            "--povray-grains ": "none",
            "--vtk ": "none",
            "--text ": "none",
            "--spin-spin-correlation ": "none",
            "--3D ": "none",
            "--verbose ": "none",
            "--vector-z ": "0,0,1",
            "--vector-x ": "0,0,1",
            "--slice ": "0,1,0,1,0,1",
            "--slice-void ": "",
            "--slice-sphere ": "",
            "--slice-cylinder ": "",
            "--remove-material ": "",
            "--frame-start ": "0",
            "--frame-final ": "0",
            "--afm ": "",
            "--colourmap ": "BWR",
            "--custom-colourmap ": ""
        }
  # --xyz    Data output in .xyz format for viewing in rasmol/jmol
  #                --povray Data output in PoVRAY format for rendering
  #                --povray-cells Data output in PoVRAY format for rendering
  #                --povray-grains Data output in PoVRAY format for rendering
  #                --vtk    Data output in VTK format for viewing in Paraview
  #                --text   Data output in plain text format for plotting in gnuplot/excel etc
  #                --cells  Data output in plain text format in cells
  #                --ssc    Spin-spin correlation data in text format



        colors = ["C2", "BWR", "CBWR", "Rainbow"]
        self.flag_widgets = {}
        entries = {}
        Padx=5
        max_row=7

        for i, (flag, default) in enumerate(self.flags.items()):
            row = i % 7 + 1
            col =3*(i // 7)
            # Checkbox
            var = tk.BooleanVar()
            # Create flag frame
            check = tk.Checkbutton(flag_frame, text=flag, variable=var, font=13)
            check.grid(row=row, column=col+1, sticky="w", padx=10, pady=5)
            # Entry field
            if flag == "--colourmap":
                entry = ttk.Combobox(flag_frame, values=colors,state="readonly", width=10)
                entry.grid(row=row, column=col+2, padx=Padx  , sticky="e")
                entry.set(default if default in colors else "Rainbow")
                entries[flag] = (var, entry, check)
            elif default == "none":
                entry = tk.Entry(flag_frame, width=10, state='disabled')
                entry.grid(row=row, column=col+2,  padx=Padx , sticky="w")
                entry.insert(0, default)
                entries[flag] = (var, entry, check)
            else:
                entry = tk.Entry(flag_frame, bg='white', width=10)
                entry.grid(row=row, column=col+2,  padx=Padx , sticky="w")
                entry.insert(0, default)
                entries[flag] = (var, entry, check)



            # Help button
            help_button = tk.Button(flag_frame, text="?", command=lambda flag=flag: show_help(flag))
            help_button.grid(row=row, column=col+3, sticky="w")
            self.flag_widgets[flag] = (var, entry)




        run_vdc_button = tk.Button(flag_frame, text="Run vdc",bg="lightgreen", command=self.run_vdc, width=20)
        run_vdc_button.grid(row=max_row+1, column=2, columnspan=3, pady=20, sticky="w")

    def run_vdc(self):
        """Run the VDC command with selected flags"""
        if not (vdc_path := self.path_entry.get()):
            messagebox.showerror("Error", "Please select VDC executable")
            return

        flags = []
        for flag, (var, entry) in self.flag_widgets.items():
            if var.get():
                value = entry.get()

                if value and value != "none":
                    flags.append(f"{flag} {value}")
                else:
                    flags.append(flag)
        print(flags)

        if not flags:
            messagebox.showerror("Error", "Please select at least one flag")
            return

        try:
            result = subprocess.run(
                f"{vdc_path} {' '.join(flags)}",
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Create a custom dialog for VDC Output
                dialog = Toplevel()
                dialog.title("VDC Output")
                dialog.geometry("600x200")  # Set custom size (width x height)

                # Create a Text widget for the output
                text_area = Text(dialog, wrap="word", font=("Arial", 12))
                text_area.insert(tk.END, result.stdout)
                text_area.config(state="disabled")  # Make text read-only

                # Add a scrollbar
                scrollbar = Scrollbar(dialog, orient="vertical", command=text_area.yview)
                text_area.config(yscrollcommand=scrollbar.set)

                # Layout widgets
                text_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
                scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

                # Add an OK button to close
                ok_button = Button(dialog, text="OK", command=dialog.destroy)
                ok_button.grid(row=1, column=0, columnspan=2, pady=10)

                # Make the dialog resizable
                dialog.grid_rowconfigure(0, weight=1)
                dialog.grid_columnconfigure(0, weight=1)

                # Center the dialog on the screen
                dialog.update_idletasks()
                width = dialog.winfo_width()
                height = dialog.winfo_height()
                x = (dialog.winfo_screenwidth() // 2) - (width // 2)
                y = (dialog.winfo_screenheight() // 2) - (height // 2)
                dialog.geometry(f"{width}x{height}+{x}+{y}")

                dialog.transient(dialog.master)  # Keep dialog on top of parent
                dialog.grab_set()  # Make dialog modal
                dialog.wait_window()  # Wait until dialog is closed

                self.save_config()
            else:
                messagebox.showerror("Error", result.stderr)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    # def run_vdc(self):
    #     vdc_path = self.path_entry.get()
    #     selected_flags = ""
    #     for _, entries in self.flag_vars:
    #         for flag, (var, entry, check) in entries.items():
    #             if var.get():
    #                 selected_flags += flag + entry.get() + " "
    #     command = vdc_path + " " + selected_flags
    #
    #     try:
    #         result = subprocess.run(command, capture_output=True, text=True, shell=True)
    #         if result.returncode == 0:
    #             messagebox.showinfo("vdc Output", result.stdout)
    #         else:
    #             messagebox.showerror("Error", result.stderr)
    #     except Exception as e:
    #         messagebox.showerror("Error", str(e))
    #     # Save configuration
    #     self.save_config()

   


    def create_vesta_section(self):
        """Create the VESTA program section"""
        frame = tk.LabelFrame(self.frame, text="VESTA Program PATH:", font=("Helvetica", 14, "bold"))
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Website link
        tk.Label(frame, text="Visualize structures after run 'vdc --xyz' using VESTA:", font=("Helvetica", 11)).grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")

        link = tk.Label(frame, text="https://jp-minerals.org/vesta/en/download.html",
                       font=("Helvetica", 11, "underline"), fg="blue", cursor="hand2")
        link.grid(row=0, column=2, columnspan=4, padx=5, pady=5, sticky="w")
        link.bind("<Button-1>", lambda e: webbrowser.open(link.cget("text")))

        # Path entry
        tk.Label(frame, text="VESTA Path:", font=("Helvetica", 12, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.vesta_path_entry = ttk.Entry(frame, width=40)
        self.vesta_path_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        tk.Button(frame, text="Browse", command=self.browse_vesta).grid(row=1, column=4, padx=5, pady=5, sticky="w")

        # XYZ file
        tk.Label(frame, text="XYZ File:", font=("Helvetica", 12, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.xyz_entry = ttk.Entry(frame, width=40)
        self.xyz_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        self.xyz_entry.insert(0, "crystal.xyz")

        tk.Button(frame, text="Run VESTA",bg="lightblue", command=self.run_vesta).grid(row=2, column=4,  padx=5, pady=5, sticky="w")

    def browse_vesta(self):
        """Browse for VESTA executable"""
        if path := filedialog.askopenfilename(title="Select VESTA executable"):
            self.vesta_path_entry.delete(0, tk.END)
            self.vesta_path_entry.insert(0, path)
            self.save_vesta_config()

    def save_vesta_config(self):
        """Save VESTA configuration"""
        try:
            with open(os.path.join(self.tmp_path, "config_vesta.txt"), "w") as f:
                f.write(self.vesta_path_entry.get() + "\n")
        except Exception as e:
            print(f"Error saving VESTA config: {e}")


    def load_vesta_config(self):
        """Load VESTA configuration"""
        try:
            with open(os.path.join(self.tmp_path, "config_vesta.txt"), "r") as f:
                if path := f.readline().strip():
                    self.vesta_path_entry.insert(0, path)
        except FileNotFoundError:
            pass

    def run_vesta(self):
        """Run the VESTA program"""
        if not (vesta_path := self.vesta_path_entry.get()):
            messagebox.showerror("Error", "Please select VESTA executable")
            return
        xyz_file = self.xyz_entry.get()

        if not xyz_file:
            messagebox.showerror("Error", "Please select a xyz file")
            return
        if not os.path.isfile(xyz_file):
            messagebox.showerror("Error", "The selected xyz file does not exist")
            return
        if not xyz_file.lower().endswith('.xyz'):
            messagebox.showerror("Error", "Please select a valid .xyz file")
            return

        xyz_file = self.xyz_entry.get()
        try:
            if platform.system() == "Windows":
                subprocess.Popen([vesta_path, xyz_file], shell=True)
            else:
                subprocess.Popen([vesta_path, xyz_file])
            self.save_vesta_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run VESTA: {str(e)}")

 #--------------------------
    def open_link(self, url):
        webbrowser.open_new(url)
 #--------------------------



    def create_povray_section(self):
        """Create the POVRAY program section"""
        frame = tk.LabelFrame(self.frame, text="POVRAY Program", font=("Helvetica", 14, "bold"))
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        install_text = "Visualize structures after 'vdc --povray' using POVRAY"
        if platform.system() != "Windows":
            install_text += " (Install on Ubuntu: sudo apt install povray)"

        # POV file
        tk.Label(frame, text="POV File:", font=("Helvetica", 12, "bold")).grid(row=1, column=1, padx=5, pady=5, sticky="e")
        self.pov_entry = ttk.Entry(frame, width=40)
        self.pov_entry.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.pov_entry.insert(0, "spins.pov")

        tk.Label(frame, text=install_text, font=("Helvetica", 11)).grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        tk.Button(frame, text="Run POVRAY",bg="lightblue", command=self.run_povray).grid(row=1, column=3, padx=5, pady=5, sticky="w")
        tk.Button(frame, text="View PNG", bg="lightgreen" , command=self.view_png).grid(row=1, column=4, padx=5, pady=5, sticky="w")

    def run_povray(self):
        """Run the POVRAY command"""
        pov_file = self.pov_entry.get()
        if not pov_file:
            messagebox.showerror("Error", "Please select a POV file")
            return
        if not os.path.isfile(pov_file):
            messagebox.showerror("Error", "The selected POV file does not exist")
            return
        if not pov_file.lower().endswith('.pov'):
            messagebox.showerror("Error", "Please select a valid .pov file")
            return
        try:
            # if hasattr(self, 'current_image'):
            #     self.canvas.delete(self.current_image)
            # if hasattr(self, 'photo'):
            #     self.photo = None

            result = subprocess.run(
                f"povray {pov_file}",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                messagebox.showinfo("POVRAY Output", "POVRAY finished successfully")
                #self.view_png()
                self.insert_png()
            else:
                messagebox.showerror("Error", result.stderr)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_png(self):
        """View the generated PNG file"""
        png_file = self.pov_entry.get().replace(".pov", ".png")
        try:
            img = Image.open(png_file)
            img.show()
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {png_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view PNG: {str(e)}")

 #--------------------------        
    def insert_png(self):


        frame = tk.LabelFrame(self.frame, text="POVRAY output image", font=("Helvetica", 14, "bold"))
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        plot_path =self.pov_entry.get().replace(".pov", ".png")

        try:
            # Add widgets on top of the canvas
            plot_show = tk.PhotoImage(file=plot_path)  # Replace with actual path
            plot_show_label = tk.Label(frame, image=plot_show, bg="green")
            plot_show_label.grid( padx=5, pady=5, sticky="w")
            plot_show_label.image = plot_show  # Keep a reference to the image
            #frame.create_window(150, 900, window=plot_show_label, anchor=tk.NW)  # Position the l
        except FileNotFoundError:
            pass

            
            

## Assuming you have a root and tab setup somewhere else in your main application
#root = tk.Tk()
#root.title("Visual VDC")

#tab_control = ttk.Notebook(root)
#tab1 = ttk.Frame(tab_control)
#tab_control.add(tab1, text='Tab 1')

#VisuaVDC(tab1)

#tab_control.pack(expand=1, fill='both')

#root.mainloop()


    
