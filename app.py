
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from pymongo import MongoClient
from user import User  # Import the User class
from datetime import datetime
import csv
import os
import matplotlib.pyplot as plt  # For data visualization

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# MongoDB setup with Atlas URI
client = MongoClient('mongodb+srv://jedielmwangi:SFPz6A9h0pFP0Yox@cluster0.mbqss.mongodb.net/userdata?retryWrites=true&w=majority')
db = client['userdata']
collection = db['user_data']

@app.route('/')
def index():
    # Get today's date
    today_date = datetime.today().strftime('%Y-%m-%d')  
    return render_template('index.html', date=today_date)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Retrieve form data
        age = request.form['age']
        gender = request.form['gender']
        income = request.form['income']
        
        # Capture expenses based on the checkboxes
        expenses = {}
        
        if 'utilities' in request.form:
            expenses['utilities'] = float(request.form['utilities_amount']) if request.form['utilities_amount'] else 0
        if 'entertainment' in request.form:
            expenses['entertainment'] = float(request.form['entertainment_amount']) if request.form['entertainment_amount'] else 0
        if 'school_fees' in request.form:
            expenses['school_fees'] = float(request.form['school_fees_amount']) if request.form['school_fees_amount'] else 0
        if 'shopping' in request.form:
            expenses['shopping'] = float(request.form['shopping_amount']) if request.form['shopping_amount'] else 0
        if 'healthcare' in request.form:
            expenses['healthcare'] = float(request.form['healthcare_amount']) if request.form['healthcare_amount'] else 0

        # Create a User object and save data to CSV
        user = User(age, gender, income, expenses)
        user.save_to_csv()  # Save data to CSV (Optional)

        # Save data to MongoDB
        collection.insert_one({
            'age': age,
            'gender': gender,
            'income': income,
            'expenses': expenses
        })

        flash("Data submitted successfully!", "success")  # Success message
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")  # Error message
    return redirect(url_for('index'))

@app.route('/export', methods=['GET'])
def export():
    # Define the CSV file path
    csv_file_path = 'exported_data.csv'
    
    # Fetch all data from MongoDB
    users = collection.find()  # Retrieve all documents from the 'user_data' collection
    
    # Open CSV file and write the data
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Age', 'Gender', 'Income', 'Utilities', 'Entertainment', 'School Fees', 'Shopping', 'Healthcare'])
        
        # Write data from MongoDB to CSV
        for user in users:
            writer.writerow([
                user.get('age', ''),
                user.get('gender', ''),
                user.get('income', ''),
                user['expenses'].get('utilities', ''),
                user['expenses'].get('entertainment', ''),
                user['expenses'].get('school_fees', ''),
                user['expenses'].get('shopping', ''),
                user['expenses'].get('healthcare', '')
            ])
    
    # Return the CSV file as a download
    return send_file(csv_file_path, as_attachment=True, download_name='user_data.csv')

@app.route('/visualize', methods=['GET'])
def visualize():
    # Fetch all data from MongoDB for visualization
    users = list(collection.find())
    
    # Example of visualizing average income vs age
    age_income = {int(user['age']): float(user['income']) for user in users if 'age' in user and 'income' in user}
    
    if age_income:
        ages = list(age_income.keys())
        incomes = list(age_income.values())

        plt.figure(figsize=(10, 5))
        plt.bar(ages, incomes, color='blue')
        plt.title('Income by Age')
        plt.xlabel('Age')
        plt.ylabel('Income')
        plt.grid(axis='y')
        
        # Save the figure
        plt.savefig('income_by_age.png')

        return send_file('income_by_age.png', as_attachment=True)

    flash("No data available for visualization.", "warning")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)
