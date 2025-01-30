# Check Student Inactivity

A Python tool to monitor student activity in Canvas LMS courses. This tool helps faculty identify students who haven't logged into their Canvas courses within specified timeframes.

## Features

- Check multiple courses at once
- Multiple inactivity thresholds:
  - Students inactive for 7+ days
  - Students inactive for 14+ days
  - Students who have never logged in
- Displays student names, IDs, email addresses, and last login dates
- Progress bar for monitoring check progress
- Option to export results to CSV
- Secure API key handling

## Prerequisites

1. Python 3.6 or higher
2. Canvas API Key (see instructions below)
3. Course IDs for the courses you want to check

## Installation

1. Clone this repository:
```bash
git clone https://github.com/elblanco2/Check-Student-Inactivity.git
cd Check-Student-Inactivity
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Getting Your Canvas API Key

1. Log into Canvas
2. Click on "Account" in the global navigation menu
3. Click on "Settings"
4. Scroll to the "Approved Integrations" section
5. Click on "New Access Token"
6. Add a purpose (e.g., "Student Activity Monitor")
7. Copy the generated token (Note: You can only see this once!)

## Finding Course IDs

Course IDs can be found in the URL when viewing a course in Canvas. For example:
```
https://yourschool.instructure.com/courses/123456
```
In this URL, `123456` is the course ID.

## Usage

1. Run the script:
```bash
python check_student_activity.py
```

2. Enter your Canvas information when prompted:
   - Canvas URL (e.g., https://yourschool.instructure.com)
   - API Key (input will be hidden)

3. Enter course IDs one at a time:
   - Type the course ID and press Enter
   - Type 'done' when finished adding courses

4. Select an inactivity threshold:
   1. Show students who haven't logged in for 7 days
   2. Show students who haven't logged in for 14 days
   3. Show students who have never logged in

5. Review the results:
   - Results will be displayed in the terminal
   - If you want to save results, use the --export flag when running the script:
     ```bash
     python check_student_activity.py --export
     ```

## Output Example

```
===========================================
Course: MATH101 - Introduction to Mathematics (ID: 123456)
Total Students: 30
Students inactive for 7+ days: 5

Inactive Students List:
Name                           ID         Email                          Last Login  Days Inactive
---------------------------------------------------------------------------------
John Doe                      987654     john.doe@email.com            2025-01-20  10
Jane Smith                    987655     jane.smith@email.com          2025-01-21  9
...
```

## Security Notes

- The script never saves your API key
- API key input is hidden when typing
- Use a dedicated API key for this tool
- Revoke the API key from Canvas when no longer needed

## Troubleshooting

1. If you get a connection error:
   - Check your Canvas URL
   - Verify your API key
   - Ensure you have internet connectivity

2. If you get "Invalid course ID":
   - Make sure you have the correct course ID
   - Verify you have permission to access the course

3. If student emails show as "N/A":
   - Verify you have permission to view student email addresses in Canvas

## Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Submit an issue on GitHub
3. Contact your institution's Canvas administrator

## License

This project is licensed under the MIT License - see the LICENSE file for details.
