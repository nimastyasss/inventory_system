from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import config

app = Flask(__name__)
app.config.from_object(config.Config)
mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM items')
    items = cur.fetchall()
    cur.close()
    return render_template('index.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO items (name, quantity, price) VALUES (%s, %s, %s)', (name, quantity, price))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/view_item/<int:item_id>')
def view_item(item_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM items WHERE id = %s', (item_id,))
    item = cur.fetchone()
    cur.close()
    return render_template('view_item.html', item=item)

@app.route('/edit_item', methods=['POST'])
def edit_item():
    item_id = request.form['id']
    name = request.form['name']
    quantity = request.form['quantity']
    price = request.form['price']
    
    cur = mysql.connection.cursor()
    cur.execute('UPDATE items SET name = %s, quantity = %s, price = %s WHERE id = %s', (name, quantity, price, item_id))
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('index'))

@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    cur = mysql.connection.cursor()
    # Hapus item dari tabel
    cur.execute('DELETE FROM items WHERE id = %s', (item_id,))
    mysql.connection.commit()

    # Perbarui ID item yang tersisa agar berurutan
    cur.execute('SET @rownum := 0;')
    cur.execute('UPDATE items SET id = @rownum := @rownum + 1 ORDER BY id;')
    
    # Setel ulang nilai AUTO_INCREMENT
    cur.execute('SET @max_id = (SELECT MAX(id) FROM items);')
    cur.execute('SET @auto_increment_value = @max_id + 1;')
    cur.execute('SET @query = CONCAT("ALTER TABLE items AUTO_INCREMENT = ", @auto_increment_value);')
    cur.execute('PREPARE stmt FROM @query;')
    cur.execute('EXECUTE stmt;')
    cur.execute('DEALLOCATE PREPARE stmt;')

    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
