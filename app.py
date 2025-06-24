from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product
import os

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            return 'User already exists'
        db.session.add(User(username=username, password=password))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    products = Product.query.all()
    print(f"Total products in DB: {len(products)}")  # Should print 11
    for p in products:
        print(p.name, p.image)
    return render_template('dashboard.html', products=products)

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    product_ids = session.get('cart', [])
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    total = sum(p.price for p in products)
    return render_template('cart.html', products=products, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])  # Accepts POST
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'cart' not in session:
        session['cart'] = []
    
    if product_id not in session['cart']:
        session['cart'].append(product_id)
        session.modified = True
    
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Store both address and payment method
        session['shipping_address'] = {
            'full_name': request.form.get('full_name'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip_code': request.form.get('zip_code'),
            'phone': request.form.get('phone')
        }
        session['payment_method'] = request.form.get('payment_method')
        return redirect(url_for('confirmation'))
    
    product_ids = session.get('cart', [])
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    total = sum(p.price for p in products)
    
    return render_template('checkout.html', 
                         products=products,
                         total=total,
                         payment_methods=['card', 'upi', 'netbanking', 'cod'])

@app.route('/confirmation')
def confirmation():
    if 'user_id' not in session or 'payment_method' not in session:
        return redirect(url_for('dashboard'))
    
    product_ids = session.get('cart', [])
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    total = sum(p.price for p in products)
    
    # Get stored data
    address = session.get('shipping_address', {})
    payment_method = session.pop('payment_method')
    
    # Clear cart
    session.pop('cart', None)
    
    return render_template('checkout.html',
                         products=products,
                         total=total,
                         confirmation=True,
                         address=address,
                         payment_method=payment_method)

if __name__ == '__main__':
    with app.app_context():
        # Always create tables if they don't exist
        db.create_all()
        
        # Clear existing products (optional)
        Product.query.delete()
    
    with app.app_context():
        if Product.query.count() == 0:  # add products only if none exist
            db.session.add(Product(name='Sage Green Crystal Saree Gown', price=325000, image='Sage Green Crystal Saree Gown.jpg'))
            db.session.add(Product(name='Mint Green Gown', price=167000, image='Mint Green Gown.jpg'))
            db.session.add(Product(name='Red Carpet Glamour Gown', price=57000, image='Red Carpet Glamour Gown.jpg'))
            db.session.add(Product(name='Navy Asymmetric Gown', price=215000, image='Navy Asymmetric Gown.jpg'))
            db.session.add(Product(name='Yellow Halter Gown', price=335000, image='Yellow Halter Gown.jpg'))
            db.session.add(Product(name='Champagne Bow Gown', price=245000, image='Champagne Bow Gown.jpg'))
            db.session.add(Product(name='Powder Blue Gown', price=195000, image='Powder Blue Gown.jpg'))
            db.session.add(Product(name='Deep Red Crystal Gown', price=275000, image='Deep Red Crystal Gown.jpg'))
            db.session.add(Product(name='Light Blue Fitted Gown', price=235000, image='Light Blue Fitted Gown.jpg'))
            db.session.add(Product(name='Mauve Fitted Gown', price=185000, image='Mauve Fitted Gown.jpg'))
            db.session.add(Product(name='Burnt Orange High-Neck Gown', price=295000, image='Burnt Orange High-Neck Gown.jpg'))
            db.session.add(Product(name='White Sculptural Gown', price=265000, image='White Sculptural Gown.jpg'))
            db.session.add(Product(name='Navy Corset Gown', price=225000, image='Navy Corset Gown.jpg'))
            db.session.add(Product(name='Olive Green One-Shoulder Gown', price=285000, image='Olive Green One-Shoulder Gown.jpg'))
            db.session.add(Product(name='Ombre Metallic Gown', price=295000, image='Ombre Metallic Gown.jpg'))
            db.session.commit()

    app.run(debug=True)

   



