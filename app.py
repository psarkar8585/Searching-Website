from flask import Flask, request, redirect, url_for, render_template, abort
import psycopg2

app = Flask(__name__)

# Database connection parameters
hostname = 'localhost'
database = 'item'
username = 'postgres'
password = '1234'
port_id = 5432

def get_db_connection():
    """Establish and return a database connection."""
    conn = psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=password,
        port=port_id
    )
    print("Connection to the database established successfully.")
    return conn

@app.route('/', methods=['GET']) 
def index():
    print("jjj")
    return render_template('index.html')

@app.route('/item_list', methods=['GET'])
def item_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT distinct name, author,id from additem")
    items = cursor.fetchall()
    cursor.close()
    conn.close() 
    return render_template('itemlist.html',items1=items)
    
@app.route("/data/<section>")
def data(section):
    return "hi "+section

@app.route('/add_item', methods=['GET', 'POST']) 
def add_item():
    try:
        conn = None
        cur = None
        if request.method == 'POST':
            print("sbvfheg")
            # Get form data
            name = request.form['name']
            author = request.form['author'] if request.form['author']  else None
            # if author is None:
            print(author)    
            #     print(name,author)  
            conn = get_db_connection()
            cur = conn.cursor()

            # Create table if it doesn't exist
            create_table = '''
            CREATE TABLE IF NOT EXISTS additem (
                name VARCHAR(50),
                author VARCHAR(50)
            )
            '''
            cur.execute(create_table)
            # Insert data into the table
            insert_data = 'INSERT INTO additem(name, author) VALUES(%s, %s)'
            insert_values = (name, author)
            cur.execute(insert_data, insert_values)
            
            # Commit the transaction
            conn.commit()
            return redirect('/item_list')
        else:
            print("hrugouspoooooooooo")
            return render_template('additem.html')
        
    except Exception as error:
        print("Error:", error)
        return "An error occurred while processing your request."
    
    finally:
        # Close cursor and connection
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM additem WHERE name ILIKE %s or author ILIKE %s;', (f'%{query}%',f'%{query}%'))
    items = cur.fetchall()
    cur.close()
    conn.close()
    print(f"Search query: {query}")
    print(f"Search results: {items}")
    
    if not items:
        print("hello")
        return render_template('itemlist.html', message="No items found.")
    return render_template('itemlist.html', item1=items)
 
#view 
@app.route('/item/<_id>', methods=['GET'])
def view_item(_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT  name, author FROM additem WHERE id = %s', (_id,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    if item is None:
        abort(404)
    return render_template('view.html', item=item)

#Update
@app.route('/item/<int:_id>/update', methods=['GET', 'POST'])
def update_item(_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        author = request.form['author']
        
        # Update item in the database
        update_query = '''
        UPDATE additem
        SET name = %s, author = %s
        WHERE id = %s
        '''
        cur.execute(update_query, (name, author, _id))
        conn.commit()
        
        cur.close()
        conn.close()

        # Redirect to the view page of the updated item
        return redirect(url_for('item_list'))

    else:
        # Retrieve the item from the database
        cur.execute('SELECT name, author FROM additem WHERE id = %s', (_id,))
        item = cur.fetchone()
        
        cur.close()
        conn.close()

        if item is None:
            abort(404)
        return render_template('update.html', item=item, _id=_id)

# delete API
@app.route('/item/<int:_id>/delete', methods=['POST','GET'])
def delete_item(_id):
    conn = None
    cur = None
    try:
        if request.method == 'POST':
            # Establish database connection
            conn = get_db_connection()
            cur = conn.cursor()

            # Execute the delete query
            delete_query = '''
            DELETE FROM additem
            WHERE id = %s
            '''
            cur.execute(delete_query, (_id,))
            conn.commit()

            # Redirect to the item list after deletion
            return redirect(url_for('item_list'))

        else:
            # Handle unexpected HTTP methods
            return render_template('delete.html') # Method Not Allowed

    except Exception as error:
        import traceback
        traceback.print_exc()
        print("Error:", error)
        return "An error occurred while processing your request.", 500

    finally:
        # Ensure resources are released
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)