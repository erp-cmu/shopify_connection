import json

import frappe
from frappe.utils import get_site_path, getdate, now


@frappe.whitelist()
def receive_post_data():
    # To get raw POST data as JSON
    data = json.loads(frappe.request.data)
    createSalesOrder()
    # Process data as needed
    return {"status": "success", "received": data}


def createSalesOrder():
    # Create sale order

    customer_name = getOrCreateCustomer(customer_name="Shopify Customer")

    paramsSalesOrder = dict(
        doctype="Sales Order",
        customer=customer_name,
        delivery_date=getdate("2025-05-03", parse_day_first=False),
    )
    salesOrder = frappe.get_doc(paramsSalesOrder)

    # Add items
    item_name, uom = getOrCreateItem("ITEM001", "ITEM001")
    paramsItem = dict(
        doctype="Sales Order Item",
        item_name=item_name,
        item_code=item_name,
        uom=uom,
        qty=2,
        rate=200,
        amount=400,
        warehouse="Stores - DF",
    )
    salesOrderItem = frappe.get_doc(paramsItem)
    salesOrder.append("items", salesOrderItem)
    salesOrder.save()
    pass


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


def getOrCreateItem(
    item_code,
    item_name,
    item_group="Products",
    stock_uom="Nos",
    opening_stock=0,
    valuation_rate=0.01,  # NOTE: I put non-zero number here so that the software can calculate valuation and does not complain when performing stock entry.
    allow_negative_stock=False,
    is_stock_item=True,
    also_search_item_name=False,
):
    item_name_pk = frappe.db.exists("Item", {"item_code": item_code})
    if item_name_pk:
        return item_name_pk, getUOM(item_name_pk)

    # NOTE: Since item name is not guarantee unique, I might ended getting the wrong or duplicated items which
    # can be problematic when importing sales invoice. Threrefore, this search will only be activated on demand.
    if also_search_item_name:
        item_name_pk = frappe.db.exists("Item", {"item_name": item_name})
        if item_name_pk:
            return item_name_pk, getUOM(item_name_pk)

    uom_name_pk = getOrCreateUOM(uom_name=stock_uom, must_be_whole_number=False)

    doc = frappe.get_doc(
        {
            "doctype": "Item",
            "item_code": item_code,
            "item_name": item_name,
            "item_group": item_group,
            "stock_uom": uom_name_pk,
            "opening_stock": opening_stock,
            "valuation_rate": valuation_rate,
            "allow_negative_stock": allow_negative_stock,
            "is_stock_item": is_stock_item,
        },
    )
    doc.insert()
    return doc.name, stock_uom


def getOrCreateUOM(uom_name, must_be_whole_number=False):
    if frappe.db.exists("UOM", uom_name):
        return uom_name

    doc = frappe.get_doc(
        {
            "doctype": "UOM",
            "uom_name": uom_name,
            "must_be_whole_number": must_be_whole_number,
        }
    )
    doc.insert()
    return doc.name


def getOrCreateItemGroup(item_group_name, parent_item_group="All Item Groups", is_group=False):
    item_group_name_pk = frappe.db.exists("Item Group", item_group_name)
    if item_group_name_pk:
        return item_group_name_pk

    doc = frappe.get_doc(
        {
            "doctype": "Item Group",
            "item_group_name": item_group_name,
            "parent_item_group": parent_item_group,
            "is_group": is_group,
        }
    )
    doc.insert()
    return doc.name


def getUOM(item_name):
    stock_uom = frappe.db.get_value("Item", item_name, "stock_uom")
    return stock_uom
