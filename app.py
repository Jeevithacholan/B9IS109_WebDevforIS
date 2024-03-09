import os
from flask import Flask, render_template
from flask_pymongo import PyMongo
from bson import ObjectId
from flask import jsonify
from flask import request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'myPassword@1'  # Set a secret key for session management
app.config['MONGO_URI'] = 'mongodb://localhost:27017/jee'  # Update to your database name
mongo = PyMongo(app)


@app.route('/')
def index():
    products = mongo.db.testdata.find()  # Update to your collection name
    return render_template('index.html', products=products)


@app.route('/product/<string:product_id>')
def product_detail(product_id):
    product = mongo.db.testdata.find_one({'_id': ObjectId(product_id)})  # Convert product_id to ObjectId
    print(product)
    return render_template('product_detail.html', product=product)


@app.route('/nextProduct/<string:product_id>')
def next_product(product_id):
    current_product = mongo.db.testdata.find_one({'_id': ObjectId(product_id)})
    if current_product:
        next_product = mongo.db.testdata.find_one({'_id': {'$gt': ObjectId(product_id)}})
        if next_product:
            return jsonify({'product_id': str(next_product['_id'])})
    return jsonify({'product_id': product_id})  # Return the current product's id if no next product is found


@app.route('/prevProduct/<string:product_id>')
def prev_product(product_id):
    current_product = mongo.db.testdata.find_one({'_id': ObjectId(product_id)})
    if current_product:
        prev_product = mongo.db.testdata.find_one({'_id': {'$lt': ObjectId(product_id)}})
        if prev_product:
            return jsonify({'product_id': str(prev_product['_id'])})
    return jsonify({'product_id': product_id})  # Return the current product's id if no previous product is found


@app.route('/reservation/<string:product_id>')
def reservation_form(product_id):
    product = mongo.db.testdata.find_one({'_id': ObjectId(product_id)})  # Convert product_id to ObjectId
    print(product)
    return render_template('reservationForm.html', product=product)


@app.route('/reservationConfirmation/<string:product_id>')
def reservation_confirmation(product_id):
    product = mongo.db.testdata.find_one({'_id': ObjectId(product_id)})  # Convert product_id to ObjectId
    print(product)
    return render_template('reservation_confirmation.html', product=product)


@app.route('/adminlogin', methods=['POST'])
def admin_login():
    username = request.form.get('adminUsername')
    password = request.form.get('adminPassword')

    # Validate credentials against adminlogin collection in MongoDB
    admin = mongo.db.adminlogin.find_one({'username': username, 'password': password})
    if admin:
        # Admin credentials are valid, store user ID in session
        session['user_id'] = str(admin['_id'])
        return redirect(url_for('inventory_management'))  # Change to your actual inventory management endpoint
    else:
        # Admin credentials are invalid, redirect back to the login page with an error message
        flash('Invalid username or password', 'error')
        return redirect(url_for('index'))  # Change to your actual index page


# Protect the inventory management route with authentication
@app.route('/inventorymanagement')
def inventory_management():
    if 'user_id' in session:
        products = mongo.db.testdata.find()
        return render_template('inventorymanagement.html', products=products)
    else:
        flash('Login as Admin to access Inventory Management', 'error')
        return redirect(url_for('index'))  # Change to your actual index page


@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' in session:
        # User is authenticated, proceed with adding the product
        category = request.form.get('category')
        name = request.form.get('name')
        price = float(request.form.get('price'))
        actualPrice = float(request.form.get('actualPrice'))
        description = request.form.get('description')
        img = request.files['img']

        if img:
            # Save the image to the static/img folder
            img_filename = os.path.join('img', img.filename)
            img.save(os.path.join(app.root_path, 'static', img_filename))
            imgPath = img_filename.replace("\\", "/")
        else:
            imgPath = None

        # Insert the new product record into the database
        mongo.db.testdata.insert_one({
            'id': mongo.db.testdata.count_documents({}) + 1,
            'category': category,
            'name': name,
            'price': price,
            'actualPrice': actualPrice,
            'description': description,
            'img': imgPath
        })

        flash('Product added successfully', 'success')
        return redirect(url_for('inventory_management'))  # Redirect to inventory management page
    else:
        flash('You need to log in first', 'error')
        return redirect(url_for('index'))  # Change to your actual index page


@app.route('/update_records', methods=['POST'])
def update_records():
    if request.method == 'POST':
        product_ids = [key.split('_')[1] for key in request.form.keys() if key.startswith('category_')]
        records_updated = None
        for product_id in product_ids:
            product = mongo.db.testdata.find_one({'_id': ObjectId(product_id)})
            if product:
                if request.form.get(f'checkbox_{product_id}') == 'on':
                    if float(request.form.get(f'price_{product_id}')) != product['price']:
                        mongo.db.testdata.update_one({'_id': ObjectId(product_id)}, {
                            '$set': {'price': float(request.form.get(f'price_{product_id}'))}})
                        records_updated = True
                    # Check if actual price has changed
                    if float(request.form.get(f'actual_price_{product_id}')) != product['actualPrice']:
                        mongo.db.testdata.update_one({'_id': ObjectId(product_id)}, {
                            '$set': {'actualPrice': float(request.form.get(f'actual_price_{product_id}'))}})
                        records_updated = True
                    # Check if category has changed
                    if request.form.get(f'category_{product_id}') != product['category']:
                        mongo.db.testdata.update_one({'_id': ObjectId(product_id)},
                                                     {'$set': {'category': request.form.get(f'category_{product_id}')}})
                        records_updated = True
                    # Check if name has changed
                    if request.form.get(f'product_name_{product_id}') != product['name']:
                        print(request.form.get(f'product_name_{product_id}'))
                        mongo.db.testdata.update_one({'_id': ObjectId(product_id)},
                                                     {'$set': {'name': request.form.get(f'product_name_{product_id}')}})
                        records_updated = True
                    # Check if description has changed
                    if request.form.get(f'product_description_{product_id}') != product['description']:
                        mongo.db.testdata.update_one({'_id': ObjectId(product_id)},
                                                     {'$set': {'description': request.form.get(
                                                         f'product_description_{product_id}')}})
                        records_updated = True
                    # Check if delete option has been ticked
                    if request.form.get(f'delete_{product_id}') == 'on':
                        mongo.db.testdata.delete_one({'_id': ObjectId(product_id)})
                        records_updated = True

        if not records_updated:
            flash('Please select at least one record to update.', 'success')
        else:
            flash('Records updated successfully', 'success')
    return redirect(url_for('inventory_management'))


if __name__ == '__main__':
    app.run(debug=True)
