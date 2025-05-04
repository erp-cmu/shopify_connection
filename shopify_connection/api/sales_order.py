import json

import frappe
from frappe.utils import getdate, add_to_date

from shopify_connection.utils.customer import getOrCreateCustomer
from shopify_connection.utils.item import getOrCreateItem


@frappe.whitelist()
def webhook_sales_order():
    # To get raw POST data as JSON
    data = json.loads(frappe.request.data)
    createSalesOrder(data)
    # Process data as needed
    return {"status": "success"}


def createSalesOrder(_data):
    # Conver to frappe dict so that I can use dot notatio.
    data = frappe._dict(_data)

    order_number = data.id

    # Check if sales order is already created
    siName = frappe.db.get_all("Sales Order", filters=dict(custom_external_id=order_number))
    if len(siName) > 0:
        frappe.msgprint(f"Skip importing order: {order_number}. Order already exists")
        return

    # Create sale order
    customer_name = getOrCreateCustomer(customer_name="Shopify Customer")

    transaction_date = getdate(data.created_at, parse_day_first=False)
    delivery_date = add_to_date(transaction_date, days=1)
    paramsSalesOrder = dict(
        doctype="Sales Order",
        custom_external_id=order_number,
        customer=customer_name,
        transaction_date=transaction_date,
        delivery_date=delivery_date,
    )
    salesOrder = frappe.get_doc(paramsSalesOrder)

    # Add items
    for _it in data.line_items:
        it = frappe._dict(_it)
        item_name, uom = getOrCreateItem(it.id, it.name)
        paramsItem = dict(
            doctype="Sales Order Item",
            item_name=item_name,
            item_code=item_name,
            uom=uom,
            qty=it.quantity,
            rate=it.price,
            amount=it.quantity * it.price,
            warehouse="Stores - DF",
        )
        salesOrderItem = frappe.get_doc(paramsItem)
        salesOrder.append("items", salesOrderItem)

    salesOrder.save()
    pass
