1. Verify Python Installation
•	py --version
•	Checks if Python is available and shows the version.
2. Install Django
•	py -m pip install django
•	Installs the Django web framework.
3. Install python-dateutil (for date calculations in models)
•	py -m pip install python-dateutil
•	Required for the relativedelta functionality in FixedDeposit calculations.
4. Install Pillow (for image handling)
•	py -m pip install Pillow
•	Needed for handling profile picture uploads (ImageField in models).
•	5. Install reportlab (for PDF generation)
•	py -m pip install reportlab
•	Used in views for generating transaction PDFs.
•	6. Navigate to Project Directory and Run Database Migrations
•	cd "d:\bank_systemClg\bank_systemClg\bank_system"; py manage.py migrate
•	Changes to the project root directory and applies any pending database schema changes (using the existing SQLite database).
•	7. Start the Django Development Server
•	cd "d:\bank_systemClg\bank_systemClg\bank_system"; py manage.py runserver
•	Starts the web server at http://127.0.0.1:8000/. It runs in the background and watches for file changes.
8. Open the Application in Google Chrome
start chrome "http://127.0.0.1:8000/"
•	Launches Google Chrome and navigates to the running app. If Chrome isn't your default browser or isn't installed, you can manually open http://127.0.0.1:8000/ in any browser.
Additional Notes
•	If you encounter permission issues or need to run as admin, prepend commands with sudo (though on Windows, you might need to run PowerShell as Administrator).
•	For production, Django recommends using a WSGI server like Gunicorn instead of runserver.
•	If you want to create a superuser for admin access: After migrations, run py manage.py createsuperuser in the project directory.
•	To check for errors before running: py manage.py check in the project directory.

