import flask_api
import sys
from flask_api import status, exceptions, FlaskAPI
from flask import Flask, render_template, redirect, request, jsonify, g, url_for
import pyodbc
import requests
import pandas as pd
#have to imnport for the database

app = FlaskAPI(__name__)
# app.run(host='0.0.0.0')


#returns connection to the database, if not connected creates it
def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect('Driver={ODBC DRIVER 17 for SQL Server};'
                'Server=your_server;'
                'Database=your_database;'
                'Trusted_Connection=yes;')
    return g.db

#closes conection and commits to database on teardown
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.commit()
        db.close()

#returns results of specified query as a dictionary
def query_db(query, args=(), one=False):
    print(args)
    cursor = get_db().cursor()
    cursor.execute(query, args)
    results = []
    if cursor.description:
        columns = [column[0] for column in cursor.description]        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
    cursor.commit()
    cursor.close()
    return (results[0] if results else None) if one else results

#initilization of the db connection done on startup
# @app.cli.command('init')
# def init_db():
#     with app.app_context():
#         db = get_db()
      
       # db.commit()



#TODO place holder method to be changed later, default path
@app.route('/')
def default():
    return render_template('index.html')

# method to retrieve info on all courses
@app.route('/courses', methods=['GET','POST'])
def return_all_courses():
    query = "SELECT * FROM COURSE, COURSE_SECTION  WHERE COURSE.COURSE_ID = COURSE_SECTION.COURSE_ID;"
    courses = query_db(query)
    print(type(courses))
    print(courses)  
    results = courses
    if courses:
        return render_template('showCourse.html', results=results )
    else:
        raise exceptions.NotFound()

@app.route('/courseID', methods=['GET'])
def return_student_courses():
    args = []    
    args.append(request.args.get('cwid'))
    # print(cwid)
    query = """SELECT * 
            FROM COURSE, COURSE_SECTION, STUDENT_TAKES_COURSE  
            WHERE STUDENT_TAKES_COURSE.CWID =? AND
                STUDENT_TAKES_COURSE.COURSE_ID = COURSE.COURSE_ID AND
                STUDENT_TAKES_COURSE.DEPARTMENT_ID = COURSE.DEPARTMENT_ID AND
                STUDENT_TAKES_COURSE.COURSE_ID = COURSE_SECTION.COURSE_ID AND 
                STUDENT_TAKES_COURSE.DEPARTMENT_ID = COURSE_SECTION.DEPARTMENT_ID AND
                STUDENT_TAKES_COURSE.SECTION_ID = COURSE_SECTION.SECTION_ID;"""
    courses = query_db( query, args )
    print(type(courses))
    print(courses)  
    results = courses

    if courses:
        return render_template('showStudentCourses.html', results=results)
    else:
        raise exceptions.NotFound()



@app.route('/course', methods=['GET', 'POST'])
def return_specific_course():
    args = []    
    args.append(request.args.get('courseID'))
    args.append(request.args.get('sectionID'))
    args.append(request.args.get('departmentID'))

    query =  """SELECT CS.Course_ID,
	            CS.Class_Time,
	            CS.Days_Of_Week,
	            CS.Department_ID,
	            CS.Employee_ID,
	            CS.Section_ID,
	            COURSE.Course_Name,
	            COURSE.Pre_req_course,
	            PROFESSOR.First_Name,
	            PROFESSOR.Last_Name,
	            PROFESSOR.Email,
	            PROFESSOR.Phone,
	            DEPARTMENT.Department_Name,
	            TEXTBOOK.ISBN,
	            TEXTBOOK.Author,
	            TEXTBOOK.Name
            FROM COURSE_SECTION as CS
            JOIN COURSE ON COURSE.Course_ID = CS.Course_ID 
            JOIN PROFESSOR ON PROFESSOR.Employee_ID = CS.Employee_ID
            JOIN DEPARTMENT ON DEPARTMENT.Department_ID = CS.Department_ID
            Left JOIN (COURSE_SECTION_HAS_TEXTBOOK Left JOIN TEXTBOOK ON TEXTBOOK.ISBN= COURSE_SECTION_HAS_TEXTBOOK.ISBN) ON COURSE_SECTION_HAS_TEXTBOOK.Course_ID = CS.Course_ID
            Where CS.Course_ID =? AND
	            CS.Section_ID=? AND
	            CS.Department_ID =? AND
	            Course.Department_ID=CS.Department_ID; """

    course =query_db(query, args)
    results = course
    print(course)
    if course:
        return render_template('showSpecificCourse.html', results=results)
    else:
        raise exceptions.NotFound()



@app.route('/addCourse', methods=['POST', 'GET'])#not tested
def add_course():
    args = []
    args.append(request.args.get('cwid'))
    args.append(request.args.get('courseID'))
    args.append(request.args.get('sectionID'))
    args.append(request.args.get('departmentID'))
  
    query ="""Insert into STUDENT_TAKES_COURSE
	        values(?, ?, ?, ?);"""

    try:
        query_db(query, args)
        
        return redirect('/')
    except Exception as e:
        return 'Cannot add course', status.HTTP_409_CONFLICT
    
    

@app.route('/dropCourse', methods=['GET','DELETE'])#not tested
def drop_course():
    args = []
    args.append(request.args.get('cwid'))
    args.append(request.args.get('courseID'))
    args.append(request.args.get('sectionID'))
    args.append(request.args.get('departmentID'))
    


    query="""DELETE FROM STUDENT_TAKES_COURSE
            WHERE CWID=? AND Course_ID=? AND Section_ID=? AND Department_ID=?;"""
    try:    
        query_db(query, args)
        return redirect('/')
    except Exception as e:
        return 'Cannot add course', status.HTTP_409_CONFLICT
    
    return {"Message":"Course Sucessfully Dropped"}, status.HTTP_200_OK


if __name__ == "__main__":
    app.run(debug=True)
