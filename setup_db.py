from modules.user_auth import init_auth_db, create_test_user

# Initialize the database
init_auth_db()

# Create a test user (optional)
success, message = create_test_user('admin', 'password123', 'admin@example.com')
print(message)

print("Database setup complete! The users database has been created at data/users.db") 