# hash_passwords.py
import streamlit_authenticator as stauth

# Step 1: List of plain text passwords
passwords = ["password123", "adminpass", "viewerpass"]

# Step 2: Hash them
hashed_passwords = stauth.Hasher(passwords).generate()

# Step 3: Print them
print("Hashed Passwords:")
for hp in hashed_passwords:
    print(hp)
