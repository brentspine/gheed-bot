import time

def format_cookies(cookies_str):
    cookies = {}
    cookie_list = cookies_str.split("; ")
    for cookie in cookie_list:
        key, value = cookie.split("=")
        cookies[key] = value
    return cookies
    
def print_entry(entry):
    print("{")
    print("    \"cookies\": {")
    for key, value in entry["cookies"].items():
        print(f'      "{key}": "{value}",')
    print("    },")
    print(f'    "last_refresh": {entry["last_refresh"]},')
    print(f'    "username": "{entry["username"]}",')
    print(f'    "mail": "{entry["mail"]}",')
    print(f'    "password": "{entry["password"]}"')
    print("},") 

def main():
    entries = []

    while True:
        username_input = input("Enter username: ")
        mail_input = input("Enter mail: ")
        password_input = input("Enter password: ")
        cookies_input = input("Paste cookies: ")

        entry = {
            "cookies": format_cookies(cookies_input),
            "last_refresh": time.time(),
            "username": username_input,
            "mail": mail_input,
            "password": password_input
        }

        print_entry(entry)

        entries.append(entry)

        next_action = input("Type 'exit' to stop, press Enter to continue: ")
        if next_action.lower() == 'exit':
            break
    for entry in entries:
        print_entry(entry)

if __name__ == "__main__":
    main()
