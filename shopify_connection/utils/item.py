import frappe


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
    PREFIX_CODE = "TEMP"
    PREFIX_NAME = "(TEMP)"
    item_name_prefix = f"{PREFIX_NAME} {item_name}"
    item_code_prefix = f"{PREFIX_CODE}__{item_code}"

    item_name_pk = frappe.db.exists("Item", {"item_code": item_code})
    if item_name_pk:
        return item_name_pk, getUOM(item_name_pk)

    # Search for item with prefix
    item_name_pk = frappe.db.exists("Item", {"item_code": item_code_prefix})
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
            "item_code": item_code_prefix,
            "item_name": item_name_prefix,
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
