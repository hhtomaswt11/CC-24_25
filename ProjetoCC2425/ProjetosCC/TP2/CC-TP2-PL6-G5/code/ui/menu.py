from dataclasses import dataclass
from os import system
import shutil
import time
import os

@dataclass
class Menu:

    def __init__(self, storage_path):
        self.storage_path = storage_path

    def clear_terminal(self):
        """Limpa o terminal enviando caracteres de escape ANSI."""
        print("\033[2J\033[H", end="")

    def run(self):
        
        while True:
            print('''
                Welcome!
            
                [1]- Choose a task ID
                [0]- Quit
                ''')
            option = str(input("\nChoose an option: "))

            if option == "1":
                task_id = str(input("\nChoose a task ID: "))

                task_id_normalized = "T-" + task_id

                #se existir, pedir para introduzir um device_id
                task_path = os.path.join(self.storage_path, task_id_normalized)
                if os.path.isdir(task_path):
                    print(f"Found folder '{task_id_normalized}' in '{self.storage_path}'!")

                    device_id = str(input("\nChoose a device ID: "))
                    device_id_normalized = "n" + device_id + ".txt"

                    files_in_directory = os.listdir(task_path)  # Lista todos os ficheiros na pasta
                    if device_id_normalized in files_in_directory:  # Verifica se o device_id está na lista de ficheiros
                        print(f"Found file '{device_id_normalized}' in '{task_path}'!\n\n\n")
                        file_path = os.path.join(task_path, device_id_normalized)
                        #print(f"\nFILE_PATH: {file_path}\n")
                        
                        if os.path.isfile(file_path):
                            try:
                                #self.clear_terminal()
                                with open(file_path, 'r', encoding='utf-8') as file:
                                    
                                    content = file.read()
                                    #self.clear_terminal()
                                    #print("Conteúdo do ficheiro:")
                                    print(content)
                                    print("\n\n\t\tFile read successfully!\n\n")
                                    time.sleep(5)
                                file.close()
                            except Exception as e:
                                print(f"[Error]: Reading File {e}")
                    else:
                        print(f"Not found file'{device_id_normalized}' in '{task_path}'.")
                else:
                    print(f"Not found folder '{task_id_normalized}' in '{self.storage_path}'.")

                #se nao existir, pedir para introduzir outra vez
                


            elif option == "0":
                shutil.rmtree(self.storage_path)
                break