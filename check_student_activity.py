import os
import sys
import logging
import argparse
import getpass
from datetime import datetime, timedelta
import csv
import requests
from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.user import User
from canvasapi.exceptions import CanvasException
import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('canvas_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class CanvasActivityMonitor:
    def __init__(self):
        self.canvas = None
        self.courses = []
        self.results = {}

    def setup_canvas_connection(self):
        """Set up connection to Canvas LMS using API key and URL."""
        while True:
            try:
                base_url = input("Enter Canvas URL (e.g., https://yourschool.instructure.com): ").strip()
                print("Enter your Canvas API key (input will be hidden):")
                api_key = getpass.getpass(prompt='')
                
                print("Attempting to connect to Canvas...")
                self.canvas = Canvas(base_url, api_key)
                self.canvas.get_current_user()
                logging.info("Successfully connected to Canvas")
                return
                
            except CanvasException as e:
                print(f"\nFailed to connect to Canvas: {str(e)}")
                print("Please try again with valid credentials.\n")
            except requests.exceptions.RequestException as e:
                print(f"\nNetwork error: {str(e)}")
                print("Please check your internet connection and try again.\n")

    def add_course_ids(self):
        """Prompt user to input course IDs and validate them."""
        while True:
            try:
                course_id = input("\nEnter course ID (or 'done' to finish): ").strip()
                if not course_id:
                    print("Please enter a valid course ID or 'done' to finish.")
                    continue
                    
                if course_id.lower() == 'done':
                    if not self.courses:
                        print("Please add at least one course before proceeding.")
                        continue
                    break
                
                try:
                    course_id = int(course_id)
                except ValueError:
                    print("Please enter a valid numeric course ID.")
                    continue
                
                course = self.canvas.get_course(course_id)
                self.courses.append(course)
                logging.info(f"Added course: {course.name} (ID: {course.id})")                

            except CanvasException as e:
                logging.error(f"Error adding course {course_id}: {str(e)}")

    def get_inactivity_threshold(self):
        """Get user's choice for inactivity threshold."""
        while True:
            print("\nSelect inactivity threshold:")
            print("1) Show students who haven't logged in for 7 days")
            print("2) Show students who haven't logged in for 14 days")
            print("3) Show students who have never logged in")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice in ['1', '2', '3']:
                return {
                    '1': 7,
                    '2': 14,
                    '3': -1  # Special value for never logged in
                }[choice]
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    def check_student_activity(self, days_threshold):
        """Check student activity in all added courses."""
        for course in self.courses:
            logging.info(f"\nChecking activity for course: {course.name}")
            inactive_students = []
            
            try:
                students = []
                for student in course.get_users(enrollment_type=['student'], include=['email']):
                    students.append(student)
                
                with tqdm.tqdm(total=len(students), desc="Checking students") as pbar:
                    for student in students:
                        try:
                            enrollments = list(course.get_enrollments(user_id=student.id))
                            
                            if enrollments:
                                enrollment = enrollments[0]
                                last_activity = enrollment.last_activity_at
                                
                                if days_threshold == -1:
                                    # Check for students who have never logged in
                                    if not last_activity:
                                        inactive_students.append({
                                            'name': student.name,
                                            'id': student.id,
                                            'email': getattr(student, 'email', 'N/A'),
                                            'last_login': 'Never',
                                            'days_inactive': 'N/A'
                                        })
                                elif last_activity:
                                    last_activity_date = datetime.strptime(last_activity, "%Y-%m-%dT%H:%M:%SZ")
                                    days_since_login = (datetime.utcnow() - last_activity_date).days
                                    
                                    if days_since_login > days_threshold:
                                        inactive_students.append({
                                            'name': student.name,
                                            'id': student.id,
                                            'email': getattr(student, 'email', 'N/A'),
                                            'last_login': last_activity_date.strftime("%Y-%m-%d"),
                                            'days_inactive': days_since_login
                                        })
                                else:
                                    # Include students with no login record for all thresholds
                                    inactive_students.append({
                                        'name': student.name,
                                        'id': student.id,
                                        'email': getattr(student, 'email', 'N/A'),
                                        'last_login': 'Never',
                                        'days_inactive': 'N/A'
                                    })
                            
                            pbar.update(1)
                            
                        except CanvasException as e:
                            logging.error(f"Error checking student {student.id}: {str(e)}")
                            pbar.update(1)
                            continue
                
                self.results[course.id] = {
                    'course_name': course.name,
                    'total_students': len(students),
                    'inactive_students': inactive_students,
                    'days_threshold': days_threshold
                }
                
            except CanvasException as e:
                logging.error(f"Error checking course {course.id}: {str(e)}")

    def display_results(self):
        """Display results in an organized format."""
        for course_id, data in self.results.items():
            print(f"\n{'='*80}")
            print(f"Course: {data['course_name']} (ID: {course_id})")
            print(f"Total Students: {data['total_students']}")
            
            threshold_text = "never logged in" if data['days_threshold'] == -1 else f"inactive for {data['days_threshold']}+ days"
            print(f"Students {threshold_text}: {len(data['inactive_students'])}")
            
            if data['inactive_students']:
                print(f"\nInactive Students List:")
                print(f"{'Name':<30} {'ID':<10} {'Email':<30} {'Last Login':<12} {'Days Inactive':<15}")
                print('-'*97)
                
                for student in data['inactive_students']:
                    print(f"{student['name']:<30} {student['id']:<10} {student['email']:<30} {student['last_login']:<12} {student['days_inactive']:<15}")
            else:
                print("\nNo students found matching the inactivity criteria.")

    def export_results(self):
        """Export results to a CSV file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"canvas_activity_report_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Course Name', 'Course ID', 'Student Name', 'Student ID', 
                               'Email', 'Last Login', 'Days Inactive'])
                
                for course_id, data in self.results.items():
                    for student in data['inactive_students']:
                        writer.writerow([
                            data['course_name'],
                            course_id,
                            student['name'],
                            student['id'],
                            student['email'],
                            student['last_login'],
                            student['days_inactive']
                        ])
            
            logging.info(f"Results exported to {filename}")
            
        except IOError as e:
            logging.error(f"Error exporting results: {str(e)}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Monitor student activity in Canvas LMS courses.')
    parser.add_argument('--export', action='store_true', help='Export results to CSV file')
    return parser.parse_args()

def main():
    try:
        args = parse_arguments()
        monitor = CanvasActivityMonitor()
        monitor.setup_canvas_connection()
        monitor.add_course_ids()
        
        if not monitor.courses:
            logging.error("No valid courses added. Exiting.")
            sys.exit(1)
        
        # Get inactivity threshold from user
        print("\nSpecify how you want to check student activity:")
        days_threshold = monitor.get_inactivity_threshold()
        
        # Check student activity
        print("\nChecking student activity...")
        monitor.check_student_activity(days_threshold)
        monitor.display_results()
        
        if args.export:
            monitor.export_results()
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()