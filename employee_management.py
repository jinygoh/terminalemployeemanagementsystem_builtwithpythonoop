"""
Employee Management System for BitFutura
Based on OOP principles for managing employee records via a command-line interface.
Handles CRUD operations, listing all employees, and department-wise reports.
"""
"""
4. CRUD Operations:
    -add_employee: Prompts for ID, name, department, salary, email, contact details. Uses new validation. (Project Requirements: Add Employee, Requirement 1).
    -view_employee: Finds by ID and displays employee details. (Project Requirements: View Employee).
    -update_employee: Finds by ID, allows updating Department, Salary, Email, Contact Details with validation. (Project Requirements: Update Employee).
    -delete_employee: Finds by ID, asks for confirmation, then deletes. (Project Requirements: Delete Employee).
5. Listing & Reporting:
    -list_all_employees: Provides a simple, formatted list of all employees. (Project Requirements: List All Employees).
    -generate_department_report: List Departments and Employess in those departments. (Project Requirements: Department Wise Report, Requirement 2: Design of report layout).
6. Email Confirmation: add_employee calls _send_confirmation_email (now uses integrated EmailSender) upon successful addition. (Requirement 3: Send confirmation email).
7. OOP Principles: The code maintains OOP structure:
    -Encapsulation: Data (_employees_list, _file_name) and internal methods (_load_employees, _find_employee_by_id, etc.) are kept within the EmployeeManagementSystem class, accessed via public methods. The Employee class encapsulates employee data and related methods (to_dict, from_dict).
    -Abstraction: Users interact with the system through high-level methods (add_employee, view_employee, etc.) without needing to know the internal file handling or list management details.
    -Classes/Objects: Uses Employee, EmailSender and EmployeeManagementSystem classes to model real-world entities and their management.
8. File Handling: Uses CSV (employees.csv) for persistent storage, loading on start and saving on changes/exit. Error handling for file operations included.
9. Command-Line Interface: The run() method provides the menu-driven CLI as required.
10. Testability: The separation into classes and methods (especially validation functions) makes the code more amenable to unit testing (though the tests themselves are not generated here, as per Requirement 4).
"""
import re # used for robust input format validation
import os # Required for checking file existence and path manipulation
import smtplib # For actual email sending
from email.mime.text import MIMEText # Used to create text parts of an email message
from email.mime.multipart import MIMEMultipart # Used to create multi-part messages

# --- File Handling Configuration ---
# Get the directory of the current script
# This makes the credential and data file paths relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_NAME = "employees.csv" # This will be joined with SCRIPT_DIR in __init__
DELIMITER = ","
EMPLOYEE_KEYS = ["Employee ID", "Name", "Department", "Salary", "Email", "Contact Details"]

# --- Email Sending Configuration ---
SENDER_EMAIL_PATH = os.path.join(SCRIPT_DIR, "username.txt")  # Path to file containing sender's Gmail address
SENDER_APP_PASSWORD_PATH = os.path.join(SCRIPT_DIR, "password.txt") # Path to file containing sender's Gmail App Password

DEFAULT_CONFIRMATION_SUBJECT = "Welcome to BitFutura!"
DEFAULT_CONFIRMATION_BODY_TEMPLATE = """
Hi {employee_name},

Welcome aboard to BitFutura! We are excited to have you join our team.

Your employee record (ID: {employee_id}) has been successfully created in our system.

Best regards,
BitFutura HR
"""

# --- Validation Functions ---

def is_valid_employee_id_format(employee_id):
    """
    Validates the format of the Employee ID.
    Must be non-empty and alphanumeric (simple validation).
    """
    if not employee_id:
        return False, "Employee ID cannot be empty."
    if not employee_id.isalnum():
         return False, "Employee ID must be alphanumeric (letters and numbers only)."
    return True, ""

def is_valid_name_format(name):
    """
    Validates the format of the Employee Name.
    Must be non-empty and contain only alphabetic characters and spaces.
    """
    if not name or not name.strip():
        return False, "Name cannot be empty."
    if not re.fullmatch(r'[a-zA-Z ]+', name.strip()):
        return False, "Name must contain only alphabetic characters and spaces."
    return True, ""

