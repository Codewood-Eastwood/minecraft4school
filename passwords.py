# flake8: noqa: E501

global premium_passwords

premium_passwords: list[str] = [
    "caidon67",  # Caidon
    "mnn3gkczLnH4",  # Angad
    "ginger1",  # Andrew
    "vedsucks123",  # Vedanth
    "130iq",  # Zaid
]

def passwords():
    global premium_passwords

    PASSWORDS = [
        "grade3",
        "sixseven",
        "lovenatsuki",
        "angadssistersayshi"
    ]
    PASSWORDS.extend(
        premium_passwords
    )
    return PASSWORDS