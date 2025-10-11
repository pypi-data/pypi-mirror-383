import os
import subprocess
from colorama import Fore, Style, init
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

init(autoreset=True)  # Enables color on Windows too

COMMANDS = [
    "cd", "clear", "exit", "help", "ls", "mkdir", "rmdir", "python", "echo"
]

class CustomTerminal:
    def __init__(self):
        self.session = PromptSession()
        self.completer = WordCompleter(COMMANDS, ignore_case=True)

    def run(self):
        print(Fore.CYAN + "🚀 Welcome to VedantSH (Custom Python Terminal)!")
        print(Fore.YELLOW + "Type 'help' to see available commands.\n")

        while True:
            try:
                cmd = self.session.prompt(
                    f"{Fore.GREEN}{os.getcwd()} {Fore.WHITE}>> ",
                    completer=self.completer
                ).strip()

                if not cmd:
                    continue

                if cmd.lower() == "exit":
                    print(Fore.CYAN + "Goodbye 👋")
                    break

                elif cmd.startswith("cd "):
                    self.change_directory(cmd[3:].strip())

                elif cmd.lower() == "clear":
                    self.clear_screen()

                elif cmd.lower() == "help":
                    self.show_help()

                else:
                    self.run_command(cmd)

            except KeyboardInterrupt:
                print("\n" + Fore.YELLOW + "Use 'exit' to quit.")
            except EOFError:
                break

    def change_directory(self, path):
        try:
            os.chdir(os.path.expanduser(path))
        except FileNotFoundError:
            print(Fore.RED + "❌ Directory not found.")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_help(self):
        print(Fore.CYAN + "Available commands:")
        print(Fore.YELLOW + "  cd <dir>      - Change directory")
        print(Fore.YELLOW + "  clear         - Clear the screen")
        print(Fore.YELLOW + "  exit          - Exit terminal")
        print(Fore.YELLOW + "  help          - Show this help")
        print(Fore.YELLOW + "  [system cmd]  - Run any system command")

    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            if result.stdout:
                print(Style.RESET_ALL + result.stdout, end="")
            if result.stderr:
                print(Fore.RED + result.stderr, end="")
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

# Launcher function (used for entry point)
def main():
    shell = CustomTerminal()
    shell.run()
