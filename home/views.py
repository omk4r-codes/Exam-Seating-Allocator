from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from home.models import Addstudent
from home.models import Addclassrooms
import json
import random
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Create your views here.
def index(request):
    if request.user.is_anonymous:
        return redirect("/login")
    return render(request, "index.html")

def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "login.html")
    return render(request, "login.html")

def logoutUser(request):
    logout(request)
    return redirect("/login")

def addstudents(request):
    if request.method == "POST":
        name = request.POST.get('name')
        mis = request.POST.get('mis')
        branch = request.POST.get('branch')
        year = request.POST.get('year')

        
        student = Addstudent(name=name, mis=mis, branch=branch, year=year)
        student.save()

    return render(request, "addstudents.html")

def addclassrooms(request):
    if request.method == "POST":
        name = request.POST.get('name')
        seats = request.POST.get('seats')
        
        classroom = Addclassrooms(name=name, seats= seats)
        classroom.save()

    return render(request, "addclassrooms.html")


def save_students_to_json():
        # Retrieve all instances of Addstudent model
        students = Addstudent.objects.all()

        # Serialize instances into JSON format
        serialized_students = []
        for student in students:
            serialized_student = {
                "name": student.name,
                "roll_no": student.mis,
                "branch": student.branch,
                "year": student.year
            }
            serialized_students.append(serialized_student)

        # Write serialized data to a JSON file
        with open('students.json', 'w') as f:
            json.dump(serialized_students, f)


def save_classrooms_to_json():
    classrooms = Addclassrooms.objects.all()
    serialized_classrooms = []
    for classroom in classrooms:
        serialized_classroom = {
            "classroom_name": classroom.name,
            "seats":classroom.seats
        }
        serialized_classrooms.append(serialized_classroom)
    
    with open('classrooms.json', 'w') as f:
        json.dump(serialized_classrooms, f)



def generateseating(request):
    if request.method == "POST":
        branch = request.POST.get('branch')
        year = request.POST.get('year')
        classrooms = []
        classrooms = request.POST.getlist('classrooms[]')

        print(branch, year, classrooms)
        
        save_students_to_json()
        save_classrooms_to_json()
        result = allocate_seats(branch, year, classrooms)

        # Write result to file
        if result:
            write_allocation(result)
            # Generate PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="seating_arrangement.pdf"'

            # Generate PDF content
            pdf = SimpleDocTemplate(response, pagesize=letter)
            styles = getSampleStyleSheet()
            pdf_content = []

            pdf_content.append(Paragraph("Seating Arrangement", styles['Title']))
            pdf_content.append(Spacer(1, 12))

            for entry in result:
                pdf_content.append(Paragraph(f"{entry['roll_no']} - {entry['classroom_name']} {entry['desk_no']}", styles['Normal']))
                pdf_content.append(Spacer(1, 6))

            pdf.build(pdf_content)
            
            return response
        return HttpResponse("Seating arrangement has been successfully written to 'seating_arrangement.txt'.")


    return render(request, "generateseating.html")

def allocate_seats(branch, year, available_classrooms_input):
    # Read data from database
    students = read_students_from_database()
    classrooms = read_classrooms_from_database()

    # Filter students based on given branches and years
    filtered_students = [student for student in students if student['branch'] == branch and student['year'] == year]

    # Filter available classrooms based on user input
    available_classrooms = [classroom for classroom in classrooms if classroom['classroom_name'] in available_classrooms_input]

    # Perform seat allocation
    result = allocate_seats_greedy(filtered_students, available_classrooms)

    return result

def read_students_from_database():
    # Retrieve all instances of Addstudent model
    students = Addstudent.objects.all()

    # Serialize instances into JSON-like format
    serialized_students = []
    for student in students:
        serialized_student = {
            "name": student.name,
            "roll_no": student.mis,
            "branch": student.branch,
            "year": student.year
        }
        serialized_students.append(serialized_student)

    return serialized_students

def read_classrooms_from_database():
    classrooms = Addclassrooms.objects.all()
    serialized_classrooms = []
    for classroom in classrooms:
        serialized_classroom = {
            "classroom_name": classroom.name,
            "seats": classroom.seats
        }
        serialized_classrooms.append(serialized_classroom)

    return serialized_classrooms

def write_allocation(result):
    with open('seating_arrangement.txt', 'w') as file:
        for entry in result:
            file.write(f"{entry['roll_no']} - {entry['classroom_name']} {entry['desk_no']}\n")

def allocate_seats_greedy(students, available_classrooms):
    # Shuffle both students and available classrooms
    random.shuffle(students)
    random.shuffle(available_classrooms)

    result = []

    # Assign seats to students greedily
    for student in students:
        for classroom in available_classrooms:
            if 'occupied' not in classroom:
                classroom['occupied'] = 0
            if classroom['seats'] > classroom.get('occupied', 0):
                result.append({'roll_no': student['roll_no'], 'classroom_name': classroom['classroom_name'], 'desk_no': classroom['seats'] - classroom.get('occupied', 0) + 1})
                classroom['occupied'] += 1
                break

    return result