from django.shortcuts import render
from rest_framework import viewsets, status

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Invoice, InvoiceItem, Customer
from .serializers import InvoiceSerializer,ProductSerializer

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .models import Customer, Invoice, InvoiceItem, Product
import json

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Customer, Invoice, InvoiceItem, Product

@api_view(['POST'])
def generate_invoice(request):
    try:
        print("Request Data:", request.data)  # Log the request data for debugging

        data = request.data
        customer_email = data.get("customer_email")
        items = data.get("items", [])
        paid_amount = float(data.get("paid_amount", 0) or 0)  # Ensuring it's a valid float

        if not customer_email or not items:
            return Response({"error": "Invalid input: Missing required fields."}, status=400)

        # Get or create customer
        customer, _ = Customer.objects.get_or_create(email=customer_email)

        total_without_tax = total_tax = net_price = 0
        invoice = Invoice.objects.create(customer=customer, paid_amount=paid_amount)

        processed_items = []  # List to store item details for rendering

        for item in items:
            product = Product.objects.filter(product_id=item["product_id"]).first()
            if not product:
                return Response({"error": f"Product ID {item['product_id']} not found"}, status=400)

            quantity = int(item["quantity"])
            purchase_price = product.price * quantity
            tax_amount = (purchase_price * product.tax_percentage) / 100
            total_price = purchase_price + tax_amount

            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=quantity,
                purchase_price=purchase_price,
                tax_percentage=product.tax_percentage,
                tax_amount=tax_amount,
                total_price=total_price
            )

            processed_items.append({
                "product_id": product.product_id,
                "unit_price": product.price,
                "quantity": quantity,
                "purchase_price": purchase_price,
                "tax_percent": product.tax_percentage,
                "tax_payable": tax_amount,
                "total_price": total_price
            })

            total_without_tax += purchase_price
            total_tax += tax_amount
            net_price += total_price

        rounded_net_price = round(net_price)
        balance_payable = paid_amount - rounded_net_price

        # Update invoice details
        invoice.total_without_tax = total_without_tax
        invoice.total_tax = total_tax
        invoice.net_price = net_price
        invoice.rounded_net_price = rounded_net_price
        invoice.balance_payable = balance_payable
        invoice.save()

        # Prepare balance denomination (Optional)
        denominations = {100: 0, 50: 1, 20: 2, 10: 1, 5: 1, 1: 1}  # Example denomination breakdown

        # Render invoice HTML
        html_content = render_to_string("invoice_email.html", {
            "customer_email": customer_email,
            "items": processed_items,
            "total_without_tax": total_without_tax,
            "total_tax": total_tax,
            "net_price": net_price,
            "rounded_net_price": rounded_net_price,
            "balance_payable": balance_payable,
            "denominations": denominations,
        })

        # Send the email with the invoice HTML
        send_invoice_email(customer_email, html_content)

        # return Response({
        #     "message": "Invoice generated successfully",
        #     "invoice_html": html_content  # Return HTML directly
        # }, status=201)
        return Response({
        "message": "Invoice generated successfully",
        "invoice_id": invoice.id,
        "net_price": net_price
    }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("Error generating invoice:", str(e))  # Log the error for debugging
        return Response({"error": str(e)}, status=500)


def send_invoice_email(customer_email, html_content):
    try:
        subject = "Your Invoice from Ruphinz"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [customer_email]

        plain_message = strip_tags(html_content)  # Convert HTML to plain text

        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            html_message=html_content,  # Send as HTML
        )
        print(f"Invoice email sent to {customer_email}")
    except Exception as e:
        print(f"Error sending email: {e}")  # Log email error

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def billing_page(request):
    return render(request, 'billing.html')
