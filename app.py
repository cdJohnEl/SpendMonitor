from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from firebase_admin import credentials, firestore, initialize_app
import google.generativeai as genai
import os
from datetime import datetime
from PIL import Image
import io
import re
from dotenv import load_dotenv



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
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

def parse_receipt_data(text):
    data = {}
    
    # Clean up the text first - remove any ** markers
    text = text.replace('**', '')
    
    patterns = {
        'Amount': r'₦([\d,]+\.\d{2})',  # Matches ₦5,000.00
        'Date': r'(\w+ \d{2},?\d{4})',  # Matches Nov 09,2024
        'Time': r'(\d{2}:\d{2})',  # Matches 08:56
        'Transaction type': r'Transaction Type:?\s*([^\n]+)',  # Matches "Transfer to bank"
        'Recipient details': r'PAYSTACK[^\n]*(?:\n[^S\n]*)*',  # Matches PAYSTACK lines until Sender
        'Sender details': r'CHIMDIKE[^\n]*',  # Matches the sender name and details
        'Transaction Reference': r'Transaction Reference\s*(\d+)',
        'SessionID': r'SessionID\s*(\d+)'
    }
    
    # Extract amount
    amount_match = re.search(patterns['Amount'], text)
    if amount_match:
        amount = amount_match.group(1)
        data['Amount'] = float(amount.replace(',', ''))
    else:
        data['Amount'] = 'N/A'
    
    # Extract date and time
    date_match = re.search(patterns['Date'], text)
    time_match = re.search(patterns['Time'], text)
    data['Date'] = date_match.group(1) if date_match else 'N/A'
    data['Time'] = time_match.group(1) if time_match else 'N/A'
    
    # Extract transaction type
    trans_type_match = re.search(patterns['Transaction type'], text, re.IGNORECASE)
    data['Transaction type'] = trans_type_match.group(1).strip() if trans_type_match else 'N/A'
    
    # Extract recipient details
    recipient_match = re.search(patterns['Recipient details'], text)
    if recipient_match:
        recipient = recipient_match.group(0)
        # Clean up and format recipient details
        recipient_lines = [line.strip() for line in recipient.split('\n') if line.strip()]
        data['Recipient details'] = ' | '.join(recipient_lines)
    else:
        data['Recipient details'] = 'N/A'
    
    # Extract sender details
    sender_match = re.search(patterns['Sender details'], text)
    if sender_match:
        sender = sender_match.group(0)
        # Clean up sender details
        data['Sender details'] = sender.strip()
    else:
        data['Sender details'] = 'N/A'
    
    # Extract reference numbers
    ref_match = re.search(patterns['Transaction Reference'], text)
    session_match = re.search(patterns['SessionID'], text)
    data['Transaction Reference'] = ref_match.group(1) if ref_match else 'N/A'
    data['SessionID'] = session_match.group(1) if session_match else 'N/A'
    
    return data

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/google-auth', methods=['POST'])
def google_auth():
    data = request.json
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(data['token'])
        uid = decoded_token['uid']
        
        # Get or create user in Firestore
        user_ref = db.collection('users').document(uid)
        user_ref.set({
            'email': data['email'],
            'name': data['displayName'],
            'last_login': datetime.now().isoformat()
        }, merge=True)
        
        # Set session
        session['user'] = data['email']
        session['uid'] = uid
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in google_auth: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400





@app.route('/upload', methods=['POST'])
def upload_receipt():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
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
        print(parsed_data)
        return jsonify({"result": parsed_data})

@app.route('/save', methods=['POST'])
def save_receipt():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user_email = session['user']
    current_date = datetime.now()
    month_year = current_date.strftime("%B_%Y")
    
    receipts_ref = db.collection('users').document(user_email).collection('receipts').document(month_year)
    receipts_ref.set({
        current_date.isoformat(): data
    }, merge=True)
    
    return jsonify({"message": "Receipt saved successfully"})

@app.route('/get_receipts')
def get_receipts():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_email = session['user']
    receipts_ref = db.collection('users').document(user_email).collection('receipts')
    receipts = receipts_ref.get()
    
    result = {}
    for doc in receipts:
        result[doc.id] = doc.to_dict()
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

