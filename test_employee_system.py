import unittest
import os
import csv
import smtplib  # Ensure smtplib is imported for exception handling
from unittest.mock import patch, mock_open, MagicMock, call

# Import the classes and functions from your script
try:
    from employee_management import (
        is_valid_employee_id_format, is_valid_name_format, is_valid_department_format,
        is_valid_salary_format, is_valid_email_format, is_valid_contact_details_format,
        Employee, EmployeeManagementSystem, EmailSender, # Added EmailSender
        FILE_NAME, DELIMITER, EMPLOYEE_KEYS,
        SENDER_EMAIL_PATH, SENDER_APP_PASSWORD_PATH, # Import new constants
        DEFAULT_CONFIRMATION_SUBJECT, DEFAULT_CONFIRMATION_BODY_TEMPLATE
    )
except ImportError:
    print("Error: Make sure your original script is saved as 'employee_management.py' "
          "in the same directory, or adjust the import statement.")
    exit()

# --- Test Data ---
VALID_EMP_DATA_1 = {
    "Employee ID": "BF001", "Name": "Alice Smith", "Department": "Engineering",
    "Salary": "75000.50", "Email": "alice.s@bitfutura.test", "Contact Details": "123-456-7890"
}
VALID_EMP_DATA_2 = {
    "Employee ID": "BF002", "Name": "Bob Johnson", "Department": "Marketing",
    "Salary": "60000", "Email": "bob.j@bitfutura.test", "Contact Details": "987-654-3210"
}
VALID_EMP_DATA_3 = {
    "Employee ID": "BF003", "Name": "Charlie Lee", "Department": "Engineering",
    "Salary": "80000.00", "Email": "charlie.l@bitfutura.test", "Contact Details": "555-111-2222"
}

# --- Test Classes ---

class TestValidationFunctions(unittest.TestCase):
    """Tests for the standalone validation functions."""

    def test_is_valid_employee_id_format(self):
        self.assertTrue(is_valid_employee_id_format("BF001")[0])
        self.assertFalse(is_valid_employee_id_format("")[0])
        self.assertEqual(is_valid_employee_id_format("BF 001")[1], "Employee ID must be alphanumeric (letters and numbers only).")

    def test_is_valid_name_format(self):
        self.assertTrue(is_valid_name_format("Alice Smith")[0])
        self.assertFalse(is_valid_name_format("Alice123")[0])
        self.assertEqual(is_valid_name_format("Alice123")[1], "Name must contain only alphabetic characters and spaces.")

    def test_is_valid_department_format(self):
        self.assertTrue(is_valid_department_format("Engineering")[0])
        self.assertFalse(is_valid_department_format("Eng@Dept")[0])
        self.assertEqual(is_valid_department_format("Eng@Dept")[1], "Department can only contain letters, numbers, spaces, and hyphens.")

    def test_is_valid_salary_format(self):
        self.assertTrue(is_valid_salary_format("50000")[0])
        self.assertFalse(is_valid_salary_format("-100")[0])
        self.assertEqual(is_valid_salary_format("abc")[1], "Salary must be a valid number (e.g., 50000 or 65000.50).")

    def test_is_valid_email_format(self):
        self.assertTrue(is_valid_email_format("test@example.com")[0])
        self.assertFalse(is_valid_email_format("test @example.com")[0])
        expected_invalid_msg = "Invalid email format (must contain '@' and '.', no spaces allowed)."
        self.assertEqual(is_valid_email_format("test @example.com")[1], expected_invalid_msg)

    def test_is_valid_contact_details_format(self):
        self.assertTrue(is_valid_contact_details_format("123-456-7890")[0])
        self.assertFalse(is_valid_contact_details_format("")[0])
        self.assertEqual(is_valid_contact_details_format("")[1], "Contact Details cannot be empty.")


