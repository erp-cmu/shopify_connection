import frappe


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
