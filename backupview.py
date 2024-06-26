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
from collections import defaultdict


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

        # print(branch, year, classrooms)
        
        save_students_to_json()
        save_classrooms_to_json()
        result = allocate_seats(branch, year, classrooms)

        # print(result)

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
    filtered_students = [student for student in students if student['branch'] ==  branch and student['year'] == year]

    # Filter available classrooms based on user input
    available_classrooms = [classroom for classroom in classrooms if classroom['classroom_name'] in available_classrooms_input]

    print(f"{filtered_students} + {available_classrooms}")

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


def allocate_complex_seats(branches, year, available_classrooms_input):
    '''
        branches = ['Computer', 'EnTC', 'Metallurgy', 'Mechanical']
        year = TY
        classrooms =  ['AC-101', 'AC-102', 'AC-103', 'AC-104', 'AC-201', 'AC-202', 'AC-203', 'AC-204', 'EE-001', 'EE-002', 'EE-003', 'EE-101', 'EE-102', 'EE-103', 'Ex1', 'Ex2', 'Ex3']
    '''
    students = read_students_from_database()
    classrooms = read_classrooms_from_database()

    # print(students)
    print(classrooms)

    filtered_students = [student for student in students if student['branch'] in branches and student['year'] == year]

    available_classrooms = [classroom for classroom in classrooms if classroom['classroom_name'] in available_classrooms_input]

    result = allocate_seats_greedy_kp(filtered_students, available_classrooms)

    # result = f"{filtered_students} + {available_classrooms}"
    return result

def allocate_seats_greedy_kp(students, available_classrooms):
    result = []
    
    # Create dictionaries to keep track of available seats in each classroom
    classroom_seats = {classroom['classroom_name']: classroom['seats'] for classroom in available_classrooms}

    # Sort students based on priority of branch and year
    students.sort(key=lambda x: (x['branch'], x['year']))
    
    # Function to find available seat in a classroom
    def find_seat(classroom_name, required_seats, classroom_seats):
        if classroom_name in classroom_seats and classroom_seats[classroom_name] >= required_seats:
            classroom_seats[classroom_name] -= required_seats
            return True
        return False
    
    for student in students:
        branch = student['branch']
        year = student['year']
        required_seats = 1  # Assuming each student requires one seat
        
        if branch == 'Computer':
            # Priority: AC, Ex1, EE
            if find_seat('AC-101', required_seats, classroom_seats):
                classroom_name = 'AC-101'
            elif find_seat('AC-102', required_seats, classroom_seats):
                classroom_name = 'AC-102'
            elif find_seat('AC-103', required_seats, classroom_seats):
                classroom_name = 'AC-103'
            elif find_seat('AC-104', required_seats, classroom_seats):
                classroom_name = 'AC-104'
            elif find_seat('Ex1', required_seats, classroom_seats):
                classroom_name = 'Ex1'
            elif find_seat('EE-001', required_seats, classroom_seats):
                classroom_name = 'EE-001'
            else:
                # Handle case when no single seat available
                print("No available single seat for Computer branch student.")
                continue
                
        elif branch == 'EnTC':
            # Priority: Ex1, AC, EE
            if find_seat('Ex1', required_seats, classroom_seats):
                classroom_name = 'Ex1'
            elif find_seat('AC-101', required_seats, classroom_seats):
                classroom_name = 'AC-101'
            elif find_seat('AC-102', required_seats, classroom_seats):
                classroom_name = 'AC-102'
            elif find_seat('AC-103', required_seats, classroom_seats):
                classroom_name = 'AC-103'
            elif find_seat('AC-104', required_seats, classroom_seats):
                classroom_name = 'AC-104'
            elif find_seat('EE-001', required_seats, classroom_seats):
                classroom_name = 'EE-001'
            else:
                # Handle case when no single seat available
                print("No available single seat for EnTC branch student.")
                continue
                
        elif branch == 'Mechanical':
            # Priority: EE, AC, Ex1
            if find_seat('EE-001', required_seats, classroom_seats):
                classroom_name = 'EE-001'
            elif find_seat('EE-002', required_seats, classroom_seats):
                classroom_name = 'EE-002'
            elif find_seat('EE-003', required_seats, classroom_seats):
                classroom_name = 'EE-003'
            elif find_seat('AC-101', required_seats, classroom_seats):
                classroom_name = 'AC-101'
            elif find_seat('AC-102', required_seats, classroom_seats):
                classroom_name = 'AC-102'
            elif find_seat('AC-103', required_seats, classroom_seats):
                classroom_name = 'AC-103'
            elif find_seat('AC-104', required_seats, classroom_seats):
                classroom_name = 'AC-104'
            elif find_seat('Ex1', required_seats, classroom_seats):
                classroom_name = 'Ex1'
            else:
                # Handle case when no single seat available
                print("No available single seat for Mechanical branch student.")
                continue
                
        # Append student's seating information to result
        result.append({
            'roll_no': student['roll_no'],
            'classroom_name': classroom_name,
            'desk_no': classroom_seats[classroom_name] + 1
        })

    return result

def generatecomplex(request):
    if request.method == "POST":
        branches = request.POST.getlist('branches[]')
        year = request.POST.get('year')
        classrooms = request.POST.getlist('classrooms[]')

        print(branches, year, classrooms)

        with open('students.json', 'r') as f:
            students_data = json.load(f)

        with open('classrooms.json', 'r') as f:
            classrooms_data = json.load(f)


        result = allocate_complex_seats(branches, year, classrooms)

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

            serial_number = 1
            for entry in result:
                pdf_content.append(Paragraph(f"{serial_number}. {entry['roll_no']} - {entry['classroom_name']} {entry['desk_no']}", styles['Normal']))
                pdf_content.append(Spacer(1, 6))

                serial_number += 1
            pdf.build(pdf_content)
            
            return response
        return HttpResponse("Seating arrangement has been successfully written to 'seating_arrangement.txt'.")


    return render(request, "generatecomplex.html")