def is_valid_department_format(department):
    """
    Validates the format of the Department.
    Must be non-empty. Can contain letters, numbers, spaces, hyphens.
    """
    if not department or not department.strip():
        return False, "Department cannot be empty."
    if not re.fullmatch(r'[a-zA-Z0-9 \-]+', department.strip()):
         return False, "Department can only contain letters, numbers, spaces, and hyphens."
    return True, ""

def is_valid_salary_format(salary_str):
    """
    Validates the format of the Salary.
    Must be a non-empty positive number (integer or float).
    """
    if not salary_str or not salary_str.strip():
        return False, "Salary cannot be empty."
    try:
        salary = float(salary_str)
        if salary < 0:
            return False, "Salary cannot be negative."
    except ValueError:
        return False, "Salary must be a valid number (e.g., 50000 or 65000.50)."
    return True, ""

def is_valid_email_format(email):
    """
    Validates the format of the Email Address.
    Must be non-empty and follow a basic email format (contain "@" and ".").
    Does not allow spaces.
    """
    if not email or not email.strip():
        return False, "Email cannot be empty."
    if not re.match(r'^\S+@\S+\.\S+$', email.strip()):
         return False, "Invalid email format (must contain '@' and '.', no spaces allowed)."
    return True, ""

def is_valid_contact_details_format(contact_details):
    """
    Validates the Contact Details.
    Must be non-empty (simple validation). Can include phone, address etc.
    """
    if not contact_details or not contact_details.strip():
        return False, "Contact Details cannot be empty."
    return True, ""

# --- Email Sender Class (Integrated from sendingemail.py) ---
class EmailSender:
    '''
    This class handles the email sending process using Gmail SMTP.
    '''
    def __init__(self, sender_email, sender_app_password):
        '''
        Initialize the EmailSender instance with the sender's email and App Password.
        :param sender_email: The email address of the sender.
        :param sender_app_password: The App Password of the sender's Gmail account.
        '''
        self.sender_email = sender_email
        self.sender_app_password = sender_app_password

    def send_email(self, recipient_name, recipient_email, subject, body):
        '''
        Sends an email to a specified recipient.
        :param recipient_name: The recipient's name (used for logging/personalization if needed).
        :param recipient_email: The recipient's email address.
        :param subject: The email subject.
        :param body: The email body.
        '''
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        try:
            print("\nAttempting to send confirmation email...")
            print("Connecting to email server (smtp.gmail.com:465)...")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                print("Logging in to Gmail...")
                server.login(self.sender_email, self.sender_app_password)
                print(f"Sending email to {recipient_email} (Name: {recipient_name})...")
                server.sendmail(self.sender_email, recipient_email, message.as_string())
                print(f"Email successfully sent to {recipient_email}.")
        except smtplib.SMTPAuthenticationError:
            print("\nEmail not sent. Authentication failed. Check sender email/App Password.")
            print("Ensure 'Less secure app access' is NOT needed if using App Passwords, as App Passwords bypass this setting.")
            print(f"Sender email used: {self.sender_email}")
        except smtplib.SMTPConnectError:
            print("\nEmail not sent. Could not connect to Gmail SMTP server.")
            print("Check network connection and server address/port (smtp.gmail.com:465).")
        except smtplib.SMTPServerDisconnected:
            print("\nEmail not sent. Server disconnected unexpectedly.")
        except smtplib.SMTPException as smtp_e:
            print(f"\nEmail not sent due to an SMTP error: {smtp_e}")
        except Exception as e:
            print("\nEmail not sent due to an unexpected error during sending process.")
            print("Error details:", e)

# --- Employee Class (OOP Core) ---

