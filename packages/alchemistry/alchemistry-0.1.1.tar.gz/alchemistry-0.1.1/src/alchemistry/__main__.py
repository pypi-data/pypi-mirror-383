from alchemistry import game
from alchemistry.cli import exec_command

def main():
	try:
		print("Welcome to Alchemistry! Type \"help\" for help!")
		while True:
			inp = input("> ")

			exec_command(inp)
	except KeyboardInterrupt:
		print("\n\nWow, what a shame.")

if __name__ == "__main__":
	main()