class TestEmployeeClass(unittest.TestCase):
    """Tests for the Employee class."""

    def test_employee_init_valid(self):
        emp = Employee(
            employee_id=VALID_EMP_DATA_1["Employee ID"], name=VALID_EMP_DATA_1["Name"],
            department=VALID_EMP_DATA_1["Department"], salary=VALID_EMP_DATA_1["Salary"],
            email=VALID_EMP_DATA_1["Email"], contact_details=VALID_EMP_DATA_1["Contact Details"]
        )
        self.assertEqual(emp.employee_id, VALID_EMP_DATA_1["Employee ID"])
        self.assertEqual(emp.salary, float(VALID_EMP_DATA_1["Salary"]))

    def test_employee_init_invalid_id(self):
        with self.assertRaisesRegex(ValueError, "Employee ID cannot be empty"):
            Employee("", "Test", "Test", "50000", "t@t.com", "Test")

    def test_employee_to_dict(self):
        # FIX: Initialize Employee by explicitly mapping dictionary keys to __init__ parameters
        emp = Employee(
            employee_id=VALID_EMP_DATA_1["Employee ID"],
            name=VALID_EMP_DATA_1["Name"],
            department=VALID_EMP_DATA_1["Department"],
            salary=VALID_EMP_DATA_1["Salary"],
            email=VALID_EMP_DATA_1["Email"],
            contact_details=VALID_EMP_DATA_1["Contact Details"]
        )
        self.assertEqual(emp.to_dict(), VALID_EMP_DATA_1)

    def test_employee_from_dict_valid(self):
        emp = Employee.from_dict(VALID_EMP_DATA_1)
        self.assertIsInstance(emp, Employee)
        self.assertEqual(emp.employee_id, VALID_EMP_DATA_1["Employee ID"])

    def test_employee_from_dict_invalid_salary_format(self):
        invalid_data = VALID_EMP_DATA_1.copy()
        invalid_data["Salary"] = "not-a-number"
        with patch('builtins.print') as mock_print:
            emp = Employee.from_dict(invalid_data)
            self.assertIsNone(emp)
            mock_print.assert_any_call(f"Error creating employee: Invalid salary format 'not-a-number'. Data: {invalid_data}")

    def test_employee_from_dict_validation_error_in_init(self):
        invalid_data = VALID_EMP_DATA_1.copy()
        invalid_data["Department"] = "" # This will cause ValueError in Employee.__init__
        with patch('builtins.print'): # Suppress print from from_dict
            with self.assertRaisesRegex(ValueError, "Department cannot be empty"):
                Employee.from_dict(invalid_data)

    def test_employee_str(self):
        # FIX: Initialize Employee by explicitly mapping dictionary keys to __init__ parameters
        emp = Employee(
            employee_id=VALID_EMP_DATA_1["Employee ID"],
            name=VALID_EMP_DATA_1["Name"],
            department=VALID_EMP_DATA_1["Department"],
            salary=VALID_EMP_DATA_1["Salary"],
            email=VALID_EMP_DATA_1["Email"],
            contact_details=VALID_EMP_DATA_1["Contact Details"]
        )
        expected_str = (f"ID: {VALID_EMP_DATA_1['Employee ID']}, Name: {VALID_EMP_DATA_1['Name']}, "
                        f"Dept: {VALID_EMP_DATA_1['Department']}, Salary: {float(VALID_EMP_DATA_1['Salary']):.2f}, "
                        f"Email: {VALID_EMP_DATA_1['Email']}, Contact: {VALID_EMP_DATA_1['Contact Details']}")
        self.assertEqual(str(emp), expected_str)


MOCK_CSV_HEADER = DELIMITER.join(EMPLOYEE_KEYS)
MOCK_CSV_DATA_VALID = (
    MOCK_CSV_HEADER + "\n" +
    DELIMITER.join(VALID_EMP_DATA_1.values()) + "\n" +
    DELIMITER.join(VALID_EMP_DATA_2.values()) + "\n"
)
MOCK_CSV_DATA_MALFORMED = (
    MOCK_CSV_HEADER + "\n" +
    "BF001,Alice Smith,Engineering,75000.50,alice.s@bitfutura.test\n"
    "BF002,Bob Johnson,Marketing,60000,bob.j@bitfutura.test,987-654-3210\n"
)
MOCK_CSV_DATA_INVALID_SALARY_IN_FILE = ( # Renamed for clarity
    MOCK_CSV_HEADER + "\n" +
    "BF001,Alice Smith,Engineering,INVALID_SAL,alice.s@bitfutura.test,123-456-7890\n"
    "BF002,Bob Johnson,Marketing,60000,bob.j@bitfutura.test,987-654-3210\n"
)
MOCK_CSV_DATA_DUPLICATE_ID = (
    MOCK_CSV_HEADER + "\n" +
    DELIMITER.join(VALID_EMP_DATA_1.values()) + "\n" +
    DELIMITER.join(VALID_EMP_DATA_1.values()) + "\n"
)

