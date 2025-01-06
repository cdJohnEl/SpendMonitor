from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_bcrypt import Bcrypt
from firebase_admin import credentials, firestore, initialize_app
import google.generativeai as genai
import os
from datetime import datetime
from PIL import Image
import io
import re
from dotenv import load_dotenv
from functools import wraps
import csv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
bcrypt = Bcrypt(app)

# Initialize Firebase
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')
cred = credentials.Certificate(firebase_credentials_path)
initialize_app(cred)
db = firestore.client()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        users_ref = db.collection('users')
        users_ref.add({
            'name': name,
            'email': email,
            'password': hashed_password
        })
        
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        user = query.get()
        
        if user and bcrypt.check_password_hash(user[0].to_dict()['password'], password):
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_email = session['user']
    user_ref = db.collection('users').document(user_email)
    
    # Get total income and expenses
    income = user_ref.collection('transactions').where('type', '==', 'income').get()
    expenses = user_ref.collection('transactions').where('type', '==', 'expense').get()
    
    total_income = sum(doc.to_dict()['amount'] for doc in income)
    total_expenses = sum(doc.to_dict()['amount'] for doc in expenses)
    balance = total_income - total_expenses
    
    return render_template('dashboard.html', balance=balance, total_income=total_income, total_expenses=total_expenses)

def parse_receipt_data(text):
    patterns = {
        'Amount': r'₦([\d,]+\.\d{2})',
        'Date': r'Date\s*:\s*(\d{2}/\d{2}/\d{4})',
        'Time': r'Time\s*:\s*(\d{2}:\d{2})',
        'Transaction type': r'Transaction type\s*:\s*(.+)',
        'Recipient details': r'recipient details\s*:\s*(.+)',
        'Sender details': r'Sender details\s*:\s*(.+)',
        'Remarks': r'remarks\s*:\s*(.+)',

    }
    
    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1).strip()
        else:
            data[key] = ''

    # Extract amount
    amount_match = re.search(patterns['Amount'], text)
    if amount_match:
        amount = amount_match.group(1)
        try:
            data['Amount'] = float(amount.replace(',', ''))
        except ValueError:
            data['Amount'] = 0.0
    else:
        data['Amount'] = 0.0
    return data

@app.route('/upload', methods=['POST'])
@login_required
def upload_receipt():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        image = Image.open(file.stream)
        prompt = "The Image is a receipt. Please extract the following information: \n\n Amount, Date, Time, Transaction type, recipient details, and Sender details and remarks if any. \n\n"
        response = model.generate_content([prompt, image])
        parsed_data = parse_receipt_data(response.text)
        return jsonify({"result": parsed_data})

@app.route('/save', methods=['POST'])
@login_required
def save_receipt():
    try:
        data = request.json
        user_email = session['user']
        transaction_type = data.get('transaction_type')
        
        # Get amount from the receipt data
        amount_str = str(data.get('Amount', '0'))
        try:
            # Remove currency symbol and commas, then convert to float
            amount = float(amount_str.replace('₦', '').replace(',', ''))
        except ValueError:
            amount = 0.0
        
        if not transaction_type:
            return jsonify({"error": "Missing transaction type"}), 400
        
        transaction_ref = db.collection('users').document(user_email).collection('transactions').document()
        transaction_ref.set({
            'type': transaction_type,
            'amount': amount,
            'date': datetime.now().isoformat(),
            'details': data
        })
        
        return jsonify({"message": "Transaction saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_transactions')
@login_required
def get_transactions():
    user_email = session['user']
    transactions_ref = db.collection('users').document(user_email).collection('transactions')
    transactions = transactions_ref.order_by('date', direction='DESCENDING').limit(10).get()
    
    result = []
    for doc in transactions:
        transaction = doc.to_dict()
        transaction['id'] = doc.id
        result.append(transaction)
    
    return jsonify(result)

@app.route('/download_summary')
@login_required
def download_summary():
    user_email = session['user']
    transactions_ref = db.collection('users').document(user_email).collection('transactions')
    transactions = transactions_ref.order_by('date').get()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Amount', 'Details'])
    
    for doc in transactions:
        transaction = doc.to_dict()
        writer.writerow([
            transaction['date'],
            transaction['type'],
            transaction['amount'],
            str(transaction['details'])
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='finance_summary.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)

