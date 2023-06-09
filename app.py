import streamlit as st
import pandas as pd
import sqlite3

conn = sqlite3.connect('task_manager.db')

# Create the users table if it doesn't exist
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

# Create the tasks table if it doesn't exist
conn.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    task_description TEXT,
    task_deadline TEXT,
    task_repeat TEXT,
    team_members TEXT,
    task_status TEXT DEFAULT 'Pending'
)
''')

st.title('Task Manager Login')

# Add a registration page
if st.button('Register'):
    st.subheader('Create Admin Account')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    confirm_password = st.text_input('Confirm Password', type='password')
    if password != confirm_password:
        st.error('Password does not match the confirm password.')
    else:
        role = 'Admin'
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        conn.commit()
        st.success(f'Admin account for {username} created successfully. Please login.')

# Add a login page
else:
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        # Check if the username and password are correct
        user_data = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        if user_data:
            role = user_data[2]
            st.success(f'Logged in as {role}')
            if role == 'Admin':
                # Show the Admin dashboard
                st.title('Admin Dashboard')

                # Show a table of all the users and their roles
                users = pd.read_sql_query('SELECT username, role FROM users', conn)
                st.write(users)

                # Add a new user
                new_username = st.text_input('New Username')
                new_password = st.text_input('New Password', type='password')
                new_role = st.selectbox('New Role', ['Team Head', 'Team Member'])
                if st.button('Add User'):
                    conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (new_username, new_password, new_role))
                    conn.commit()
                    st.success('User added successfully')
                    users = pd.read_sql_query('SELECT username, role FROM users', conn)
                    st.write(users)

                # Delete a user
                delete_username = st.selectbox('Select User to Delete', users['username'].tolist())
                if st.button('Delete User'):
                    conn.execute('DELETE FROM users WHERE username=?', (delete_username,))
                    conn.commit()
                    st.success('User deleted successfully')
                    users = pd.read_sql_query('SELECT username, role FROM users', conn)
                    st.write(users)

                # Update a user's role
                update_username = st.selectbox('Select User to Update', users['username'].tolist())
                update_role = st.selectbox('New Role', ['Team Head', 'Team Member'])
                if st.button('Update Role'):
                    conn.execute('UPDATE users SET role=? WHERE username=?', (update_role, update_username))
                    conn.commit()
                    st.success('Role updated successfully')
                    users = pd.read_sql_query('SELECT username, role FROM users', conn)
                    st.write(users)
            elif role == 'Team Head':
                # Show the Team Head dashboard
                st.title('Team Head Dashboard')
                # Show a table of all the tasks assigned to the team
                tasks = pd.read_sql_query('SELECT * FROM tasks WHERE team_members LIKE ?', (f'%{username}%',))
                st.write(tasks)

                # Add a new task
                task_name = st.text_input('Task Name')
                task_description = st.text_area('Task Description')
                task_deadline = st.text_input('Task Deadline (YYYY-MM-DD)')
                task_repeat = st.selectbox('Task Repeat', ['', 'Daily', 'Weekly', 'Monthly'])
                team_members = st.multiselect('Assign to Team Members', pd.read_sql_query('SELECT username FROM users WHERE role=?', conn, params=('Team Member',))['username'].tolist())
                if st.button('Add Task'):
                   team_members_str = ','.join(team_members)
                   conn.execute('INSERT INTO tasks (task_name, task_description, task_deadline, task_repeat, team_members) VALUES (?, ?, ?, ?, ?)', (task_name, task_description, task_deadline, task_repeat, team_members_str))
                   conn.commit()
                   st.success('Task added successfully')
                   tasks = pd.read_sql_query('SELECT * FROM tasks WHERE team_members LIKE ?', (f'%{username}%',))
                   st.write(tasks)

                # Delete a task
                delete_task_id = st.selectbox('Select Task to Delete', tasks['id'].tolist())
                if st.button('Delete Task'):
                   conn.execute('DELETE FROM tasks WHERE id=?', (delete_task_id,))
                   conn.commit()
                   st.success('Task deleted successfully')
                   tasks = pd.read_sql_query('SELECT * FROM tasks WHERE team_members LIKE ?', (f'%{username}%',))
                   st.write(tasks)

                # Update a task's status
                update_task_id = st.selectbox('Select Task to Update', tasks['id'].tolist())
                update_task_status = st.selectbox('New Status', ['Pending', 'In Progress', 'Completed'])
                if st.button('Update Status'):
                   conn.execute('UPDATE tasks SET task_status=? WHERE id=?', (update_task_status, update_task_id))
                   conn.commit()
                   st.success('Status updated successfully')
                   tasks = pd.read_sql_query('SELECT * FROM tasks WHERE team_members LIKE ?', (f'%{username}%',))
                   st.write(tasks)

            elif role == 'Team Member':
                # Show the Team Member dashboard
                st.title('Team Member Dashboard')

                # Show a table of all the tasks assigned to the team member
                tasks = pd.read_sql_query('SELECT * FROM tasks WHERE team_members LIKE ?', (f'%{username}%',))
                st.write(tasks)

                # Update a task's status
                update_task_id = st.selectbox('Select Task to Update', tasks['id'].tolist())
                update_task_status = st.selectbox('New Status', ['Pending', 'In Progress', 'Completed'])
                if st.button('Update Status'):
                   conn.execute('UPDATE tasks SET task_status=? WHERE id=?', (update_task_status, update_task_id))
                   conn.commit()
                   st.success('Status updated successfully')
                   tasks = pd.read_sql_query('SELECT * FROM tasks WHERE team_members LIKE ?', (f'%{username}%',))
                   st.write(tasks)

        else:
            st.error('Incorrect username or password')

