from flask import Flask, render_template, request, url_for, flash, redirect
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'test'
}

app.secret_key = '11223344'  # Required for flash messages

# Initialize Database
def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todo (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            task VARCHAR(100) NOT NULL, 
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# Home Route - Display Tasks
@app.route('/')
def index():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todo")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', tasks=tasks)
@app.route('/complete/<int:task_id>', methods=['POST'])
def complete(task_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE todo SET completed = NOT completed WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return '', 204
# Add Task
@app.route('/add', methods=['POST'])
def add():
    task = request.form['task']
    if not task:
        flash("Task cannot be empty!", "warning")
        return redirect(url_for('index'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todo(task) VALUES (%s)", (task,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Task Added Successfully!", "success")
    return redirect(url_for('index'))

# Update Task (Show Edit Form)
@app.route('/update/<int:task_id>', methods=['GET', 'POST'])
def update(task_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    if request.method == 'POST':
        new_task = request.form['task']
        cursor.execute("UPDATE TABLE todo set task = %s WHERE id = %s",(new_task,task_id))
        conn.commit()
        cursor.close()
        conn.close()
    # Fetch existing task for pre-filling in update form
    cursor.execute("SELECT * FROM todo WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('update.html', task=task)

# Delete Task
@app.route('/delete/<int:task_id>')
def delete(task_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todo WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Task Deleted Successfully!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
