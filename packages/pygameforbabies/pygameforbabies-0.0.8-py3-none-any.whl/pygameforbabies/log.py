# Define ANSI escape codes for colors and reset
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m" # Resets all formatting

def info(text):
    print(f"INFO    {text}")
def warn(text):
    print(f"{YELLOW}WARN    {text}{RESET}")
def error(text):
    print(f"{RED}ERROR    {text}{RESET}")
if __name__ == "__main__":
    info("dada")
    warn("eeep")
    error("mada")