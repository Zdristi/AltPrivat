import sqlite3
from datetime import datetime
import os

def connect_db():
    """Establish connection to the database."""
    return sqlite3.connect('users.db')

def view_all_users():
    """View all users in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, subscription_expires, is_subscribed FROM users")
    users = cursor.fetchall()
    
    print("All users in the database:")
    print("User ID | Subscription Expires | Is Subscribed")
    print("-" * 50)
    
    for user in users:
        print(f"{user[0]} | {user[1]} | {user[2]}")
    
    conn.close()

def check_user_subscription(user_id):
    """Check if a specific user has an active subscription."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT is_subscribed, subscription_expires FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        is_sub, expires = result
        if is_sub and datetime.now().date() <= datetime.fromisoformat(expires).date():
            print(f"User {user_id} has an active subscription until {expires}")
            return True
        else:
            print(f"User {user_id} subscription expired on {expires}")
            return False
    else:
        print(f"User {user_id} not found in database")
        return False

def add_user(user_id, days=30):
    """Manually add a user with a subscription."""
    from datetime import timedelta
    
    conn = connect_db()
    cursor = conn.cursor()
    
    expiration_date = (datetime.now() + timedelta(days=days)).date()
    
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, subscription_expires, is_subscribed)
        VALUES (?, ?, 1)
    """, (user_id, expiration_date))
    
    conn.commit()
    conn.close()
    
    print(f"Added/updated user {user_id} with subscription until {expiration_date}")

def remove_user(user_id):
    """Remove a user from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    
    if cursor.rowcount > 0:
        print(f"Removed user {user_id} from database")
    else:
        print(f"User {user_id} not found in database")
    
    conn.commit()
    conn.close()

def main():
    print("Database Management Tool")
    print("Commands:")
    print("1. view - View all users")
    print("2. check <user_id> - Check specific user subscription")
    print("3. add <user_id> [days] - Add user with subscription (default 30 days)")
    print("4. remove <user_id> - Remove user from database")
    
    while True:
        command = input("\nEnter command: ").strip().split()
        
        if not command:
            continue
            
        if command[0] == "view":
            view_all_users()
        elif command[0] == "check" and len(command) >= 2:
            try:
                user_id = int(command[1])
                check_user_subscription(user_id)
            except ValueError:
                print("Invalid user ID")
        elif command[0] == "add" and len(command) >= 2:
            try:
                user_id = int(command[1])
                days = int(command[2]) if len(command) > 2 else 30
                add_user(user_id, days)
            except ValueError:
                print("Invalid user ID or days")
        elif command[0] == "remove" and len(command) >= 2:
            try:
                user_id = int(command[1])
                remove_user(user_id)
            except ValueError:
                print("Invalid user ID")
        elif command[0] in ["exit", "quit"]:
            break
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()