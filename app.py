from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trainees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Trainee model
class Trainee(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    nic = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    institute = db.Column(db.String(100), nullable=False)
    languages = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    supervisor = db.Column(db.String(100), nullable=False)
    assigned_work = db.Column(db.String(200), nullable=False)
    target_date = db.Column(db.String(20), nullable=False)

    @staticmethod
    def generate_id():
        # Get the last trainee ID from the database
        last_trainee = Trainee.query.order_by(Trainee.id.desc()).first()
        if last_trainee:
            # Extract the numeric part and increment it
            last_id = int(last_trainee.id[1:])  # Skip the 'T' and convert to int
            new_id = last_id + 1
        else:
            new_id = 1  # Start from 1 if no trainees exist
        
        return f'T{new_id:06d}'  # Format as T000001, T000002, etc.
# Create the database
with app.app_context():
    db.create_all()



@app.route('/')
def home():
    return render_template('create.html')

@app.route('/add', methods=['POST'])
def add_intern():
    trainee = Trainee(
        id=Trainee.generate_id(),  
        name=request.form['name'],
        mobile=request.form['mobile'],
        nic=request.form['nic'],
        email=request.form['email'],
        address=request.form['address'],
        start_date=request.form['start_date'],
        end_date=request.form['end_date'],
        institute=request.form['institute'],
        languages=request.form['languages'],
        specialization=request.form['specialization'],
        supervisor=request.form['supervisor'],
        assigned_work=request.form['assigned_work'],
        target_date=request.form['target_date']
    )
    db.session.add(trainee)
    db.session.commit()
    return redirect(url_for('table'))

@app.route('/table')
def table():
    page = request.args.get('page', 1, type=int)  # Get the current page number from the query string
    per_page = request.args.get('per_page', 10, type=int)  # Get the number of entries per page from the query string
    trainees = Trainee.query.paginate(page=page, per_page=per_page, error_out=False)  # Correct usage

    return render_template('table.html', trainees=trainees,per_page=per_page)

@app.route('/export')
def export_to_excel():
    trainees = Trainee.query.all()
    trainee_list = [
        {
            "Name": t.name,
            "Mobile": t.mobile,
            "NIC": t.nic,
            "Email": t.email,
            "Address": t.address,
            "Start Date": t.start_date,
            "End Date": t.end_date,
            "Institute": t.institute,
            "Languages": t.languages,
            "Specialization": t.specialization,
            "Supervisor": t.supervisor,
            "Assigned Work": t.assigned_work,
            "Target Date": t.target_date,
        }
        for t in trainees
    ]
    df = pd.DataFrame(trainee_list)
    file_path = os.path.join(os.getcwd(), "trainees.xlsx")
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

@app.route('/clear')
def clear_database():
    db.drop_all()  # This will drop all tables in the database
    db.create_all()  # This will recreate the tables
    return redirect(url_for('table'))  # Redirect to the table view

if __name__ == '__main__':
    app.run(debug=True)