class Employee:
    """Represents a single employee record."""
    def __init__(self, employee_id, name, department, salary, email, contact_details):
        if not is_valid_employee_id_format(employee_id)[0]: raise ValueError(is_valid_employee_id_format(employee_id)[1])
        if not is_valid_name_format(name)[0]: raise ValueError(is_valid_name_format(name)[1])
        if not is_valid_department_format(department)[0]: raise ValueError(is_valid_department_format(department)[1])
        if not is_valid_salary_format(str(salary))[0]: raise ValueError(is_valid_salary_format(str(salary))[1])
        if not is_valid_email_format(email)[0]: raise ValueError(is_valid_email_format(email)[1])
        if not is_valid_contact_details_format(contact_details)[0]: raise ValueError(is_valid_contact_details_format(contact_details)[1])

        self.employee_id = employee_id.strip()
        self.name = name.strip()
        self.department = department.strip()
        self.salary = float(salary)
        self.email = email.strip()
        self.contact_details = contact_details.strip()

    def to_dict(self):
        """Converts the Employee object's data into a dictionary."""
        return {
            "Employee ID": self.employee_id,
            "Name": self.name,
            "Department": self.department,
            "Salary": f"{self.salary:.2f}",
            "Email": self.email,
            "Contact Details": self.contact_details
        }

    @staticmethod
    def from_dict(data_dict):
        """Creates an Employee object from a dictionary."""
        try:
            salary_str = data_dict.get("Salary", "0")
            try:
                salary_float = float(salary_str)
            except ValueError:
                print(f"Error creating employee: Invalid salary format '{salary_str}'. Data: {data_dict}")
                return None

            return Employee(
                employee_id=data_dict.get("Employee ID", ""),
                name=data_dict.get("Name", ""),
                department=data_dict.get("Department", ""),
                salary=salary_float,
                email=data_dict.get("Email", ""),
                contact_details=data_dict.get("Contact Details", "")
            )
        except ValueError as e:
            print(f"Error creating employee object from dictionary: {e}. Data: {data_dict}")
            raise e
        except Exception as e:
            print(f"Unexpected error creating employee from dictionary: {e}. Data: {data_dict}")
            return None

    def __str__(self):
        """String representation for easily printing employee details."""
        return (f"ID: {self.employee_id}, Name: {self.name}, Dept: {self.department}, "
                f"Salary: {self.salary:.2f}, Email: {self.email}, Contact: {self.contact_details}")

# --- Employee Management System Class (OOP Core) ---

