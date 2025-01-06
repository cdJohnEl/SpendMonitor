# 🔎 SpendMonitor - Finance Tracker

SpendMonitor is a finance tracking application that streamlines expense and income management by enabling users to upload and process receipts for financial summaries. It leverages advanced AI and Firebase integration for secure and efficient tracking of financial transactions. Designed with user experience in mind, SpendMonitor helps you stay on top of your finances!

## Features

- **Receipt Upload and Scanning**:  
  Users can upload receipts for automated extraction of key financial information such as:
  - Amount
  - Date
  - Time
  - Transaction type
  - Recipient details
  - Sender details
  - Remarks (if available)
  
- **AI-Powered Information Extraction**:  
  The app utilizes a Generative AI model (`gemini-1.5-pro`) to analyze receipts and extract relevant financial data automatically.

- **Financial Summaries**:  
  Provides users with a breakdown of:
  - Current Balance
  - Total Income
  - Total Expenses
  - Recent Transactions

- **Secure Login**:  
  Requires user authentication to access the dashboard and features, ensuring data security.

- **Export Financial Data**:  
  Users can download financial summaries for their records.

## Technologies Used

- **Backend**:  
  - Python with Flask framework
  - Firebase Firestore (database for data storage)
  - Google Generative AI (`gemini-1.5-pro`) for OCR and information extraction

- **Frontend**:  
  - HTML templates (e.g., `dashboard.html`) for user interface design
  - Jinja2 for dynamic rendering of financial data

- **Other Dependencies**:  
  - PIL (Pillow library) for receipt image processing
  - `dotenv` for environment variable management
  - Flask-Bcrypt for password hashing
  - Flask-Session for user session management

## How It Works

1. **Login Required**:  
   Users must log in using secure credentials to access features like uploading a receipt.

2. **Receipt Processing**:  
   - Navigate to the dashboard and upload a receipt using the file uploader.
   - The receipt image is processed using Generative AI to extract details.

3. **Data Extraction**:  
   - The app uses regex patterns to parse extracted text for specific information such as amount, date, time, and transaction types.

4. **Review Transactions**:  
   - Scanned results are displayed on the dashboard for categorizing as income or expense.
   - Users can save this information for future references.

5. **Financial Summary**:  
   - The dashboard provides a live overview of your current balance, total income, and expenses.
   - Recent transactions are also listed for quick access.

6. **Export Data**:  
   - Users can download a detailed financial summary for offline use.

## Folder Structure

The following files are critical for the application's operation:

1. **`app.py`** - Main backend file containing:
   - Flask app setup and routing
   - Receipt processing logic
   - Integration with Generative AI and Firebase

2. **`dashboard.html`** - Core frontend template used for displaying:
   - Financial summaries
   - Receipt upload interface
   - Recent transactions and user actions

3. **`.env`** - Environment variable file (not included for security) containing:
   - SECRET_KEY for Flask session security
   - Firebase credentials file path
   - Gemini AI API key

## Installation and Setup

To set up SpendMonitor locally, follow these steps:

1. **Clone the Repository**  
   ```
   git clone https://github.com/cdJohnEl/SpendMonitor.git
   cd spendmonitor
   ```

2. **Install Dependencies**  
   Make sure Python is installed on your system. Then, run:
   ```
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**  
   Create a `.env` file in the root directory and provide the following:
   ```
   SECRET_KEY=your_secret_key
   FIREBASE_CREDENTIALS=path/to/firebase/credentials.json
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Run the Application**  
   Start the local development server:
   ```
   python app.py
   ```

   The application will be available at `http://127.0.0.1:5000/`.

5. **Login (or Register)**  
   Access the app, create an account (if required), and start uploading receipts!

## Key Dependencies

The following Python libraries and services are utilized extensively in SpendMonitor:

- **Flask**: Server-side web framework
- **Pillow**: Image processing library
- **Firebase Admin SDK**: Database operations
- **Regex (re)**: Text extraction from scanned data
- **Google Generative AI**: For analyzing receipt images

Install all dependencies as listed in the `requirements.txt`.


## Future Improvements

- **Enhanced Receipt Parsing**: Improve AI's accuracy with more complex receipt formats.
- **Multi-Language Support**: Allow parsing receipts in multiple languages.
- **Mobile Responsiveness**: Optimize the app UI for mobile devices.
- **Advanced Analytics**: Add features like expense trends and budgeting recommendations.

## Author

- **John Chimdike Ezekiel**  
  Designed and developed SpendMonitor.

## License

This project is licensed under the MIT License.

---

Manage your expenses with ease, upload receipts conveniently, and stay financially on track with SpendMonitor! 