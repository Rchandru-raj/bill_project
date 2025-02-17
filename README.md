# bill_project
Billing details
Clone the code
Create the virtual environment python -m venv envname
pip install -r requirements.txt
Then Run the code python manage.py runserver
if any products need to add 

POST http://127.0.0.1:8000/api/products/ 
{
    "name": "Keyboard",
    "available_stock": 100,
    "price": 29.99,
    "tax_percentage": 5.00
}
Product Id is auto generated ex prod01,prod02
Billing page http://127.0.0.1:8000/api/billing/

