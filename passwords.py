# passwords.py
# flake8: noqa: E501

import json
import os

PASSWORDS_FILE = "passwords_data.json"

premium_passwords = [
    {"name": "Premium 1", "password": "kindcar13"},
    {"name": "Premium 2", "password": "jadeheat_30"},
    {"name": "Admin", "password": "mnn3gkczLnH4"}
]

PREMIUM_MARK = "__PREMIUM__"

def _load_passwords():
    if not os.path.exists(PASSWORDS_FILE):
        # Default passwords
        passwords = [
            {"name": "User", "password": "basicpassword"}
        ] + premium_passwords
        _save_passwords(passwords)
        return passwords
    with open(PASSWORDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_passwords(passwords):
    with open(PASSWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(passwords, f, indent=2)

def get_passwords() -> list[dict]:
    return _load_passwords()

def add_password(name: str, password: str):
    passwords = _load_passwords()
    # Prevent duplicate names
    if any(entry['name'] == name for entry in passwords):
        raise ValueError("A password with this name already exists.")
    passwords.append({"name": name, "password": password})
    _save_passwords(passwords)

def edit_password(old_name: str, new_name: str, new_password: str):
    passwords = _load_passwords()
    found = False
    for entry in passwords:
        if entry['name'] == old_name:
            entry['name'] = new_name
            entry['password'] = new_password
            found = True
            break
    if not found:
        raise ValueError("Password entry not found.")
    _save_passwords(passwords)

def delete_password(name: str):
    passwords = _load_passwords()
    new_passwords = [entry for entry in passwords if entry['name'] != name]
    if len(new_passwords) == len(passwords):
        raise ValueError("Password entry not found.")
    _save_passwords(new_passwords)

def get_premium_passwords() -> list[dict]:
    return [entry for entry in _load_passwords() if entry.get('premium')]

def add_premium_password(name: str, password: str):
    passwords = _load_passwords()
    if any(entry['name'] == name for entry in passwords):
        raise ValueError("A password with this name already exists.")
    passwords.append({"name": name, "password": password, "premium": True})
    _save_passwords(passwords)

def edit_premium_password(old_name: str, new_name: str, new_password: str):
    passwords = _load_passwords()
    found = False
    for entry in passwords:
        if entry['name'] == old_name and entry.get('premium'):
            entry['name'] = new_name
            entry['password'] = new_password
            found = True
            break
    if not found:
        raise ValueError("Premium password entry not found.")
    _save_passwords(passwords)

def delete_premium_password(name: str):
    passwords = _load_passwords()
    new_passwords = [entry for entry in passwords if not (entry['name'] == name and entry.get('premium'))]
    if len(new_passwords) == len(passwords):
        raise ValueError("Premium password entry not found.")
    _save_passwords(new_passwords)
