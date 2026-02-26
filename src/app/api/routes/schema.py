# app/api/routes/schema.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.user import User
from app.models.table import Table

router = APIRouter(prefix="/schema", tags=["schema"])

DIETARY_OPTIONS = [
    "dairy_free", "egg_free", "fish_allergy", "gluten_free",
    "halal", "kosher", "nut_allergy", "peanut_allergy",
    "sesame_allergy", "shellfish_allergy", "soy_free", "vegan", "vegetarian"
]

SCHEMA = {
    "reservation": {
        "endpoint": "/api/reservations",
        "bootstrap": "/api/reservations/{id}/bootstrap",
        "fields": {
            "date":       { "type": "date",   "required": True,  "label": "Date" },
            "start_time": { "type": "time",   "required": True,  "label": "Start Time" },
            "end_time":   { "type": "time",   "required": False, "label": "End Time" },
            "status":     { "type": "enum",   "required": False, "label": "Status",
                            "options": ["draft", "confirmed", "cancelled"],
                            "default": "draft" },
            "notes":      { "type": "textarea","required": False, "label": "Notes",
                            "maxLength": 500 },
        },
        "children": ["attendee"],
    },

    "attendee": {
        "endpoint": "/api/reservation-attendees",
        "fields": {
            "member_id":   { "type": "member_select", "required": False, "label": "Member" },
            "guest_name":  { "type": "text",   "required": False, "label": "Guest Name",
                             "maxLength": 120,
                             "note": "Required if no member selected" },
            "dietary_restrictions": {
                "type": "multiselect", "required": False,
                "label": "Dietary Restrictions",
                "options": DIETARY_OPTIONS
            },
            "selection_confirmed": { "type": "boolean", "required": False,
                                     "label": "Selection Confirmed", "default": False },
        },
        "validation": "member_id OR guest_name required",
        "children": ["order"],
    },

    "order": {
        "endpoint": "/api/orders",
        "ensure_endpoint": "/api/orders/ensure",
        "fire_endpoint": "/api/orders/{id}/fire",
        "chit_endpoint": "/api/orders/{id}/chit",
        "fields": {
            "status": { "type": "enum", "required": False, "label": "Status",
                        "options": ["open", "fired", "fulfilled"], "default": "open" },
            "notes":  { "type": "textarea", "required": False, "label": "Notes",
                        "maxLength": 500 },
        },
        "children": ["order_item"],
        "lifecycle": {
            "open":      { "editable": True,  "can_fire": True  },
            "fired":     { "editable": False, "can_fire": False },
            "fulfilled": { "editable": False, "can_fire": False },
        }
    },

    "order_item": {
        "endpoint": "/api/order-items",
        "list_endpoint": "/api/order-items/by-order/{order_id}",
        "create_endpoint": "/api/order-items/by-order/{order_id}",
        "fields": {
            "menu_item_id": { "type": "menu_select", "required": True,  "label": "Menu Item" },
            "quantity":     { "type": "number",      "required": False, "label": "Quantity",
                              "min": 1, "default": 1 },
            "status":       { "type": "enum",        "required": False, "label": "Status",
                              "options": ["selected", "confirmed", "served", "canceled"],
                              "default": "selected" },
        },
        "display": {
            "use_snapshot_name":  True,
            "use_snapshot_price": True,
            "fallback_to_live":   True,
        }
    },

    "member": {
        "endpoint": "/api/members",
        "fields": {
            "name":     { "type": "text",        "required": True,  "label": "Name",
                          "maxLength": 120 },
            "relation": { "type": "text",        "required": False, "label": "Relation",
                          "maxLength": 50,
                          "placeholder": "e.g. spouse, colleague, guest" },
            "dietary_restrictions": {
                "type": "multiselect", "required": False,
                "label": "Dietary Restrictions",
                "options": DIETARY_OPTIONS
            },
        },
    },

    "menu_item": {
        "endpoint": "/api/menu-items",
        "fields": {
            "name":        { "type": "text",     "required": True,  "label": "Name",
                             "maxLength": 140 },
            "description": { "type": "textarea", "required": False, "label": "Description",
                             "maxLength": 500 },
            "price_cents": { "type": "price",    "required": True,  "label": "Price",
                             "min": 0,
                             "note": "Stored as cents. UI shows dollars." },
            "dietary_restrictions": {
                "type": "multiselect", "required": False,
                "label": "Dietary Accommodations",
                "options": DIETARY_OPTIONS,
                "note": "What this item accommodates"
            },
            "is_active":   { "type": "boolean",  "required": False, "label": "Active",
                             "default": True },
        },
        "admin_only": True,
    },

    "dining_room": {
        "endpoint": "/api/dining-rooms",
        "fields": {
            "name":        { "type": "text",     "required": True,  "label": "Name",
                             "maxLength": 120 },
            "description": { "type": "textarea", "required": False, "label": "Description",
                             "maxLength": 255 },
            "is_active":   { "type": "boolean",  "required": False, "label": "Active",
                             "default": True },
        },
        "admin_only": True,
    },

    "table": {
        "endpoint": "/api/tables",
        "fields": {
            "name":           { "type": "text",    "required": True, "label": "Name",
                                "maxLength": 80 },
            "dining_room_id": { "type": "relation","required": True, "label": "Dining Room",
                                "relation_entity": "dining_room" },
            "seat_count":     { "type": "number",  "required": True, "label": "Seat Count",
                                "min": 1 },
            "is_active":      { "type": "boolean", "required": False,"label": "Active",
                                "default": True },
        },
        "admin_only": True,
    },

    "seat_assignment": {
        "endpoint": "/api/seat-assignments",
        "fields": {
            "reservation_id": { "type": "int",     "required": True, "label": "Reservation" },
            "table_id":       { "type": "relation","required": True, "label": "Table",
                                "relation_entity": "table" },
            "notes":          { "type": "textarea","required": False,"label": "Notes",
                                "maxLength": 500 },
        },
        "staff_only": True,
    },

    "message": {
        "endpoint": "/api/messages",
        "list_endpoint": "/api/messages/by-reservation/{reservation_id}",
        "fields": {
            "body": { "type": "textarea", "required": True, "label": "Message",
                      "minLength": 1 },
        },
        "append_only": True,
    },

    "user": {
        "endpoint": "/api/users",
        "fields": {
            "email":    { "type": "email",    "required": True,  "label": "Email" },
            "password": { "type": "password", "required": True,  "label": "Password",
                          "note": "Max 72 bytes. Write-only — never returned." },
            "role":     { "type": "enum",     "required": False, "label": "Role",
                          "options": ["member", "staff", "admin"],
                          "default": "member",
                          "admin_only": True },
        },
    },
}


@router.get("")
def get_schema(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    max_capacity = (
        db.query(func.max(Table.seat_count))
        .filter(Table.is_active == True)
        .scalar() or 4
    )

    schema = SCHEMA if current_user.role == "admin" else {
        k: v for k, v in SCHEMA.items()
        if not v.get("admin_only") and not v.get("staff_only")
    }

    return {
        **schema,
        "_config": {
            "max_party_size": max_capacity
        }
    }

