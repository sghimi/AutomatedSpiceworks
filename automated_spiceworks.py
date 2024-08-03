import requests
from bs4 import BeautifulSoup
import json
import getpass


session = requests.Session()

# Gets CSRF token from response (HTML) + userID variable set
def get_csrf_token(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})
    
    return csrf_token['content'] if csrf_token else None

def get_chdUser_id(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', text=lambda t: t and 'var chdUserId' in t)
    if script_tag:
        script_content = script_tag.string
        start = script_content.find("var chdUserId = '") + len("var chdUserId = '")
        end = script_content.find("';", start)
        chdUserId = script_content[start:end]
        return chdUserId
    return None

# Function to perform the initial GET request and extract CSRF token
def initial_get_request(url, headers):
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        print("Initial request successful")
        csrf_token = get_csrf_token(response)
        if csrf_token:
            print("Authentication token:", csrf_token)
            return csrf_token
        else:
            print("CSRF token not found in the response.")
            exit()
    else:
        print("Initial request failed with status code:", response.status_code)
        exit()

# Function to perform the POST login request
def login_post_request(url, headers, data):
    response = session.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("Login POST request successful")
        chdUserId = get_chdUser_id(response)
        print("UserID: ", chdUserId)
        return chdUserId
    else:
        print("Login POST request failed with status code:", response.status_code)
        exit()

# Function to perform the subsequent GET request
def next_get_request(url, headers):
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        print("Next GET request successful")
        csrf_token = get_csrf_token(response)
        if csrf_token:
            print("CSRF token:", csrf_token)
            return csrf_token
        else:
            print("CSRF token not found in the response.")
            exit()
    else:
        print("Next GET request failed with status code:", response.status_code)
        exit()

# Add comment on ticket post request
def add_comment(ticket_number, message, csrf_token):
    comment_url = f"https://on.spiceworks.com/api/tickets/{ticket_number}/comments"
    comment_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": f"https://on.spiceworks.com/tickets/my_tickets/1?sort=updated_at-desc&ticket_number={ticket_number}",
        "X-CSRF-Token": csrf_token,
        "Content-Type": "application/json",
        "Origin": "https://on.spiceworks.com"
    }

    comment_json_data = {
        "ticket_comment": {
            "activity_type": "comment",
            "body": message,
            "initial_upload_ids": []
        }
    }

    response = session.post(comment_url, headers=comment_headers, json=comment_json_data)
    print("Comment request status code:", response.status_code)

# Create ticket post request
def create_ticket(title, description, csrf_token):
    final_url = "https://on.spiceworks.com/api/main/tickets"
    final_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://on.spiceworks.com/tickets/unassigned/1?sort=updated_at-desc",
        "X-CSRF-Token": csrf_token,
        "Content-Type": "application/json",
        "Origin": "https://on.spiceworks.com"
    }

    json_data = {
        "ticket": {
            "assignee_id": 1191447,
            "creator_id": 1191447,
            "creator_type": "User",
            "custom_values": [
                {"custom_attribute_id": 556393, "custom_attribute_type": "list", "ticket_id": None, "value": ""},
                {"custom_attribute_id": 556394, "custom_attribute_type": "list", "ticket_id": None, "value": ""},
                {"custom_attribute_id": 556395, "custom_attribute_type": "list", "ticket_id": None, "value": ""},
                {"custom_attribute_id": 556396, "custom_attribute_type": "list", "ticket_id": None, "value": ""}
            ],
            "description": title,
            "initial_upload_ids": [],
            "organization_id": 744757,
            "priority": 2,
            "summary": description,
            "ticket_category_id": None
        }
    }

    response = session.post(final_url, headers=final_headers, json=json_data)
    print("Final POST request status code: ", response.status_code)



#CLI logic

def main_menu():
    while True:
        print("\nSpiceworks CLI Menu")
        print("1. Edit Ticket")
        print("2. Create Ticket")
        print("3. Exit")
        
        choice = input("\nSelect an option: ")

        if choice == "1":
            edit_ticket()
        elif choice == "2":
            create_ticket()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("\nInvalid choice. Please select again.")

def edit_ticket():
    ticket_number = input("Enter ticket number: ")
    message = input("Enter the message: ")
    add_comment(ticket_number, message, csrf_token)

def main_menu():
    while True:
        print("\nSpiceworks CLI Menu")
        print("1. Edit Ticket")
        print("2. Create Ticket")
        print("3. Exit")
        
        choice = input("Select an option: ")

        if choice == "1":
            edit_ticket()
        elif choice == "2":
            create_new_ticket()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select again.")

def edit_ticket():
    ticket_number = input("Enter ticket number: ")
    message = input("Enter the message: ")
    add_comment(ticket_number, message, csrf_token)

def create_new_ticket():
    title = input("Enter the title:\n")
    description = input("Enter the description:\n")
    create_ticket(title, description, csrf_token)


# Main code execution + authentication
if __name__ == "__main__":
    initial_url = "https://accounts.spiceworks.com/sign_in?policy=hosted_help_desk&success=https://on.spiceworks.com"
    initial_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
        "TE": "trailers"
    }

    authentication_token = initial_get_request(initial_url, initial_headers)

    post_url = "https://accounts.spiceworks.com/sign_in.json"
    post_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": initial_url,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://accounts.spiceworks.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "TE": "trailers"
    }

    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")

    form_data = {
        "email": email,
        "password": password,
        "referer": "/sign_in?policy=hosted_help_desk&success=https://on.spiceworks.com",
        "authenticity_token": authentication_token,
        "sso": "",
        "sig": "",
        "success": "https://on.spiceworks.com",
        "permission_denied": "https://accounts.spiceworks.com/",
        "policy": "hosted_help_desk"
    }

    chdUserId = login_post_request(post_url, post_headers, form_data)

    next_url = "https://on.spiceworks.com/tickets/unassigned/1?sort=updated_at-desc"
    next_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://accounts.spiceworks.com/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
        "TE": "trailers"
    }

    csrf_token = next_get_request(next_url, next_headers)
    
    print("chdUserId:", chdUserId)
    main_menu()