import argparse
import random
import string

# Class to create a custom help message (i.e. The output of >> create_password -h)
class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        pass
    def add_arguments(self, actions):
        pass

def get_available_chars(omit_chars=None, include_chars=None):

    available_chars = string.ascii_letters + string.digits + string.punctuation

    if omit_chars:
        chars = ''.join(c for c in available_chars if c not in omit_chars)
        available_chars = chars
    if include_chars:
        chars = ''.join(c for c in available_chars if c in include_chars)
        available_chars = chars

    return available_chars

def generate_password(length, omit_chars=None, include_chars=None):

    available_chars = get_available_chars(omit_chars, include_chars)
    
    if not available_chars:
        raise ValueError("No characters available after omitting specified characters.")
    
    password = ''

    for _ in range(length):

        if len(available_chars) < 1:
            
            available_chars = get_available_chars(omit_chars, include_chars)
        
        random_char = random.choice(available_chars)
        password += random_char

        available_chars = available_chars.replace(random_char, '')
    
    return password

def main():
    passwords_str_example = "\033[1m\033[32m" + "\n".join(["CqmW}$Kaj3P-PCJ", 
                                                   "b;%Kv(q7%>)M,3h", 
                                                   "b1i(L]~:F4DDg/d", 
                                                   "L&|X0VFVZg#e\\HO"]) + "\033[0m"
    
    ArgumentParser_desc = (
    " \nGenerates a random password.\n"
    "Here's an example command to print 4 random passwords of length 15 and omit the characters (*+^) in each of them:\n\n"
    ">> password -n 4 -l 15 -o *+^\n\n"
    f"Will return something like: \n\n{passwords_str_example}\n\n"
    "The default command is:\n"
    ">> password -n 1 -l 12 (prints 1 password of length 12)\n\n "
    "The arguments are:\n "
    "-l (or --password_length): sets the password length\n "
    "-o (or --characters_to_omit): sets the characters to omit (cannot be used with the -i argument)\n "
    "-i (or --characters_to_include): sets the character to include (cannot be used with the -o argument)\n "
    "-n (or --password_number): sets how many passwords to return\n "
)

    parser = argparse.ArgumentParser(
        description=ArgumentParser_desc,
        formatter_class=CustomHelpFormatter,
        add_help=True
    )

    group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "-l",
        "--password_length",
        type=int,
        nargs="?",
        default=12,
        help="Length of the password (default: 12)"
    )
    group.add_argument(
        "-o",
        "--characters_to_omit",
        type=str,
        nargs="?",
        default="",
        help="Characters to exclude from the password (default: none)"
    )
    group.add_argument(
        "-i",
        "--characters_to_include",
        type=str,
        nargs="?",
        default="",
        help="Characters to exclude from the password (default: none)"
    )
    parser.add_argument(
        "-n",
        "--password_number",
        type=int,
        nargs="?",
        default=1,
        help="Number of passwords to show (default: 1)"
    )
    
    args = parser.parse_args()
    
    try:
        passwords = [generate_password(args.password_length, args.characters_to_omit, args.characters_to_include) for _ in range(args.password_number)]

        print(f"\n")

        for password in passwords:
            print(f"\033[1m\033[32m{password}\033[0m")

        print(f"\n")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()