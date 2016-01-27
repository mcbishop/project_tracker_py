"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM Students
        WHERE github = :github
        """
    db_cursor = db.session.execute(QUERY, {'github': github})
    row = db_cursor.fetchone() 
    print "Student: %s %s\nGithub account: %s" % (row[0], row[1], row[2])


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """INSERT INTO students VALUES (:first_name, :last_name, :github)"""
    db_cursor = db.session.execute(QUERY, {'first_name': first_name, 'last_name': last_name, 'github': github})

    print "Successfully added student: %s %s" % (first_name, last_name)
    db.session.commit()


def get_project_by_title(title):
    """Given a project title, print information about the project."""
    
    try: 
        QUERY = """SELECT title, description, max_grade 
               FROM projects
               where title = :title
               """ 
        db_cursor = db.session.execute(QUERY, {'title': title,})
        results = db_cursor.fetchone()
        db.session.commit()

        print "Project title: %s \n \
               Project description: %s \n \
               Project max grade: %s" % (results[0],results[1],results[2])
    except:
        print "No such project exists."


def add_project(title, max_grade, description):
    """Given a project title, description and max grade, add to project table and print confirmation."""
    
    try:
        description = " ".join(description)
        QUERY = """INSERT INTO projects VALUES (:title, :max_grade, :description)"""
        db_cursor = db.session.execute(QUERY, {'title': title, 'max_grade': max_grade, 'description':description})    
        db.session.commit()
    
        print "Project %s successfully added to database." % (title)
    
    except:
        print "Invalid project title or max grade value."

def get_grade_by_github(github):
    """Given a student's github name, get all projects and grades."""
    try:
        QUERY = """SELECT project_title, grade from grades WHERE student_github = :github"""

        db_cursor = db.session.execute(QUERY, {'github':github,})
        results = db_cursor.fetchall()
        db.session.commit()

        for item in results:
            print "Project name: %s Project Grade: %s" %(item[0], item[1])
    except:
        print "No such github exists."


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""
    
    try:
        QUERY = """SELECT grade FROM grades
               WHERE student_github = :github AND project_title = :title
               """
        db_cursor = db.session.execute(QUERY, {'github': github, 'title': title,})
        results = db_cursor.fetchone()
        db.session.commit()
        print "Student github: %s \n \
               Project Title: %s \n \
               Student Grade: %s" % (github, title, results[0])
    except:
        print "No such title or student exists."


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""

    try:
        QUERY = """INSERT INTO grades VALUES (:github, :title, :grade)"""

        db_cursor = db.session.execute(QUERY, {'github': github, 'title': title, 'grade': grade,})

        print "Successfully added grade for student %s, project %s: %s" %(github, title, grade)
        db.session.commit()

    except:
        print "Invalid github or project title."


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        try:
            input_string = raw_input("HBA Database> ")
            tokens = input_string.split()
            command = tokens[0]
            args = tokens[1:]

            if command == "student":
                github = args[0]
                get_student_by_github(github)

            elif command == "new_student":
                first_name, last_name, github = args   # unpack!
                make_new_student(first_name, last_name, github)

            elif command == "get_project":
                title = args[0]
                get_project_by_title(title)

            elif command == "get_grade":
                github, title = args
                get_grade_by_github_title(github, title)

            elif command == "assign_grade":
                github, title, grade = args
                assign_grade(github, title, grade)

            elif command == "get_all_grades":
                github = args[0]
                get_grade_by_github(github)

            elif command == "add_project":
                title = args[0] 
                max_grade = args[1] 
                description = args[2:]
                add_project(title, max_grade, description)
            else:
                if command != "quit":
                    print "Invalid Entry. Try again."

        except ValueError:
            print "Incorrect number of arguments. Please retry."


if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    handle_input()

    db.session.close()