TEST_FILE_NAME = "test_" + FILE_NAME

class TestEmployeeManagementSystem(unittest.TestCase):
    """Tests for the EmployeeManagementSystem class."""

    def setUp(self):
        if os.path.exists(TEST_FILE_NAME):
            os.remove(TEST_FILE_NAME)
        self.ems = EmployeeManagementSystem(file_name=TEST_FILE_NAME)

    def tearDown(self):
        if os.path.exists(TEST_FILE_NAME):
            os.remove(TEST_FILE_NAME)

    @patch('employee_management.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=MOCK_CSV_DATA_VALID)
    @patch('builtins.print')
    def test_load_employees_success(self, mock_print, mock_file, mock_exists):
        mock_exists.return_value = True
        ems_loaded = EmployeeManagementSystem(file_name=TEST_FILE_NAME)
        self.assertEqual(len(ems_loaded._employees_list), 2)
        self.assertEqual(ems_loaded._employees_list[0].employee_id, VALID_EMP_DATA_1["Employee ID"])

    @patch('employee_management.os.path.exists')
    @patch('builtins.print')
    def test_load_employees_file_not_found(self, mock_print, mock_exists):
        mock_exists.return_value = False
        ems_loaded = EmployeeManagementSystem(file_name=TEST_FILE_NAME)
        self.assertEqual(len(ems_loaded._employees_list), 0)
        mock_print.assert_any_call(f"No data file found ({TEST_FILE_NAME}). Starting with an empty list.")

    @patch('employee_management.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=MOCK_CSV_DATA_MALFORMED)
    @patch('builtins.print')
    def test_load_employees_malformed_line(self, mock_print, mock_file, mock_exists):
        mock_exists.return_value = True
        ems_loaded = EmployeeManagementSystem(file_name=TEST_FILE_NAME)
        self.assertEqual(len(ems_loaded._employees_list), 1)
        malformed_line_content = "BF001,Alice Smith,Engineering,75000.50,alice.s@bitfutura.test"
        mock_print.assert_any_call(f"Skipping malformed line 2 in {TEST_FILE_NAME} (expected {len(EMPLOYEE_KEYS)} values, got {len(EMPLOYEE_KEYS)-1}): {malformed_line_content}")

    @patch('employee_management.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=MOCK_CSV_DATA_INVALID_SALARY_IN_FILE)
    @patch('builtins.print')
    def test_load_employees_invalid_data_in_file(self, mock_print, mock_file, mock_exists):
        mock_exists.return_value = True
        ems_loaded = EmployeeManagementSystem(file_name=TEST_FILE_NAME)
        self.assertEqual(len(ems_loaded._employees_list), 1) # Only BF002 should load
        self.assertEqual(ems_loaded._employees_list[0].employee_id, "BF002")
        # Check for the print message from Employee.from_dict when salary conversion fails
        invalid_line_content = "BF001,Alice Smith,Engineering,INVALID_SAL,alice.s@bitfutura.test,123-456-7890"
        invalid_data_dict = dict(zip(EMPLOYEE_KEYS, invalid_line_content.split(DELIMITER)))
        mock_print.assert_any_call(f"Error creating employee: Invalid salary format 'INVALID_SAL'. Data: {invalid_data_dict}")
        # Check for the print message from _load_employees when from_dict returns None
        mock_print.assert_any_call(f"Skipping invalid data on line 2 in {TEST_FILE_NAME} (Employee.from_dict returned None): {invalid_line_content}")


    @patch('employee_management.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=MOCK_CSV_DATA_DUPLICATE_ID)
    @patch('builtins.print')
    def test_load_employees_duplicate_id_in_file(self, mock_print, mock_file, mock_exists):
        mock_exists.return_value = True
        ems_loaded = EmployeeManagementSystem(file_name=TEST_FILE_NAME)
        self.assertEqual(len(ems_loaded._employees_list), 1)
        mock_print.assert_any_call("Warning: Duplicate Employee ID 'BF001' found in file on line 3. Skipping duplicate.")

    @patch('builtins.open', new_callable=mock_open)
    def test_save_employees(self, mock_file):
        emp1 = Employee.from_dict(VALID_EMP_DATA_1)
        self.ems._employees_list = [emp1]
        self.ems._save_employees()
        mock_file.assert_called_once_with(TEST_FILE_NAME, 'w', encoding='utf-8', newline='')
        handle = mock_file()
        expected_header = DELIMITER.join(EMPLOYEE_KEYS) + '\n'
        expected_line1 = DELIMITER.join(VALID_EMP_DATA_1.values()) + '\n'
        handle.write.assert_any_call(expected_header)
        handle.write.assert_any_call(expected_line1)

    def test_find_employee_by_id(self):
        emp1 = Employee.from_dict(VALID_EMP_DATA_1)
        self.ems._employees_list = [emp1]
        self.assertIs(self.ems._find_employee_by_id("BF001"), emp1)
        self.assertIsNone(self.ems._find_employee_by_id("BF999"))

    # --- Test _send_confirmation_email (New approach with EmailSender) ---

    @patch('employee_management.os.path.exists')
    @patch('employee_management.open', new_callable=mock_open)
    @patch('employee_management.EmailSender')
    @patch('builtins.print')
    def test_send_email_success(self, mock_print, MockEmailSenderCls, mock_file_open, mock_os_exists):
        mock_os_exists.return_value = True # Assume credential files exist
        # Configure mock_open to return different data for email and password files
        mock_file_open.side_effect = [
            mock_open(read_data="sender@example.com").return_value,
            mock_open(read_data="app_password123").return_value
        ]
        mock_email_sender_instance = MockEmailSenderCls.return_value # Get the mocked instance

        test_emp_id = "E001"
        test_email = "recipient@example.com"
        test_name = "Test Recipient"
        self.ems._send_confirmation_email(test_emp_id, test_email, test_name)

        # Check os.path.exists calls
        mock_os_exists.assert_any_call(SENDER_EMAIL_PATH)
        mock_os_exists.assert_any_call(SENDER_APP_PASSWORD_PATH)

        # Check file open calls
        mock_file_open.assert_any_call(SENDER_EMAIL_PATH, 'r')
        mock_file_open.assert_any_call(SENDER_APP_PASSWORD_PATH, 'r')

        # Check EmailSender instantiation
        MockEmailSenderCls.assert_called_once_with("sender@example.com", "app_password123")

        # Check EmailSender.send_email call
        expected_subject = DEFAULT_CONFIRMATION_SUBJECT
        expected_body = DEFAULT_CONFIRMATION_BODY_TEMPLATE.format(employee_name=test_name, employee_id=test_emp_id)
        mock_email_sender_instance.send_email.assert_called_once_with(
            recipient_name=test_name,
            recipient_email=test_email,
            subject=expected_subject,
            body=expected_body
        )
        mock_print.assert_any_call("Sender credentials successfully read.")
        # Note: Actual "Email successfully sent" print comes from EmailSender, which is mocked.

    @patch('employee_management.os.path.exists')
    @patch('builtins.print')
    def test_send_email_credential_file_not_found(self, mock_print, mock_os_exists):
        mock_os_exists.side_effect = lambda path: False if path == SENDER_EMAIL_PATH else True # Email file missing
        
        self.ems._send_confirmation_email("E001", "test@example.com", "Test User")
        
        mock_os_exists.assert_any_call(SENDER_EMAIL_PATH)
        mock_print.assert_any_call(f"Error: Sender email file not found at {SENDER_EMAIL_PATH}.")
        mock_print.assert_any_call(f"Email not sent: Prerequisite file missing: {SENDER_EMAIL_PATH}")


    @patch('employee_management.os.path.exists')
    @patch('employee_management.open', new_callable=mock_open)
    @patch('employee_management.EmailSender')
    @patch('builtins.print')
    def test_send_email_smtp_auth_error_via_emailsender(self, mock_print, MockEmailSenderCls, mock_file_open, mock_os_exists):
        mock_os_exists.return_value = True
        mock_file_open.side_effect = [
            mock_open(read_data="sender@example.com").return_value,
            mock_open(read_data="wrong_password").return_value
        ]
        mock_email_sender_instance = MockEmailSenderCls.return_value
        # Simulate an SMTPAuthenticationError from the EmailSender's send_email method
        mock_email_sender_instance.send_email.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication credentials invalid")

        self.ems._send_confirmation_email("E001", "test@example.com", "Test User")

        MockEmailSenderCls.assert_called_once_with("sender@example.com", "wrong_password")
        mock_email_sender_instance.send_email.assert_called_once()
        # This specific error message is now part of EmailSender, which is mocked.
        # The _send_confirmation_email method will catch the exception and print its own generic message.
        mock_print.assert_any_call("\nAn unexpected error occurred while preparing or attempting to send the confirmation email: (535, b'Authentication credentials invalid')")


    # --- Test Main EMS Operations ---

    @patch('builtins.input')
    @patch('builtins.print')
    @patch.object(EmployeeManagementSystem, '_save_employees')
    @patch.object(EmployeeManagementSystem, '_send_confirmation_email') # Mock the wrapper
    def test_add_employee_success(self, mock_send_email_method, mock_save, mock_print, mock_input):
        emp_id = "BF101"
        emp_name = "New Employee"
        emp_email = "new@bitfutura.test"
        mock_input.side_effect = [
            emp_id, emp_name, "Testing", "55000", emp_email, "Contact Info"
        ]
        self.ems.add_employee()

        self.assertEqual(len(self.ems._employees_list), 1)
        self.assertEqual(self.ems._employees_list[0].employee_id, emp_id)
        mock_save.assert_called_once()
        mock_send_email_method.assert_called_once_with(emp_id, emp_email, emp_name)
        mock_print.assert_any_call(f"\nConfirmation: Employee '{emp_name}' (ID: {emp_id}) has been successfully added.")

    @patch('builtins.input', return_value="BF001")
    @patch('builtins.print')
    def test_view_employee_found(self, mock_print, mock_input):
        emp1 = Employee.from_dict(VALID_EMP_DATA_1)
        self.ems._employees_list = [emp1]
        self.ems.view_employee()
        mock_print.assert_any_call(f"  Employee ID: {emp1.employee_id}")

    @patch('builtins.input')
    @patch('builtins.print')
    @patch.object(EmployeeManagementSystem, '_save_employees')
    def test_update_employee_success(self, mock_save, mock_print, mock_input):
        emp1 = Employee.from_dict(VALID_EMP_DATA_1)
        self.ems._employees_list = [emp1]
        mock_input.side_effect = [
            "BF001", "Alice Smith Jr", "", "80000", "", "New Contact", "yes"
        ]
        self.ems.update_employee()
        self.assertEqual(self.ems._employees_list[0].name, "Alice Smith Jr")
        mock_save.assert_called_once()

    @patch('builtins.input')
    @patch('builtins.print')
    @patch.object(EmployeeManagementSystem, '_save_employees')
    def test_delete_employee_success(self, mock_save, mock_print, mock_input):
        emp1 = Employee.from_dict(VALID_EMP_DATA_1)
        self.ems._employees_list = [emp1]
        mock_input.side_effect = ["BF001", "yes"]
        self.ems.delete_employee()
        self.assertEqual(len(self.ems._employees_list), 0)
        mock_save.assert_called_once()

    @patch('builtins.print')
    def test_list_all_employees_success(self, mock_print):
        emp1 = Employee.from_dict(VALID_EMP_DATA_1)
        self.ems._employees_list = [emp1]
        self.ems.list_all_employees()
        mock_print.assert_any_call(f"{emp1.employee_id:<15} {emp1.name:<25} {emp1.department:<20}")

    @patch('builtins.print')
    def test_generate_department_report_success(self, mock_print):
        emp1 = Employee.from_dict(VALID_EMP_DATA_1) # Engineering
        self.ems._employees_list = [emp1]
        self.ems.generate_department_report()
        mock_print.assert_any_call("\n--- Department: ENGINEERING ---")
        mock_print.assert_any_call(f"Total Employees in Engineering: 1")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)