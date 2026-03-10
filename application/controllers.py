import re

from flask import Flask, render_template, redirect, request
from flask import current_app as app
from datetime import datetime, timedelta

from .models import *

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        this_user = User.query.filter_by(username = username).first()
        if this_user:
            if this_user.password == password:
                if this_user.type == "Admin":
                    return redirect("/admin/{}".format(this_user.uid))
                elif this_user.type == "Student":
                    return redirect("/student/{}".format(this_user.uid))
                elif this_user.type == "Company":
                    return redirect("/company/{}".format(this_user.uid))
            else:
                return render_template("incorrect_password.html")
        else:
            return render_template("user_DNE.html")
    return render_template("login.html")
 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        type = request.form["type"]
        user_name= User.query.filter_by(username=username).first()
        user_email= User.query.filter_by(email=email).first()
        if user_name or user_email:
            return render_template("user_exists.html")
        else:
            user = User(username=username, email=email, password=password, type=type)
            db.session.add(user)
            db.session.commit()
        return render_template("reg_success.html")
    return render_template("register.html")

@app.route("/student/<int:user_id>")
def student(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    all_companies = Company.query.filter_by(approval_status="Approved").all()
    all_applications = Application.query.filter_by(sid=user_id).all()
    drive = Placement_Drive.query.filter(Placement_Drive.did.in_([app.did for app in all_applications])).all()
    company = Company.query.filter(Company.cid.in_([d.cid for d in drive])).all()
    return render_template("student_dash.html", this_user=this_user, all_companies=all_companies, all_applications=all_applications, drive=drive, company=company)

@app.route("/C_edit/<int:user_id>", methods=["GET", "POST"])
def C_edit(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    exist_user = Company.query.filter_by(cid=user_id).first()
    uname = this_user.username
    if exist_user is None:
        if request.method == "POST":
            company_name = request.form["company_name"]
            company_about = request.form["company_about"]
            location = request.form["location"]
            hr_contact = request.form["hr_contact"]
            website_url = request.form["website_url"]
            com = Company(cid=user_id, username=uname, cname=company_name, cabout=company_about, clocation=location, hr_contact=hr_contact, c_website=website_url)
            db.session.add(com)
            db.session.commit()
            return redirect("/company/{}".format(user_id))
    else:
        if request.method == "POST":
            exist_user.cname = request.form["company_name"]
            exist_user.cabout = request.form["company_about"]
            exist_user.clocation = request.form["location"]
            exist_user.hr_contact = request.form["hr_contact"]
            exist_user.c_website = request.form["website_url"]
            db.session.commit()
            return redirect("/company/{}".format(user_id))
    return render_template("C_edit_profile.html", this_user=this_user)

@app.route("/S_edit/<int:user_id>", methods=["GET", "POST"])
def S_edit(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    exist_user = Student.query.filter_by(sid=user_id).first()
    uname = this_user.username
    if exist_user is None:
        if request.method == "POST":
            student_name = request.form["student_name"]
            department = request.form["department"]
            gpa = request.form["gpa"]
            year_of_graduation = request.form["year_of_graduation"]
            contact = request.form["contact"]
            resume = request.form["resume"]
            stu = Student(sid=user_id, username=uname, sname=student_name, sdepartment=department, gpa=gpa, yog=year_of_graduation, contact=contact, resume=resume)
            db.session.add(stu)
            db.session.commit()
            return redirect("/student/{}".format(user_id))
    else:
        if request.method == "POST":
            exist_user.sname = request.form["student_name"]
            exist_user.sdepartment = request.form["department"]
            exist_user.gpa = request.form["gpa"]
            exist_user.yog = request.form["year_of_graduation"]
            exist_user.contact = request.form["contact"]
            exist_user.resume = request.form["resume"]
            db.session.commit()
            return redirect("/student/{}".format(user_id))
    return render_template("S_edit_profile.html", this_user=this_user)

@app.route("/create_drive/<int:user_id>", methods=["GET", "POST"])
def create_drive(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    company = Company.query.filter_by(cid=user_id).first()
    if company.approval_status != "Approved":
        return render_template("cant_create_drive.html", company=company)
    elif company.cname is None:
        return render_template("company_profile.html",company=company)
    else:
        if request.method == "POST":
            drive_name = request.form["drive_name"]
            job_title = request.form["job_title"]
            job_description = request.form["job_description"]
            eligibility_criteria = request.form["eligibility_criteria"]
            salary = request.form["salary"]
            location = request.form["location"]
            type = request.form["interview_type"]
            application_deadline = request.form["application_deadline"]
            drive = Placement_Drive(dname=drive_name, cid=user_id, job_title=job_title, job_description=job_description, eligibility_criteria=eligibility_criteria, salary = salary, location = location, interview_type=type, application_deadline=application_deadline)
            db.session.add(drive)   
            db.session.commit()
            return redirect("/company/{}".format(user_id))
    return render_template("create_drive.html", this_user=this_user)

@app.route("/view_company/<int:company_id>", methods=["GET", "POST"])
def view_company(company_id):
    today = datetime.today().date()
    this_company = Company.query.filter_by(cid=company_id).first()
    all_drives = Placement_Drive.query.filter_by(cid=company_id, status="Approved").filter((Placement_Drive.application_deadline >= today) & (Placement_Drive.status != "Closed")).all()
    return render_template("about_company.html", this_company=this_company, all_drives=all_drives)

@app.route("/view_drive/<int:drive_id>", methods=["GET", "POST"])
def view_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=this_drive.cid).first()
    return render_template("S_drive_info.html", this_drive=this_drive, this_company=this_company)

@app.route("/apply/<int:drive_id>/<string:interview_type>",methods=["GET","POST"])
def apply_drive(drive_id, interview_type):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    interview_type = this_drive.interview_type
    if request.method == "POST":
        if this_drive.application_deadline < str(datetime.today().date()):
            return render_template("app_deadline.html")
        elif Student.query.filter_by(sid=request.form["student_id"]).first().status == "Deactivated":
            return render_template("deactivate_student.html")
        elif Student.query.filter_by(sid=request.form["student_id"]).first() is None:
            return render_template("student_profile.html", student_id=request.form["student_id"])
        else:
            student_id = request.form["student_id"]
            gpa = request.form["gpa"]
            yog = request.form["year_of_graduation"]
            application_date = request.form["application_date"]
            resume = request.form["resume"]
            if drive_id not in [app.did for app in Application.query.filter_by(sid=student_id).all()]:
                this_app = Application(sid=student_id, did=drive_id, type=interview_type, gpa=gpa, yog=yog, application_date=application_date, resume=resume)
                db.session.add(this_app)
                db.session.commit()
            else:
                return render_template("already_applied.html")
            this_user = User.query.filter_by(uid=student_id).first()
            return redirect("/student/{}".format(this_user.uid))
    return render_template("apply_for_drive.html", this_drive=this_drive)

@app.route("/S_app_history/<int:student_id>", methods=["GET", "POST"])
def S_app_history(student_id):
    this_user = User.query.filter_by(uid=student_id).first()
    this_student = Student.query.filter_by(sid=student_id).first()
    all_applications = Application.query.filter_by(sid=student_id).all()
    drive = Placement_Drive.query.filter(Placement_Drive.did.in_([app.did for app in all_applications])).all()
    company = Company.query.filter(Company.cid.in_([d.cid for d in drive])).all()
    return render_template("student_app_history.html",this_user=this_user, this_student=this_student, all_applications=all_applications, drive=drive, company=company)

@app.route("/back/<int:user_id>", methods=["GET", "POST"])
def back(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    if this_user.type == "Admin":
        return redirect("/admin/{}".format(user_id))
    elif this_user.type == "Student":
        return redirect("/student/{}".format(user_id))
    elif this_user.type == "Company":
        return redirect("/company/{}".format(user_id))
    
@app.route("/view_applied_drive/<int:student_id>/<int:drive_id>", methods=["GET", "POST"])
def view_applied_drive(student_id, drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=this_drive.cid).first()
    this_application = Application.query.filter_by(sid=student_id, did=drive_id).first()
    return render_template("S_applied.html", this_drive=this_drive, this_company=this_company, this_application=this_application)

@app.route("/company/<int:user_id>", methods=["GET", "POST"])
def company(user_id):
    if Company.query.filter_by(cid=user_id).first() is None:
        return render_template("C_not_approved.html")
    else:
        today = datetime.today().date()
        total_app = len(Application.query.filter(Application.did.in_([drive.did for drive in Placement_Drive.query.filter_by(cid=user_id).all()])).all())
        upcoming_drives= Placement_Drive.query.filter((Placement_Drive.application_deadline >= today) & (Placement_Drive.status !="Closed"), Placement_Drive.cid==user_id).all()
        for drive in upcoming_drives:
            drive.noa_ud = len(Application.query.filter_by(did=drive.did).all())
        close_drives = Placement_Drive.query.filter(Placement_Drive.application_deadline < today, Placement_Drive.cid==user_id).all()
        for drive in close_drives:
            drive.status = "Closed"
            db.session.commit()
        closed_drives=Placement_Drive.query.filter_by(status="Closed", cid=user_id).all()
        for drive in closed_drives:
            drive.noa_cd = len(Application.query.filter_by(did=drive.did).all())
        this_user = User.query.filter_by(uid=user_id).first()
        this_company = Company.query.filter_by(cid=user_id).first()
        return render_template("company_dash.html", total_app=total_app, upcoming_drives=upcoming_drives, closed_drives=closed_drives, this_user=this_user, this_company=this_company)

@app.route("/view_upcoming_drive/<int:company_id>/<int:drive_id>", methods=["GET", "POST"])
def view_upcoming_drive(company_id, drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=company_id).first()
    all_applications = Application.query.filter_by(did=drive_id).all()
    students = Student.query.filter(Student.sid.in_([app.sid for app in all_applications])).all()
    all_students = []
    for app in all_applications:
        student = Student.query.filter_by(sid=app.sid).first()
        all_students.append({'student': student, 'app': app})
    return render_template("update_app_for_drive.html", this_drive=this_drive, this_company=this_company, all_applications=all_applications,students=students, all_students=all_students)

@app.route("/review_application/<int:student_id>/<int:drive_id>", methods=["GET", "POST"])
def review_application(student_id, drive_id):
    this_application = Application.query.filter_by(sid=student_id, did=drive_id).first()
    this_student = Student.query.filter_by(sid=student_id).first()
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=this_drive.cid).first()
    if request.method == "POST":
        new_status = request.form["status"]
        this_application.status = new_status
        db.session.commit()
        return redirect("/view_upcoming_drive/{}/{}".format(this_company.cid, drive_id))
    return render_template("C_student_app.html", this_application=this_application, this_student=this_student, this_drive=this_drive, this_company=this_company)

@app.route("/admin/<int:user_id>", methods=["GET", "POST"])
def admin(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    reg_companies = Company.query.filter_by(approval_status="Approved").all()
    rc = len(reg_companies)
    reg_students = Student.query.all()
    rs = len(reg_students)
    company_applications = User.query.filter_by(type="Company").all()
    com_app = []
    for company in company_applications:
        if Company.query.filter_by(cid=company.uid).first() is None:
            com_app.append(company)
    ca = len(com_app)
    ongoing_drives = Placement_Drive.query.filter().all()
    od = len(ongoing_drives)
    student_applications = Application.query.filter_by().all()
    sa = len(student_applications)
    drive = Placement_Drive.query.filter(Placement_Drive.did.in_([app.did for app in student_applications])).all()
    student = Student.query.filter(Student.sid.in_([app.sid for app in student_applications])).all()
    company = Company.query.filter(Company.cid.in_([d.cid for d in drive])).all()
    return render_template("admin_dash.html", this_user=this_user, reg_companies=reg_companies, reg_students=reg_students, com_app=com_app, ongoing_drives=ongoing_drives, student_applications=student_applications, rc=rc, rs=rs, ca=ca, od=od, sa=sa, drive=drive, student=student, company=company)

@app.route("/A_view_drive/<int:drive_id>", methods=["GET", "POST"])
def A_view_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=this_drive.cid).first()
    return render_template("A_ongoing_drive_info.html", this_drive=this_drive, this_company=this_company)

@app.route("/A_student_app/<int:student_id>/<int:drive_id>", methods=["GET", "POST"])
def A_student_app(student_id, drive_id):
    this_application = Application.query.filter_by(sid=student_id, did=drive_id).first()
    this_student = Student.query.filter_by(sid=student_id).first()
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=this_drive.cid).first()
    return render_template("A_student_app.html", this_application=this_application, this_student=this_student, this_drive=this_drive, this_company=this_company)

@app.route("/approve_company/<int:company_id>", methods=["GET", "POST"])
def approve_company(company_id):
    this_user = User.query.filter_by(uid=company_id).first()
    if Company.query.filter_by(cid=company_id).first() is not None:
        exist_company = Company.query.filter_by(cid=company_id).first()
        exist_company.approval_status = "Approved"
        db.session.commit()
    else:
        new_company = Company(cid=company_id, username=this_user.username, approval_status="Approved")
        db.session.add(new_company)
        db.session.commit()
    return redirect("/admin/1")

@app.route("/reject_company/<int:company_id>", methods=["GET", "POST"])
def reject_company(company_id):
    this_user = User.query.filter_by(uid=company_id).first()
    if Company.query.filter_by(cid=company_id).first() is not None:
        exist_company = Company.query.filter_by(cid=company_id).first()
        exist_company.approval_status = "Rejected"
        db.session.commit()
    else:
        new_company = Company(cid=company_id, username=this_user.username, approval_status="Rejected")
        db.session.add(new_company)
        db.session.commit()
    return redirect("/admin/1")

@app.route("/blacklist_company/<int:company_id>", methods=["GET", "POST"])
def blacklist_company(company_id):
    this_company = Company.query.filter_by(cid=company_id).first()
    this_company.approval_status = "Blacklisted"
    db.session.commit()
    all_drives = Placement_Drive.query.filter_by(cid=company_id).all()
    for drive in all_drives:
        drive.status = "Closed"
        db.session.commit()
    return redirect("/admin/1")

@app.route("/deactivate_student/<int:student_id>", methods=["GET", "POST"])
def deactivate_student(student_id):
    this_student = Student.query.filter_by(sid=student_id).first()
    this_student.status = "Deactivated"
    db.session.commit()
    return redirect("/admin/1")

@app.route("/activate_student/<int:student_id>", methods=["GET", "POST"])
def activate_student(student_id):
    this_student = Student.query.filter_by(sid=student_id).first()
    this_student.status = "Activated"
    db.session.commit()
    return redirect("/admin/1")

@app.route("/approve_drive/<int:drive_id>", methods=["GET", "POST"])
def approve_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_drive.status = "Approved"
    db.session.commit()
    return redirect("/admin/1")

@app.route("/reject_drive/<int:drive_id>", methods=["GET", "POST"])
def reject_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_drive.status = "Rejected"
    db.session.commit()
    return redirect("/admin/1")

@app.route("/S_my_profile/<int:user_id>", methods=["GET", "POST"])
def S_my_profile(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    this_student = Student.query.filter_by(sid=user_id).first()
    return render_template("S_my_profile.html", this_user=this_user, this_student=this_student)

@app.route("/C_my_profile/<int:user_id>", methods=["GET", "POST"])
def C_my_profile(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    this_company = Company.query.filter_by(cid=user_id).first()
    return render_template("C_my_profile.html", this_user=this_user, this_company=this_company)

@app.route("/edit_drive/<int:drive_id>", methods=["GET", "POST"])
def edit_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    if request.method == "POST":
        this_drive.job_title = request.form["job_title"]
        this_drive.job_description = request.form["job_description"]
        this_drive.eligibility_criteria = request.form["eligibility_criteria"]
        this_drive.salary = request.form["salary"]
        this_drive.location = request.form["location"]
        this_drive.interview_type = request.form["interview_type"]
        this_drive.application_deadline = request.form["application_deadline"]
        db.session.commit()
        return redirect("/company/{}".format(this_drive.cid))
    return render_template("C_edit_drive.html", this_drive=this_drive)

@app.route("/view_for_edit/<int:user_id>/<int:drive_id>", methods=["GET", "POST"])
def view_for_edit(user_id, drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=user_id).first()
    return render_template("C_drive_info.html", this_drive=this_drive, this_company=this_company)

@app.route("/remove_drive/<int:drive_id>", methods=["GET", "POST"])
def remove_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    db.session.delete(this_drive)
    db.session.commit()
    return redirect("/company/{}".format(this_drive.cid))

@app.route("/close_drive/<int:drive_id>", methods=["GET", "POST"])
def close_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_drive.status = "Closed"
    db.session.commit()
    return redirect("/company/{}".format(this_drive.cid))

@app.route("/open_drive/<int:drive_id>", methods=["GET", "POST"])
def open_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_drive.status = "Pending"
    db.session.commit()
    return redirect("/company/{}".format(this_drive.cid))

@app.route("/update_selection_status/<int:drive_id>/<int:student_id>", methods=["GET", "POST"])
def update_selection_status(drive_id, student_id):
    this_app = Application.query.filter_by(sid=student_id, did=drive_id).first()
    application = Placement_Drive.query.filter_by(did=drive_id).first()
    if request.method == "POST":
        result = request.form["result"]
        this_app.status = result
        db.session.commit()
    return redirect("/company/{}".format(application.cid))

@app.route("/all_placement_history", methods=["GET", "POST"])
def all_placement_history():
    total_applications = len(Application.query.all())
    total_placed = len(Application.query.filter_by(status="Selected").all())    
    total_drives = len(Placement_Drive.query.filter_by(status="Approved").all())
    all_placed = Application.query.filter_by(status="Selected").all()
    return render_template("all_placement_history.html", total_applications=total_applications, total_placed=total_placed, total_drives=total_drives, all_placed=all_placed)

@app.route("/company_history/<int:company_id>", methods=["GET", "POST"])
def company_history(company_id):
    this_company = Company.query.filter_by(cid=company_id).first()
    total_applications = len(Application.query.filter(Application.did.in_([drive.did for drive in Placement_Drive.query.filter_by(cid=company_id).all()])).all())
    total_placed = len(Application.query.filter_by(status="Selected").filter(Application.did.in_([drive.did for drive in Placement_Drive.query.filter_by(cid=company_id).all()])).all())    
    total_drives = len(Placement_Drive.query.filter_by(cid=company_id, status="Approved").all())
    students_placed = Application.query.filter_by(status="Selected").filter(Application.did.in_([drive.did for drive in Placement_Drive.query.filter_by(cid=company_id).all()])).all()
    return render_template("company_history.html", this_company=this_company, total_applications=total_applications, total_placed=total_placed, total_drives=total_drives, students_placed=students_placed)

@app.route("/view_closed_drive_history/<int:drive_id>", methods=["GET", "POST"]) 
def view_closed_drive_history(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=this_drive.cid).first()
    total_applications = len(Application.query.filter_by(did=drive_id).all())
    total_placed = len(Application.query.filter_by(did=drive_id, status="Selected").all())
    placed_students = Application.query.filter_by(did=drive_id, status="Selected").all()
    shortlisted_students = Application.query.filter_by(did=drive_id, status="Shortlisted").all()
    return render_template("closed_drive_history.html", this_drive=this_drive, this_company=this_company, total_applications=total_applications, total_placed=total_placed, placed_students=placed_students, shortlisted_students=shortlisted_students)

@app.route("/update_closed_drive/<int:drive_id>", methods=["GET", "POST"])
def update_closed_drive(drive_id):
    this_drive = Placement_Drive.query.filter_by(did=drive_id).first()
    this_company = Company.query.filter_by(cid=this_drive.cid).first()
    return render_template("C_drive_update.html", this_drive=this_drive, this_company=this_company)

@app.route("/A_C_edit/<int:user_id>", methods=["GET", "POST"])
def A_C_edit(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    exist_user = Company.query.filter_by(cid=user_id).first()
    uname = this_user.username
    if exist_user is None:
        if request.method == "POST":
            company_name = request.form["company_name"]
            company_about = request.form["company_about"]
            location = request.form["location"]
            hr_contact = request.form["hr_contact"]
            website_url = request.form["website_url"]
            com = Company(cid=user_id, username=uname, cname=company_name, cabout=company_about, clocation=location, hr_contact=hr_contact, c_website=website_url)
            db.session.add(com)
            db.session.commit()
            return redirect("/admin/1")
    else:
        if request.method == "POST":
            exist_user.cname = request.form["company_name"]
            exist_user.cabout = request.form["company_about"]
            exist_user.clocation = request.form["location"]
            exist_user.hr_contact = request.form["hr_contact"]
            exist_user.c_website = request.form["website_url"]
            db.session.commit()
            return redirect("/admin/1")
    return render_template("A_C_edit_profile.html", this_user=this_user)

@app.route("/A_S_edit/<int:user_id>", methods=["GET", "POST"])
def A_S_edit(user_id):
    this_user = User.query.filter_by(uid=user_id).first()
    exist_user = Student.query.filter_by(sid=user_id).first()
    uname = this_user.username
    if exist_user is None:
        if request.method == "POST":
            department = request.form["department"]
            gpa = request.form["gpa"]
            year_of_graduation = request.form["year_of_graduation"]
            stu = Student(sid=user_id, username=uname, sdepartment=department, gpa=gpa, yog=year_of_graduation)
            db.session.add(stu)
            db.session.commit()
            return redirect("/admin/1")
    else:
        if request.method == "POST":
            exist_user.sdepartment = request.form["department"]
            exist_user.gpa = request.form["gpa"]
            exist_user.yog = request.form["year_of_graduation"]
            db.session.commit()
            return redirect("/admin/1")
    return render_template("A_S_edit_profile.html", this_user=this_user,exist_user=exist_user)

@app.route("/C_company_history/<int:company_id>", methods=["GET", "POST"])
def C_company_history(company_id):
    this_company = Company.query.filter_by(cid=company_id).first()
    total_applications = len(Application.query.filter(Application.did.in_([drive.did for drive in Placement_Drive.query.filter_by(cid=company_id).all()])).all())
    total_placed = len(Application.query.filter_by(status="Selected").filter(Application.did.in_([drive.did for drive in Placement_Drive.query.filter_by(cid=company_id).all()])).all())    
    total_drives = len(Placement_Drive.query.filter_by(cid=company_id, status="Approved").all())
    students_placed = Application.query.filter_by(status="Selected").filter(Application.did.in_([drive.did for drive in Placement_Drive.query.filter_by(cid=company_id).all()])).all()
    return render_template("C_company_history.html", this_company=this_company, total_applications=total_applications, total_placed=total_placed, total_drives=total_drives, students_placed=students_placed)


@app.route("/search")
def search():
    search_word = request.args.get("search")
    key = request.args.get("key")
    if key == "student_id":
        results = Student.query.filter_by(sid = search_word).all()
    elif key == "student_name":
        results = Student.query.filter_by(sname = search_word).all()
    elif key == "student_contact":
        results = Student.query.filter_by(contact = search_word).all()
    elif key == "company_id":
        results = Company.query.filter_by(cid = search_word).all()
    elif key == "company_name":
        results = Company.query.filter_by(cname = search_word).all()
    return render_template("search_results.html",results=results,key=key)


@app.route("/summary")
def summary():

    ad=len(User.query.filter_by(type="Admin").all())
    co=len(User.query.filter_by(type="Company").all())
    st=len(User.query.filter_by(type="Student").all())
    total_users = ad + co + st

    ac=len(Student.query.filter_by(status="Activated").all())
    de=len(Student.query.filter_by(status="Deactivated").all())
    total_students = ac + de

    app_com=len(Company.query.filter_by(approval_status="Approved").all())
    rej_com=len(Company.query.filter_by(approval_status="Rejected").all())
    bl_com=len(Company.query.filter_by(approval_status="Blacklisted").all())
    total_companies = app_com + rej_com + bl_com

    pen_drive=len(Placement_Drive.query.filter_by(status="Pending").all())
    app_drive=len(Placement_Drive.query.filter_by(status="Approved").all())
    rej_drive=len(Placement_Drive.query.filter_by(status="Rejected").all())
    clo_drive=len(Placement_Drive.query.filter_by(status="Closed").all())
    total_drives = pen_drive + app_drive + rej_drive + clo_drive

    sh=len(Application.query.filter_by(status="Shortlisted").all())
    se=len(Application.query.filter_by(status="Selected").all())
    re=len(Application.query.filter_by(status="Rejected").all())
    rem=len(Application.query.filter_by(status="Applied").all())
    total_applications = sh + se + re + rem 
    
    #User Bar Graph
    labels = ["Admin","Companies","Students"]
    sizes =[ad,co,st]
    plt.bar(labels,sizes)
    plt.xlabel("Types of Users")
    plt.ylabel("No of Users")
    plt.title("User Distribution")
    plt.savefig("static/user_bar.png")
    plt.clf()

    #Student Account Status Pie Chart
    labels = ["Activated","Deactivated"]
    sizes =[ac,de]
    colors = ["lightgreen","lightcoral"]
    plt.pie(sizes,labels=labels,colors=colors,autopct = "%1.1f%%")
    plt.title("Student Status Distribution")
    plt.savefig("static/student_pie.png")
    plt.clf()

    #Company Approval Status Pie Chart
    labels = ["Approved","Rejected","Blacklisted"]
    sizes =[app_com,rej_com,bl_com]
    colors = ["lightgreen","lightcoral","lightgrey"]    
    plt.pie(sizes,labels=labels,colors=colors,autopct = "%1.1f%%")
    plt.title("Company Status Distribution")   
    plt.savefig("static/company_pie.png")
    plt.clf()

    #Drive Status Pie Chart
    labels = ["Pending","Approved","Rejected","Closed"]
    sizes =[pen_drive,app_drive,rej_drive,clo_drive]
    colors = ["lightyellow","lightgreen","lightcoral","lightgrey"]   
    plt.pie(sizes,labels=labels,colors=colors,autopct = "%1.1f%%")
    plt.title("Placement Drive Status Distribution")
    plt.savefig("static/drive_pie.png")
    plt.clf()

    #Application Status Pie Chart
    labels = ["Shortlisted","Selected","Rejected","Remaining"]
    sizes =[sh,se,re,rem]
    colors = ["lightyellow","lightgreen","lightcoral","lightgrey"]
    plt.pie(sizes,labels=labels,colors=colors,autopct = "%1.1f%%")
    plt.title("Application Status Distribution")
    plt.savefig("static/application_pie.png")
    plt.clf()

    return render_template("summary.html", total_users=total_users, total_students=total_students, total_companies=total_companies, total_drives=total_drives, total_applications=total_applications, ad=ad, co=co, st=st, ac=ac, de=de, app_com=app_com, rej_com=rej_com, bl_com=bl_com, pen_drive=pen_drive, app_drive=app_drive, rej_drive=rej_drive, clo_drive=clo_drive, sh=sh, se=se, re=re, rem=rem)

