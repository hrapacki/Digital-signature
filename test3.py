import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA3_256
import matlab.engine
import csv
import random
from random import randbytes
import os

eng = matlab.engine.connect_matlab()
eng.untitled(nargout=0)
xor_histogram = eng.workspace['xor_histogram']
numbers = list(xor_histogram)
eng.quit()

def generate_keys(numbers):
    def randfunc(n, numbers):
        chunk_size = n // len(numbers) + 1
        random_data = b''
        for num in numbers:
            if isinstance(num, int):
                int_num = num
            else:
                int_num = int.from_bytes(num, byteorder='big')
            int_num = min(1024, int_num)  
            random_data += os.urandom((int_num + 7) // 8)[:chunk_size]
        return random_data[:n]
    
    key = RSA.generate(2048, randfunc=lambda n: randfunc(n, numbers))
    return key, key.publickey()
class MyAPP:
    def __init__(self, root):
        self.root = root
        self.private_key, self.public_key = generate_keys(numbers)
        self.init_gui()

    def init_gui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        self.message_label = tk.Label(frame, text="Plik do podpisania:")
        self.message_label.grid(row=0, column=0, sticky=tk.W)
        self.message_entry = tk.Entry(frame, width=40)
        self.message_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.browse_button = tk.Button(frame, text="Przeglądaj", command=self.browse_file)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)

        self.signature_label = tk.Label(frame, text="Podpis:")
        self.signature_label.grid(row=2, column=0, sticky=tk.W)
        self.signature_text = scrolledtext.ScrolledText(frame, width=40, height=5)
        self.signature_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.verify_label = tk.Label(frame, text="Plik do weryfikacji:")
        self.verify_label.grid(row=4, column=0, sticky=tk.W)
        self.verify_entry = tk.Entry(frame, width=40)
        self.verify_entry.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self.browse_verify_button = tk.Button(frame, text="Przeglądaj", command=self.browse_verify_file)
        self.browse_verify_button.grid(row=5, column=2, padx=5, pady=5)

        self.verify_result_label = tk.Label(frame, text="Wynik weryfikacji:")
        self.verify_result_label.grid(row=6, column=0, sticky=tk.W)
        self.verify_text = tk.Entry(frame, width=40)
        self.verify_text.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        self.sign_button = tk.Button(frame, text="Podpisz", command=self.sign_message)
        self.sign_button.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)

        self.verify_button = tk.Button(frame, text="Weryfikuj", command=self.verify)
        self.verify_button.grid(row=8, column=1, padx=5, pady=5, sticky=tk.E)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.message_entry.delete(0, tk.END)
            self.message_entry.insert(0, file_path)

    def browse_verify_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.verify_entry.delete(0, tk.END)
            self.verify_entry.insert(0, file_path)

    def sign_message(self):
        file_path = self.message_entry.get()
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            hash_obj = SHA3_256.new(file_data)
            signature = pkcs1_15.new(self.private_key).sign(hash_obj)
            self.signature_text.delete("1.0", tk.END)
            self.signature_text.insert(tk.END, signature.hex())

            signature_file_path = file_path + '.sig'
            with open(signature_file_path, 'wb') as sig_file:
                sig_file.write(signature)
            messagebox.showinfo("Sukces", f"Podpis zapisany w {signature_file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def verify(self):
        file_path = self.verify_entry.get()
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            signature_file_path = file_path + '.sig'
            if not os.path.exists(signature_file_path):
                raise FileNotFoundError(f"Plik podpisu {signature_file_path} nie istnieje")
            
            with open(signature_file_path, 'rb') as sig_file:
                signature = sig_file.read()

            hash_obj = SHA3_256.new(file_data)
            try:
                pkcs1_15.new(self.public_key).verify(hash_obj, signature)
                self.verify_text.delete(0, tk.END)
                self.verify_text.insert(tk.END, "Podpis prawidłowy")
            except (ValueError, TypeError):
                self.verify_text.delete(0, tk.END)
                self.verify_text.insert(tk.END, "Podpis nieprawidłowy")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MyAPP(root)
    root.mainloop()
