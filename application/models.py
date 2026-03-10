from .database import db

class User(db.Model):
    __tablename__ = 'user'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)    
    type = db.Column(db.String(), nullable=False) 
    student = db.relationship('Student', backref='student_account', foreign_keys='Student.sid')
    company = db.relationship('Company', backref='company_account', foreign_keys='Company.cid')
    
class Student(db.Model):
    __tablename__ = 'student'
    sid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True)
    username = db.Column(db.String(), db.ForeignKey('user.username'), nullable=False)
    sname = db.Column(db.String(), nullable=False)
    sdepartment = db.Column(db.String(), nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    yog = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(), nullable=False)
    resume = db.Column(db.String(), nullable=True)
    status = db.Column(db.String(), nullable=False, default='Activated') #account status: can be deactivated by admin [Activated, Deactivated]
    applications = db.relationship('Application', backref='student', foreign_keys='Application.sid', cascade='all, delete-orphan')

class Company(db.Model):
    __tablename__ = 'company'
    cid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True)
    username = db.Column(db.String(), db.ForeignKey('user.username'), nullable=False)
    cname = db.Column(db.String(), nullable=True)
    cabout = db.Column(db.String(), nullable=True)
    clocation = db.Column(db.String(), nullable=True)
    hr_contact = db.Column(db.String(), nullable=True)
    c_website = db.Column(db.String(), nullable=True)
    approval_status = db.Column(db.String(), nullable=False) #need to be approved by admin [Approved, Rejected, Blacklisted]
    drives = db.relationship('Placement_Drive', backref='company', cascade='all, delete-orphan')

class Placement_Drive(db.Model):
    __tablename__ = 'placement_drive'
    did = db.Column(db.Integer, primary_key=True)
    dname = db.Column(db.String(), nullable=False)
    cid = db.Column(db.Integer, db.ForeignKey('company.cid'), nullable=False)
    job_title = db.Column(db.String(), nullable=False)
    job_description = db.Column(db.String(), nullable=False)
    eligibility_criteria = db.Column(db.String(), nullable=False)
    salary = db.Column(db.Double, nullable=True)
    location = db.Column(db.String(), nullable=True)
    interview_type = db.Column(db.String(), nullable=True)
    application_deadline = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(), nullable=False, default='Pending') #need to be approved by admin [Pending, Approved, Rejected, Closed]
    applications = db.relationship('Application', backref='drive', foreign_keys='Application.did', cascade='all, delete-orphan')

class Application(db.Model):
    __tablename__ = 'application'
    aid = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey('student.sid'), nullable=False)
    did = db.Column(db.Integer, db.ForeignKey('placement_drive.did'), nullable=False)
    type = db.Column(db.String(), nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    yog = db.Column(db.Integer, nullable=False)
    application_date = db.Column(db.Text, nullable=False)
    resume = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False, default='Applied') #selection status: can be updated by company [Applied, Shortlisted, Selected, Rejected]
    

