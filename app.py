import os
from flask import Flask, render_template
from bson import ObjectId
from flask import jsonify
from flask import request, redirect, url_for, flash, session
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from flask import Flask, redirect, url_for, session
from flask_oauthlib.client import OAuth
from functools import wraps


app = Flask(__name__)
app.secret_key = 'my1Password@1'  # Set a secret key for session management
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='845708482790-a8adqo54svoo88872m5cn4appsdus54p.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


def get_mongo_uri():
    if 'WEBSITE_INSTANCE_ID' not in os.environ:
        # Running locally
        return MongoClient('localhost', 27017)
    else:
        # Use the connection string for Cosmos DB in Azure
        azureDB = 'mongodb+srv://jee:my1Password@gemstone.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000'
        return MongoClient(azureDB)


mongo_client = get_mongo_uri()
database: Database = mongo_client.get_database("jee")
collection: Collection = database.get_collection("testdata")


@app.route('/')
def index():
    products = database.testdata.find().sort('id')  # Gets all records from DB
    return render_template('index.html', products=products)


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    user_info = google.get('userinfo')
    session['admin_logged_in'] = True
    me = google.get('userinfo')
    flash('Logged in as ' + user_info.data['email'], 'error')
    return redirect(url_for('inventory_management'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@app.route('/product/<string:product_id>')
def product_detail(product_id):
    product = database.testdata.find_one({'_id': ObjectId(product_id)})  # Convert product_id to ObjectId
    return render_template('product_detail.html', product=product)


@app.route('/nextProduct/<string:product_id>')
def next_product(product_id):
    current_product = database.testdata.find_one({'_id': ObjectId(product_id)})
    if current_product:
        next_product = database.testdata.find_one({'id': current_product['id'] + 1})
        if next_product:
            return jsonify({'product_id': str(next_product['_id'])})
    return jsonify({'product_id': product_id})  # Return the current product's id if no next product is found


@app.route('/prevProduct/<string:product_id>')
def prev_product(product_id):
    current_product = database.testdata.find_one({'_id': ObjectId(product_id)})
    if current_product:
        prev_product = database.testdata.find_one({'id': current_product['id'] - 1})
        if prev_product:
            return jsonify({'product_id': str(prev_product['_id'])})
    return jsonify({'product_id': product_id})  # Return the current product's id if no previous product is found


@app.route('/reservation/<string:product_id>')
def reservation_form(product_id):
    product = database.testdata.find_one({'_id': ObjectId(product_id)})  # Convert product_id to ObjectId
    return render_template('reservationForm.html', product=product)


@app.route('/reservationConfirmation/<string:product_id>')
def reservation_confirmation(product_id):
    product = database.testdata.find_one({'_id': ObjectId(product_id)})  # Convert product_id to ObjectId
    return render_template('reservation_confirmation.html', product=product)


@app.route('/adminlogin', methods=['POST'])
def admin_login():
    username = request.form.get('adminUsername')
    password = request.form.get('adminPassword')

    # Validate credentials against adminlogin collection in MongoDB
    admin = database.adminlogin.find_one({'username': username, 'password': password})
    if admin:
        # Admin credentials are valid, store user ID in session
        session['user_id'] = str(admin['_id'])
        session['admin_logged_in'] = True
        return redirect(url_for('inventory_management'))  # Change to your actual inventory management endpoint
    else:
        # Admin credentials are invalid, redirect back to the login page with an error message
        flash('Invalid username or password', 'error')
        return redirect(url_for('index'))  # Change to your actual index page


# Define a decorator to check if the user is authenticated
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session and 'user_id' not in session:
            flash('Login as Admin to access Inventory Management', 'error')
            return redirect(url_for('index'))  # Redirect to the index page if not authenticated
        return f(*args, **kwargs)
    return decorated_function


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Clear the session
    session.pop('google_token', None)
    session.clear()
    return redirect(url_for('index'))  # Redirect to the index page or any other page after logout


# Protect the inventory management route with authentication
@app.route('/inventorymanagement', methods=['GET', 'POST'])
@login_required  # Apply the login_required decorator to this route
def inventory_management():
    products = database.testdata.find().sort('id')
    return render_template('inventorymanagement.html', products=products)


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
        database.testdata.insert_one({
            'id': database.testdata.count_documents({}) + 1,
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
            product = database.testdata.find_one({'_id': ObjectId(product_id)})
            if product:
                if request.form.get(f'checkbox_{product_id}') == 'on':
                    if float(request.form.get(f'price_{product_id}')) != product['price']:
                        database.testdata.update_one({'_id': ObjectId(product_id)}, {
                            '$set': {'price': float(request.form.get(f'price_{product_id}'))}})
                        records_updated = True
                    # Check if actual price has changed
                    if float(request.form.get(f'actual_price_{product_id}')) != product['actualPrice']:
                        database.testdata.update_one({'_id': ObjectId(product_id)}, {
                            '$set': {'actualPrice': float(request.form.get(f'actual_price_{product_id}'))}})
                        records_updated = True
                    # Check if category has changed
                    if request.form.get(f'category_{product_id}') != product['category']:
                        print(product)
                        database.testdata.update_one({'_id': ObjectId(product_id)},
                                                     {'$set': {'category': request.form.get(f'category_{product_id}')}})
                        records_updated = True
                    # Check if name has changed
                    if request.form.get(f'product_name_{product_id}') != product['name']:
                        print('Product Name from Browser: ' + str(request.form.get(f'product_name_{product_id}')))
                        print(product)
                        print('Product Name from DB: ' + str(product['name']))
                        database.testdata.update_one({'_id': ObjectId(product_id)},
                                                     {'$set': {'name': request.form.get(f'product_name_{product_id}')}})
                        records_updated = True
                    # Check if description has changed
                    if request.form.get(f'product_description_{product_id}') != product['description']:
                        database.testdata.update_one({'_id': ObjectId(product_id)},
                                                     {'$set': {'description': request.form.get(
                                                         f'product_description_{product_id}')}})
                        records_updated = True
                    # Check if delete option has been ticked
                    if request.form.get(f'delete_{product_id}') == 'on':
                        database.testdata.delete_one({'_id': ObjectId(product_id)})
                        records_updated = True

        if not records_updated:
            flash('Please select/modify at least one record to update.', 'success')
        else:
            flash('Records updated successfully', 'success')
    return redirect(url_for('inventory_management'))


if __name__ == '__main__':
    app.run(debug=True)

