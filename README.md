# 🏦 Banking System

A web-based **Banking System** developed using **Python and Django**. The project provides basic banking functionality along with user profile management, fixed deposit calculations, transaction management, and transaction PDF generation.

---

## 🛠️ Technologies & Libraries

* **Python**
* **Django** – Web framework
* **SQLite** – Database
* **python-dateutil** – Date calculations using `relativedelta`
* **Pillow** – Image handling and profile picture uploads
* **ReportLab** – PDF generation

---

## 📋 Prerequisites

Before running the project, make sure **Python** is installed on your system.

### Verify Python Installation

```powershell
py --version
```

This command checks whether Python is available and displays the installed version.

---

## 📦 Installation

### 1. Install Django

```powershell
py -m pip install django
```

Installs the Django web framework required to run the project.

### 2. Install python-dateutil

```powershell
py -m pip install python-dateutil
```

Required for date calculations and `relativedelta` functionality used in Fixed Deposit calculations.

### 3. Install Pillow

```powershell
py -m pip install Pillow
```

Used for image handling, including profile picture uploads through Django's `ImageField`.

### 4. Install ReportLab

```powershell
py -m pip install reportlab
```

Used for generating transaction-related PDF documents.

---

## 🗄️ Database Setup

Navigate to the project directory:

```powershell
cd "d:\bank_systemClg\bank_systemClg\bank_system"
```

Run the database migrations:

```powershell
py manage.py migrate
```

This applies all pending Django database migrations using the project's existing **SQLite database**.

---

## 🔍 Check the Project for Errors

Before starting the server, you can verify that the Django project is configured correctly:

```powershell
py manage.py check
```

If everything is configured correctly, Django will report that no issues were found.

---

## 🚀 Run the Project

From the project root directory:

```powershell
cd "d:\bank_systemClg\bank_systemClg\bank_system"
```

Start the Django development server:

```powershell
py manage.py runserver
```

The application will be available at:

**http://127.0.0.1:8000/**

The Django development server automatically watches for file changes and reloads the application when necessary.

---

## 🌐 Open the Application

You can open the application directly in Google Chrome using:

```powershell
start chrome "http://127.0.0.1:8000/"
```

Alternatively, open the following URL manually in any web browser:

**http://127.0.0.1:8000/**

---

## 👨‍💻 Django Admin Access

If you want to access the Django Admin Panel, create a superuser after running the migrations:

```powershell
py manage.py createsuperuser
```

Follow the instructions in the terminal to create the admin account.

After starting the server, the Django Admin Panel can usually be accessed at:

**http://127.0.0.1:8000/admin/**

---

## ⚠️ Troubleshooting

### Permission Issues

If you encounter permission-related issues, try running **PowerShell as Administrator**.

> **Note:** `sudo` is generally used on Linux/macOS. On Windows, use an elevated PowerShell or Command Prompt instead.

### Port Already in Use

If port `8000` is already being used, you can start Django on another port:

```powershell
py manage.py runserver 8080
```

The application will then be available at:

**http://127.0.0.1:8080/**

---

## 🏭 Production Note

The `runserver` command is intended for **development purposes** and is not recommended for production deployment.

For production environments, Django recommends using a proper **WSGI server**, such as **Gunicorn**, along with an appropriate production web-server setup.

---

## 📌 Quick Start

For a quick setup, run the following commands from the project directory:

```powershell
py --version

py -m pip install django
py -m pip install python-dateutil
py -m pip install Pillow
py -m pip install reportlab

py manage.py check
py manage.py migrate
py manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

---

## 📁 Project Type

**Banking System Web Application**

**Built with:** Python + Django + SQLite
