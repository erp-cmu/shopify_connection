import frappe
import json


@frappe.whitelist()
def receive_post_data():
    # To get raw POST data as JSON
    data = json.loads(frappe.request.data)

    customer_name = getOrCreateCustomer(customer_name="Shopify Customer")

    # Process data as needed
    return {"status": "success", "received": data, "customer": customer_name}


def getOrCreateCustomer(customer_name, customer_type="Individual"):
    customer_name_pk = frappe.db.exists("Customer", {"name": customer_name})
    if customer_name_pk:
        return customer_name_pk

    dataDict = {
        "doctype": "Customer",
        "customer_name": customer_name,
        "customer_type": customer_type,
    }

    doc = frappe.get_doc(dataDict)
    doc.insert()

    return doc.name
