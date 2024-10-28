import sqlite3
from datetime import datetime
import getpass

# Initialize and create a new SQLite database connection
def initialize_database():
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()

    # Create candidates table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        votes INTEGER DEFAULT 0
    )
    ''')

    # Create voters table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id TEXT UNIQUE NOT NULL,
        has_voted INTEGER DEFAULT 0
    )
    ''')

    # Create logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id TEXT NOT NULL,
        candidate_name TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')

    conn.commit()
    return conn, cursor

# Call the initialization function
conn, cursor = initialize_database()

ADMIN_PASSWORD = "arsh@11"  # Change this as needed

# Add a candidate to the database
def add_candidate(name):
    try:
        cursor.execute("INSERT INTO candidates (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Candidate '{name}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Candidate '{name}' already exists.")

# Register a new voter
def register_voter(voter_id):
    try:
        cursor.execute("INSERT INTO voters (voter_id) VALUES (?)", (voter_id,))
        conn.commit()
        print(f"Voter '{voter_id}' registered successfully.")
    except sqlite3.IntegrityError:
        print(f"Voter '{voter_id}' is already registered.")

# Cast a vote, ensuring the voter hasn't already voted
def cast_vote(voter_id, candidate_name):
    cursor.execute("SELECT has_voted FROM voters WHERE voter_id=?", (voter_id,))
    voter = cursor.fetchone()

    if not voter:
        print(f"Voter '{voter_id}' is not registered.")
        return

    if voter[0] == 1:
        print(f"Voter '{voter_id}' has already voted.")
        return

    cursor.execute("SELECT * FROM candidates WHERE name=?", (candidate_name,))
    candidate = cursor.fetchone()

    if not candidate:
        print(f"Candidate '{candidate_name}' not found.")
        return

    cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE name=?", (candidate_name,))
    cursor.execute("UPDATE voters SET has_voted = 1 WHERE voter_id=?", (voter_id,))
    cursor.execute("INSERT INTO logs (voter_id, candidate_name, timestamp) VALUES (?, ?, ?)",
                   (voter_id, candidate_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    print(f"Vote cast for '{candidate_name}' by '{voter_id}'.")

# Show voting results
def show_results():
    cursor.execute("SELECT name, votes FROM candidates ORDER BY votes DESC")
    results = cursor.fetchall()
    print("\nVoting Results:")
    for name, votes in results:
        print(f"{name}: {votes} votes")

# View voting logs (Admin only)
def view_logs():
    cursor.execute("SELECT * FROM logs")
    logs = cursor.fetchall()
    print("\nVoting Logs:")
    for log in logs:
        print(f"Voter: {log[1]}, Candidate: {log[2]}, Time: {log[3]}")

# Reset the voting system (Admin only)
def reset_data():
    cursor.execute("DELETE FROM candidates")
    cursor.execute("DELETE FROM voters")
    cursor.execute("DELETE FROM logs")
    conn.commit()
    print("All data has been reset.")

# Verify admin password for restricted operations
def admin_login():
    password = getpass.getpass("Enter admin password: ")
    if password == ADMIN_PASSWORD:
        return True
    else:
        print("Invalid password.")
        return False

# Main function to run the voting system
def main():
    while True:
        print("\n1. Register Voter")
        print("2. Add Candidate (Admin Only)")
        print("3. Cast Vote")
        print("4. Show Results")
        print("5. View Logs (Admin Only)")
        print("6. Reset Data (Admin Only)")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            voter_id = input("Enter voter ID: ")
            register_voter(voter_id)

        elif choice == '2':
            if admin_login():
                name = input("Enter candidate name: ")
                add_candidate(name)

        elif choice == '3':
            voter_id = input("Enter your voter ID: ")
            candidate_name = input("Enter candidate name: ")
            cast_vote(voter_id, candidate_name)

        elif choice == '4':
            show_results()

        elif choice == '5':
            if admin_login():
                view_logs()

        elif choice == '6':
            if admin_login():
                reset_data()

        elif choice == '7':
            print("Exiting the voting system.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

# Close the database connection when the program exits
conn.close()
