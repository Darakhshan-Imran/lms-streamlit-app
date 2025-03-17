# import os
# import hashlib
# import subprocess
# import psycopg2-binary


# DATABASE_URL = "postgresql://neon_db_owner:npg_YyF74kuOtCQD@ep-shrill-glitter-a129ejxy-pooler.ap-southeast-1.aws.neon.tech/lms?sslmode=require"


# AUTHORIZED_USER_HASHES = {"user_hash"}  

# def get_machine_hash():
#     """Generate a unique hash based on the machine's username."""
#     try:
#         identifier = os.getlogin()
#         return hashlib.sha256(identifier.encode()).hexdigest()
#     except Exception:
#         return None

# def get_git_username():
#     """Retrieve the GitHub username from the Git config."""
#     try:
#         result = subprocess.run(["git", "config", "--global", "user.name"], capture_output=True, text=True)
#         username = result.stdout.strip()
#         return username if username else "Unknown"
#     except Exception:
#         return "Error retrieving username"

# def get_git_email():
#     """Retrieve the GitHub email from the Git config."""
#     try:
#         result = subprocess.run(["git", "config", "--global", "user.email"], capture_output=True, text=True)
#         email = result.stdout.strip()
#         return email if email else "Unknown"
#     except Exception:
#         return "Error retrieving email"

# def log_unauthorized_user():
#     """Save the unauthorized user's GitHub info in the Neon PostgreSQL database."""
#     cloner_username = get_git_username()
#     cloner_email = get_git_email()

#     try:
#         conn = psycopg2.connect(DATABASE_URL)
#         cursor = conn.cursor()
        
#         # Ensure table exists
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS unauthorized_users (
#                 id SERIAL PRIMARY KEY,
#                 username TEXT NOT NULL,
#                 email TEXT NOT NULL,
#                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#         """)
        
#         # Insert unauthorized user details
#         cursor.execute("INSERT INTO unauthorized_users (username, email) VALUES (%s, %s)", (cloner_username, cloner_email))
        
#         conn.commit()
#         cursor.close()
#         conn.close()

#         # print(f"🚨 Unauthorized access logged: Username={cloner_username}, Email={cloner_email}")
    
#     except Exception as e:
#         print(f"⚠️ Error logging unauthorized user: {e}")

# def enforce_access_control():
#     """Verify user authorization and delete unauthorized files if necessary."""
#     if get_machine_hash() not in AUTHORIZED_USER_HASHES:
#         # print("🚨 Unauthorized access detected! Logging details & removing project files... 🚨")

#         # Log unauthorized user before taking action
#         log_unauthorized_user()

#         # Securely delete all project files
#         project_dir = os.path.dirname(os.path.abspath(__file__))

#         for root, dirs, files in os.walk(project_dir, topdown=False):
#             for file in files:
#                 try:
#                     os.remove(os.path.join(root, file))
#                 except Exception as e:
#                     print(f"Error deleting file {file}: {e}")
#             for dir in dirs:
#                 try:
#                     os.rmdir(os.path.join(root, dir))
#                 except Exception as e:
#                     print(f"Error deleting directory {dir}: {e}")

#         # print("🔥 Project files have been securely deleted. Unauthorized users cannot access this code. 🔥")
#         exit()
