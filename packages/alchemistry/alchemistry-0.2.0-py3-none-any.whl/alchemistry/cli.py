import sys
from collections.abc import Callable
from inspect import getfullargspec

from alchemistry.helpers import levenshtein_sort_list

cmds: dict[str, tuple[str, str, list[tuple[str, str]] | None, Callable[..., int]]] = {}

def register_command(name: str, short_description: str, long_description: str, arguments: list[str] | None, function: Callable[..., int]):
	argument_names = list(getfullargspec(function)[0])

	args = None

	if arguments is not None and len(argument_names) > 0:
		args = []
		for idx, arg in enumerate(arguments):
			if idx < len(argument_names):
				args.append((arg, argument_names[idx]))
			else:
				args.append((arg, "..."))

	cmds[name] = (short_description, long_description, args, function)

def help_command(command: str | None = None) -> int:
	if command is not None:
		if command not in cmds.keys():
			print(f"No such command {command}")

			commands = levenshtein_sort_list(command, list(cmds.keys()))

			print(f"Did you mean: {list(cmds.keys())[commands[0][0]]}")

			return 0

		long_desc = cmds[command][1]
		command_args = cmds[command][2]
		print(f"Instructions for: {command}\n\n{long_desc}")

		if command_args is not None:
			print("\nArguments:")
			for arg in command_args:
				print(f"{arg[1]}: {arg[0]}")
	else:
		for item in cmds:
			print(f"{item} - {cmds[item][0]}")

	return 0

register_command(
	"help",
	"Gives documentation for all available commands.",
	"The help command will tell you all you need to know. To see more for a specific command, use help <command>.",
	["Command to see more documentation for"],
	help_command
)


def quit_command() -> int:
	print("\nSee ya next time")

	sys.exit()

register_command(
	"quit",
	"Close the game",
	"What is there to say? This closes the game.",
	None,
	quit_command
)


def lest_command() -> int:
	print("""                                  ..::                                                                  ::..                                  
                                  ,,::::                                                              ::::,,                                  
                                  ::..,,::                                                          ::,,..::                                  
                                ..::....,,::                                                      ::,,....::..                                
                                ,,::,,,,  ,,::                                                  ::,,,,::,,::,,                                
                                ,,,,::..    ,,::                                              ::,,,,::,,::,,,,                                
                                ::..::        ,,::                                          ::,,,,::..  ::..::                                
                              ..::,,,,          ,,::                                      ::,,,,::..    ,,,,::..                              
                              ,,,,::..            ,,::                                  ::,,,,::..      ..::,,,,                              
                              ::..::..      ..,,,,..,,::                              ::,,,,;;,,..      ..::..::                              
                              ::..::  ..,,::::::,,,,,,;;,,                          ,,;;,,,,,,::::::,,....::..::                              
                            ..::,,::::::,,,,,,::::::,,..                              ..,,::::::,,,,,,::::;;,,::..                            
                            ,,,,..,,,,::::::,,..                                              ..,,::::::,,,,..,,,,                            
                            ::::::::,,..                                                              ..,,::::::::                            
                            ,,..                  ....,,,,::::::::::::::::::::::::::,,,,....                  ..,,                            
                                          ..,,::::::::,,,,..........      ..........,,,,::::::::,,..                                          
  ::::,,..                          ,,::::::::,,..............................................,,::::::::,,                          ..,,::::  
    ..,,::::::,,..              ,,::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::,,              ..,,::::::,,..    
            ..,,::::,,      ..::,,..                                                                      ..,,::..      ,,::::,,..            
                  ..      ..::..                                  ,,,,::,,,,                                  ..::..      ..                  
                          ::..                                ..::::,,..,,::::..                                ..::                          
,,,,,,,,,,,,,,,,,,,,    ..::                                ..::..          ..::..                                ::..    ,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,    ..::                                ::..      ::      ..::                                ::..    ,,,,,,,,,,,,,,,,,,,,
                          ::..                            ..::        ;;        ::..                            ..::                          
                          ..::..                          ,,,,        ;;        ,,,,                          ..::..                          
            ..,,::::,,      ..::,,..                      ,,,,        ;;        ,,,,                      ..,,::..      ,,::::,,..            
    ..,,::::::,,..              ,,::::..                  ,,,,        ;;        ,,,,                  ..::::,,              ..,,::::::,,..    
  ::::,,..                          ,,::::::,,..          ..::        ;;        ::..          ..,,::::::,,                          ..,,::::  
                                          ..,,::::::::,,,,..::,,..  ..;;..  ..,,::..,,,,::::::::,,..                                          
                                                  ....,,,,::::::::::::::::::::::::::,,,,....                                                  
                                                                                                                                              
                                                              ,,::::::::::::::,,                                                              
                                                              ..::,,......,,::..                                                              
                                                                ..::..  ..::..                                                                
                                                                  ..::,,::..                                                                  
                                                                    ..::..                                                                    """)
	return 0

register_command(
	"lest",
	"All hail the great Lester",
	"Lester is the greatest cat in the history of all cats.",
	None,
	lest_command
)


def exec_command(input_text: str):
	if input_text == "":
		return
	else:
		input_text = input_text.strip().lower().split(" ")
		func = input_text[0]

		args = None
		if len(input_text) > 1:
			args = list(input_text[1:])

		commands = levenshtein_sort_list(func, list(cmds.keys()))

		if commands[0][1] == 0:
			if args is None:
				cmds[list(cmds.keys())[commands[0][0]]][3]()
			else:
				cmds[list(cmds.keys())[commands[0][0]]][3](*args)
		else:
			print(f"Did you mean: {list(cmds.keys())[commands[0][0]]}")