class EmployeeManagementSystem:
    """Manages the collection of employees and provides EMS application logic."""
    def __init__(self, file_name=FILE_NAME, delimiter=DELIMITER, employee_keys=EMPLOYEE_KEYS):
        # Construct the full path for the employee data file if it's not absolute
        if not os.path.isabs(file_name):
            self._file_name = os.path.join(SCRIPT_DIR, file_name)
        else:
            self._file_name = file_name
        self._delimiter = delimiter
        self._employee_keys = employee_keys
        self._employees_list = self._load_employees()

    def _load_employees(self):
        employees_data = []
        if os.path.exists(self._file_name):
            try:
                with open(self._file_name, 'r', encoding='utf-8') as f:
                    header = f.readline().strip().split(self._delimiter)
                    for line_num, line in enumerate(f, start=2):
                        line = line.strip()
                        if not line: continue
                        values = line.split(self._delimiter)
                        if len(values) == len(self._employee_keys):
                            try:
                                employee_dict = dict(zip(self._employee_keys, values))
                                employee_obj = Employee.from_dict(employee_dict)
                                if employee_obj:
                                    is_unique = True
                                    for existing_emp in employees_data:
                                        if existing_emp.employee_id == employee_obj.employee_id:
                                            print(f"Warning: Duplicate Employee ID '{employee_obj.employee_id}' found in file on line {line_num}. Skipping duplicate.")
                                            is_unique = False
                                            break
                                    if is_unique:
                                        employees_data.append(employee_obj)
                                else:
                                    print(f"Skipping invalid data on line {line_num} in {self._file_name} (Employee.from_dict returned None): {line}")
                            except ValueError as ve:
                                print(f"Skipping invalid data format on line {line_num} in {self._file_name}: {ve}. Line: {line}")
                            except Exception as e_inner:
                                print(f"Unexpected error processing line {line_num} in {self._file_name}: {e_inner}. Line: {line}")
                        else:
                            print(f"Skipping malformed line {line_num} in {self._file_name} (expected {len(self._employee_keys)} values, got {len(values)}): {line}")
                print(f"Successfully loaded {len(employees_data)} employee records from {self._file_name}.")
            except FileNotFoundError:
                 print(f"No data file found ({self._file_name}). Starting with an empty list.")
            except Exception as e:
                print(f"An error occurred while loading data from {self._file_name}: {e}")
                employees_data = []
        else:
            print(f"No data file found ({self._file_name}). Starting with an empty list.")
        return employees_data

    def _save_employees(self):
        try:
            with open(self._file_name, 'w', encoding='utf-8', newline='') as f:
                f.write(self._delimiter.join(self._employee_keys) + '\n')
                for employee_obj in self._employees_list:
                    emp_dict = employee_obj.to_dict()
                    values = [emp_dict.get(key, "") for key in self._employee_keys]
                    line = self._delimiter.join(values)
                    f.write(line + '\n')
        except IOError as e:
             print(f"An I/O error occurred while saving data to {self._file_name}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving data: {e}")

    def _find_employee_by_id(self, employee_id):
        for employee in self._employees_list:
            if employee.employee_id == employee_id:
                return employee
        return None

    def _find_employee_index_by_id(self, employee_id):
        for i, employee in enumerate(self._employees_list):
            if employee.employee_id == employee_id:
                return i
        return -1

    def _is_employee_id_unique(self, employee_id):
        return self._find_employee_by_id(employee_id) is None

    def _does_department_exist(self, department_name):
        if not department_name: return False
        dept_name_lower = department_name.lower()
        for employee in self._employees_list:
            if employee.department and employee.department.lower() == dept_name_lower:
                return True
        return False

    def _send_confirmation_email(self, employee_id, employee_email, employee_name):
        """
        Sends a confirmation email to the new employee using the EmailSender class.
        Credentials for the sender are read from SENDER_EMAIL_PATH and SENDER_APP_PASSWORD_PATH.
        These paths are now relative to the script's location.
        """
        print("\nPreparing to send confirmation email...")
        sender_email_address = None
        sender_app_pass = None

        try:
            # Read sender's email
            if not os.path.exists(SENDER_EMAIL_PATH):
                print(f"Error: Sender email file not found at {SENDER_EMAIL_PATH}.")
                raise FileNotFoundError(SENDER_EMAIL_PATH)
            with open(SENDER_EMAIL_PATH, 'r') as f:
                sender_email_address = f.readline().strip()
            if not sender_email_address:
                print(f"Error: Sender email file at {SENDER_EMAIL_PATH} is empty.")
                raise ValueError("Sender email is empty in file.")
            print(f"Sender email read from {SENDER_EMAIL_PATH}.")

            # Read sender's app password
            if not os.path.exists(SENDER_APP_PASSWORD_PATH):
                print(f"Error: Sender app password file not found at {SENDER_APP_PASSWORD_PATH}.")
                raise FileNotFoundError(SENDER_APP_PASSWORD_PATH)
            with open(SENDER_APP_PASSWORD_PATH, 'r') as f:
                sender_app_pass = f.readline().strip()
            if not sender_app_pass:
                print(f"Error: Sender app password file at {SENDER_APP_PASSWORD_PATH} is empty.")
                raise ValueError("Sender app password is empty in file.")
            print(f"Sender app password read from {SENDER_APP_PASSWORD_PATH}.")

            print("Sender credentials successfully read.")
            
            email_service = EmailSender(sender_email_address, sender_app_pass)
            subject = DEFAULT_CONFIRMATION_SUBJECT
            body = DEFAULT_CONFIRMATION_BODY_TEMPLATE.format(employee_name=employee_name, employee_id=employee_id)
            email_service.send_email(
                recipient_name=employee_name,
                recipient_email=employee_email,
                subject=subject,
                body=body
            )

        except FileNotFoundError as fnf_e:
            print(f"Email not sent: Prerequisite file missing: {fnf_e}")
            print("Please ensure sender email ('username.txt') and app password ('password.txt') files exist in the same directory as the script.")
            print(f"  Expected email file at: {SENDER_EMAIL_PATH}")
            print(f"  Expected password file at: {SENDER_APP_PASSWORD_PATH}")
        except ValueError as val_e:
            print(f"Email not sent: Issue with credential file content: {val_e}")
        except Exception as e:
            print(f"\nAn unexpected error occurred while preparing or attempting to send the confirmation email: {e}")
            print("Confirmation email was not sent.")


    def add_employee(self):
        print("\n--- Add New Employee ---")
        while True:
            employee_id = input("Enter Employee ID: ").strip()
            id_valid, id_msg = is_valid_employee_id_format(employee_id)
            if not id_valid: print(f"Validation failed: {id_msg}"); continue
            if not self._is_employee_id_unique(employee_id):
                print(f"Validation failed: Employee ID '{employee_id}' already exists."); continue
            break
        while True:
            name = input("Enter Employee Name: ").strip()
            name_valid, name_msg = is_valid_name_format(name)
            if not name_valid: print(f"Validation failed: {name_msg}"); continue
            break
        while True:
            department = input("Enter Department: ").strip()
            dept_valid, dept_msg = is_valid_department_format(department)
            if not dept_valid: print(f"Validation failed: {dept_msg}"); continue
            break
        while True:
            salary_str = input("Enter Salary: ").strip()
            salary_valid, salary_msg = is_valid_salary_format(salary_str)
            if not salary_valid: print(f"Validation failed: {salary_msg}"); continue
            salary = float(salary_str)
            break
        while True:
            email = input("Enter Employee Email: ").strip()
            email_valid, email_msg = is_valid_email_format(email)
            if not email_valid: print(f"Validation failed: {email_msg}"); continue
            break
        while True:
            contact_details = input("Enter Contact Details (e.g., Phone/Address): ").strip()
            contact_valid, contact_msg = is_valid_contact_details_format(contact_details)
            if not contact_valid: print(f"Validation failed: {contact_msg}"); continue
            break

        try:
            new_employee = Employee(employee_id, name, department, salary, email, contact_details)
            self._employees_list.append(new_employee)
            self._save_employees()
            print(f"\nConfirmation: Employee '{name}' (ID: {employee_id}) has been successfully added.")
            # Send confirmation email
            self._send_confirmation_email(employee_id, email, name) # Pass employee_id for body template
        except ValueError as e:
             print(f"Error creating employee record: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during employee addition: {e}")

    def view_employee(self):
        print("\n--- View Employee Details ---")
        if not self._employees_list:
            print("No employee records available to view.")
            return
        employee_id_input = input("Enter Employee ID to view: ").strip()
        id_valid, id_msg = is_valid_employee_id_format(employee_id_input)
        if not id_valid:
            print(f"Invalid input: {id_msg}")
            return
        found_employee = self._find_employee_by_id(employee_id_input)
        if found_employee:
            print("\nEmployee Details:")
            print(f"  Employee ID: {found_employee.employee_id}")
            print(f"  Name: {found_employee.name}")
            print(f"  Department: {found_employee.department}")
            print(f"  Salary: {found_employee.salary:.2f}")
            print(f"  Email: {found_employee.email}")
            print(f"  Contact Details: {found_employee.contact_details}")
        else:
            print(f"Error: Employee not found with ID '{employee_id_input}'.")

    def update_employee(self):
        print("\n--- Update Employee Details ---")
        if not self._employees_list:
            print("No employee records available to update.")
            return
        employee_id_input = input("Enter Employee ID to update: ").strip()
        id_valid, id_msg = is_valid_employee_id_format(employee_id_input)
        if not id_valid:
            print(f"Invalid input: {id_msg}")
            return
        found_employee_index = self._find_employee_index_by_id(employee_id_input)
        if found_employee_index == -1:
            print(f"Error: Employee not found with ID '{employee_id_input}'.")
            return
        employee_to_update = self._employees_list[found_employee_index]
        print("\nCurrent Employee Details:")
        print(f"  ID: {employee_to_update.employee_id}")
        print(f"  Name: {employee_to_update.name}")
        print(f"  Department: {employee_to_update.department}")
        print(f"  Salary: {employee_to_update.salary:.2f}")
        print(f"  Email: {employee_to_update.email}")
        print(f"  Contact Details: {employee_to_update.contact_details}")
        print("\nEnter new details (press Enter to keep current value):")
        updated_name = employee_to_update.name
        updated_department = employee_to_update.department
        updated_salary = employee_to_update.salary
        updated_email = employee_to_update.email
        updated_contact_details = employee_to_update.contact_details
        changes_made = False
        new_name_str = input(f"Enter new Name ({employee_to_update.name}): ").strip()
        if new_name_str:
            name_valid, name_msg = is_valid_name_format(new_name_str)
            if not name_valid: print(f"Update aborted: Invalid Name - {name_msg}"); return
            updated_name = new_name_str
            changes_made = True
        new_department_str = input(f"Enter new Department ({employee_to_update.department}): ").strip()
        if new_department_str:
            dept_valid, dept_msg = is_valid_department_format(new_department_str)
            if not dept_valid: print(f"Update aborted: Invalid Department - {dept_msg}"); return
            updated_department = new_department_str
            changes_made = True
        new_salary_str = input(f"Enter new Salary ({employee_to_update.salary:.2f}): ").strip()
        if new_salary_str:
            salary_valid, salary_msg = is_valid_salary_format(new_salary_str)
            if not salary_valid: print(f"Update aborted: Invalid Salary - {salary_msg}"); return
            updated_salary = float(new_salary_str)
            changes_made = True
        new_email_str = input(f"Enter new Email ({employee_to_update.email}): ").strip()
        if new_email_str:
            email_valid, email_msg = is_valid_email_format(new_email_str)
            if not email_valid: print(f"Update aborted: Invalid Email - {email_msg}"); return
            updated_email = new_email_str
            changes_made = True
        new_contact_str = input(f"Enter new Contact Details ({employee_to_update.contact_details}): ").strip()
        if new_contact_str:
            contact_valid, contact_msg = is_valid_contact_details_format(new_contact_str)
            if not contact_valid: print(f"Update aborted: Invalid Contact Details - {contact_msg}"); return
            updated_contact_details = new_contact_str
            changes_made = True
        if not changes_made:
            print("No changes entered. Update cancelled.")
            return
        print("\nPreview of updated details:")
        print(f"  Name: {updated_name}")
        print(f"  Department: {updated_department}")
        print(f"  Salary: {updated_salary:.2f}")
        print(f"  Email: {updated_email}")
        print(f"  Contact Details: {updated_contact_details}")
        confirmation = input("\nSave these changes? (yes/no): ").lower().strip()
        if confirmation in ['yes', 'y']:
            try:
                employee_to_update.name = updated_name
                employee_to_update.department = updated_department
                employee_to_update.salary = updated_salary
                employee_to_update.email = updated_email
                employee_to_update.contact_details = updated_contact_details
                self._save_employees()
                print("Employee details updated successfully.")
            except Exception as e:
                print(f"An error occurred while saving the update: {e}")
        else:
            print("Update cancelled. No changes were saved.")

    def delete_employee(self):
        print("\n--- Delete Employee Record ---")
        if not self._employees_list:
            print("No employee records available to delete.")
            return
        employee_id_input = input("Enter Employee ID to delete: ").strip()
        id_valid, id_msg = is_valid_employee_id_format(employee_id_input)
        if not id_valid:
            print(f"Invalid input: {id_msg}")
            return
        found_employee_index = self._find_employee_index_by_id(employee_id_input)
        if found_employee_index == -1:
            print(f"Error: Employee not found with ID '{employee_id_input}'.")
            return
        employee_to_delete = self._employees_list[found_employee_index]
        print("\nEmployee Details to Delete:")
        print(f"  Employee ID: {employee_to_delete.employee_id}")
        print(f"  Name: {employee_to_delete.name}")
        print(f"  Department: {employee_to_delete.department}")
        confirmation = input("\nAre you sure you want to permanently delete this employee? (yes/no): ").lower().strip()
        if confirmation in ['yes', 'y']:
            try:
                del self._employees_list[found_employee_index]
                self._save_employees()
                print(f"Employee with ID '{employee_id_input}' has been successfully deleted.")
            except Exception as e:
                 print(f"An error occurred during deletion: {e}")
        else:
            print("Deletion cancelled.")

    def list_all_employees(self):
        print("\n--- List All Employees ---")
        if not self._employees_list:
            print("No employee records found.")
            return
        print(f"{'Employee ID':<15} {'Name':<25} {'Department':<20}")
        print("-" * 60)
        sorted_list = sorted(self._employees_list, key=lambda emp: emp.employee_id)
        for employee in sorted_list:
            print(f"{employee.employee_id:<15} {employee.name:<25} {employee.department:<20}")
        print("-" * 60)
        print(f"Total Employees: {len(self._employees_list)}")

    def generate_department_report(self):
        print("\n--- Employee Report by Department ---")
        if not self._employees_list:
            print("No employee records available to generate reports.")
            return
        departments_data = {}
        for employee in self._employees_list:
            dept_key = employee.department.strip().lower() if employee.department else "uncategorized"
            dept_display_name = employee.department.strip() if employee.department else "Uncategorized"
            if dept_key not in departments_data:
                departments_data[dept_key] = {'display_name': dept_display_name, 'employees': []}
            departments_data[dept_key]['employees'].append(employee)
        if not departments_data:
            print("No departments found among employees.")
            return
        print("\n" + "=" * 75)
        print(" Overall Employee Distribution by Department")
        print("=" * 75)
        sorted_dept_keys = sorted(departments_data.keys(), key=lambda k: departments_data[k]['display_name'])
        total_employees_overall = 0
        for dept_key in sorted_dept_keys:
            dept_info = departments_data[dept_key]
            department_name = dept_info['display_name']
            employees_in_dept = dept_info['employees']
            print(f"\n--- Department: {department_name.upper()} ---")
            print(f"{'Employee ID':<15} {'Name':<25} {'Salary':<15} {'Email':<25}")
            print("-" * 75)
            total_salary_dept = 0
            sorted_dept_list = sorted(employees_in_dept, key=lambda emp: emp.name)
            for employee in sorted_dept_list:
                print(f"{employee.employee_id:<15} {employee.name:<25} {employee.salary:<15.2f} {employee.email:<25}")
                total_salary_dept += employee.salary
            print("-" * 75)
            print(f"Total Employees in {department_name}: {len(employees_in_dept)}")
            print(f"Total Salary for {department_name}: {total_salary_dept:.2f}")
            print("-" * 75)
            total_employees_overall += len(employees_in_dept)
        print("\n" + "=" * 75)
        print(f"Report Complete. Found {len(departments_data)} departments.")
        print(f"Total Employees Across All Departments: {total_employees_overall}")
        print("=" * 75)

    def run(self):
        print("\nWelcome to the BitFutura Employee Management System")
        while True:
            print("\n--- Main Menu ---")
            print("1. Add Employee")
            print("2. View Employee")
            print("3. Update Employee")
            print("4. Delete Employee")
            print("5. List All Employees")
            print("6. Department Wise Report")
            print("7. Exit")
            choice = input("Enter your choice (1-7): ").strip()
            try:
                if choice == '1':
                    self.add_employee()
                elif choice == '2':
                    self.view_employee()
                elif choice == '3':
                    self.update_employee()
                elif choice == '4':
                    self.delete_employee()
                elif choice == '5':
                    self.list_all_employees()
                elif choice == '6':
                    self.generate_department_report()
                elif choice == '7':
                    print("Exiting Employee Management System. Saving data...")
                    self._save_employees()
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 7.")
            except KeyboardInterrupt:
                 print("\nOperation cancelled by user. Returning to main menu.")
            except EOFError:
                print("\nExiting due to unexpected end of input. Saving data...")
                self._save_employees()
                print("Goodbye!")
                break
            except Exception as e:
                print(f"\nAn unexpected error occurred: {e}")
                print("Please try again or contact support if the issue persists.")

if __name__ == "__main__":
    ems_app = EmployeeManagementSystem()
    ems_app.run()