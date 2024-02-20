import nationstates
import config
import re


def GetUserClient() -> nationstates.Nationstates:
    current_user = input("Please enter the nation using this script.")
    return nationstates.Nationstates(f"{current_user} using WA voting bloc tool by Deims Kir (credit dragoe)")

def Canonicalise(string : str) -> str:
    return string.strip().replace(" ", "_").lower()

def ParseCommand(command : str) -> tuple[str, list, list]:
    """Splits a command into the actual command, the flags for the command, and arguments for the command."""

    tokenised_command : list[str] = [x.strip() for x in command.split()]

    actual_command : str = tokenised_command[0]
    flags          : list = [x for x in tokenised_command if x.startswith("--")]
    arguments      : list = [[Canonicalise(x) for x in arg] for arg in [item.split(",") for item in re.findall(r"(?<=\[).+?(?=\])", command)]]
    
    if actual_command not in config.commands_list.keys():
        return -1, f"Invalid command: '{actual_command}'"
    
    if any((flag := x) not in config.acceptable_flags[actual_command] for x in flags):
        return -1, f"Invalid flag ('{flag}') provided for command: '{actual_command}'"
    
    return (actual_command, flags, arguments)

def Main() -> None:

    client = GetUserClient()

    while True:
        command_selected = input("Enter a command, or enter 'help' to view a list of commands.\n").lower()
        print()

        parsed_output = ParseCommand(command_selected)

        if parsed_output[0] == -1:
            print(parsed_output[1])
            continue
        else:
            command, flags, arguments = parsed_output

        if command != "exit":
            result = config.commands_list[command](client, flags, arguments)

            if isinstance(result, str):
                print(result)
            elif result == 0:
                print("Command execution successful")
            elif result[0] == -1:
                print(f"An error occured: {result[1]}")
            print()
            
            continue

        return


if __name__ == "__main__":
    Main()
