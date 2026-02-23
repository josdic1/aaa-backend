# app/api/routes/admin.py
from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from app.api.deps.auth import hash_password, get_current_user
from app.api.deps.db import get_db
from app.models.dining_room import DiningRoom
from app.models.member import Member
from app.models.menu_item import MenuItem
from app.models.message import Message
from app.models.order import Order
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.seat_assignment import SeatAssignment
from app.models.table import Table
from app.models.user import User
from app.schemas.dining_room import DiningRoomCreate, DiningRoomRead
from app.schemas.member import MemberCreate, MemberRead, MemberUpdate
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.schemas.orders import OrderResponse
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationUpdate
from app.schemas.table import TableCreate, TableRead
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(user: User = Depends(get_current_user)) -> None:
    if user.role not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Forbidden")

# ══════════════════════════════════════════════
# USERS
# ══════════════════════════════════════════════

@router.get("/users", response_model=List[UserRead])
def admin_list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return db.query(User).order_by(User.id.asc()).all()


@router.get("/users/{user_id}", response_model=UserRead)
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserRead, status_code=201)
def admin_create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role or "member",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
def admin_update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    db.delete(user)
    db.commit()
    return None


# ══════════════════════════════════════════════
# MEMBERS
# ══════════════════════════════════════════════

@router.get("/members", response_model=List[MemberRead])
def admin_list_members(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return db.query(Member).order_by(Member.id.asc()).all()


@router.get("/members/{member_id}", response_model=MemberRead)
def admin_get_member(
    member_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.post("/members", response_model=MemberRead, status_code=201)
def admin_create_member(
    payload: MemberCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    member = Member(
        user_id=user_id,
        name=payload.name,
        relation=payload.relation,
        dietary_restrictions=payload.dietary_restrictions,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.patch("/members/{member_id}", response_model=MemberRead)
def admin_update_member(
    member_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(member, k, v)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/members/{member_id}", status_code=204)
def admin_delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
    return None


# ══════════════════════════════════════════════
# RESERVATIONS
# ══════════════════════════════════════════════

@router.get("/reservations", response_model=List[ReservationRead])
def admin_list_reservations(
    status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = db.query(Reservation)
    if status:
        q = q.filter(Reservation.status == status)
    if from_date:
        q = q.filter(Reservation.date >= from_date)
    if to_date:
        q = q.filter(Reservation.date <= to_date)
    return q.order_by(Reservation.date.asc(), Reservation.start_time.asc()).all()


@router.get("/reservations/{reservation_id}", response_model=ReservationRead)
def admin_get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.post("/reservations", response_model=ReservationRead, status_code=201)
def admin_create_reservation(
    payload: ReservationCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reservation = Reservation(
        user_id=user_id,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=payload.status or "draft",
        notes=payload.notes,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.patch("/reservations/{reservation_id}", response_model=ReservationRead)
def admin_update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(reservation, k, v)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.delete("/reservations/{reservation_id}", status_code=204)
def admin_delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(reservation)
    db.commit()
    return None

# ADDITIONS FOR app/api/routes/admin.py
# Add these two blocks anywhere after the existing ORDERS section

# ══════════════════════════════════════════════
# ATTENDEES (admin full list + CRUD)
# ══════════════════════════════════════════════

@router.get("/attendees")
def admin_list_attendees(
    reservation_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = db.query(ReservationAttendee)
    if reservation_id:
        q = q.filter(ReservationAttendee.reservation_id == reservation_id)
    return q.order_by(ReservationAttendee.id.asc()).all()


@router.patch("/attendees/{attendee_id}")
def admin_update_attendee(
    attendee_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    attendee = db.get(ReservationAttendee, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    for k, v in payload.items():
        if hasattr(attendee, k):
            setattr(attendee, k, v)
    db.commit()
    db.refresh(attendee)
    return attendee


@router.delete("/attendees/{attendee_id}", status_code=204)
def admin_delete_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    attendee = db.get(ReservationAttendee, attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    db.delete(attendee)
    db.commit()
    return None


# ══════════════════════════════════════════════
# ORDERS — add PATCH for full status override
# (your existing /fulfill only does fired→fulfilled)
# ══════════════════════════════════════════════

@router.patch("/orders/{order_id}")
def admin_patch_order(
    order_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if "status" in payload:
        order.status = payload["status"]
    db.commit()
    db.refresh(order)
    return order


# ══════════════════════════════════════════════
# MENU ITEMS
# ══════════════════════════════════════════════

@router.get("/menu-items", response_model=List[MenuItemResponse])
def admin_list_menu_items(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return db.query(MenuItem).order_by(MenuItem.id.asc()).all()


@router.post("/menu-items", response_model=MenuItemResponse, status_code=201)
def admin_create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    item = MenuItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/menu-items/{item_id}", response_model=MenuItemResponse)
def admin_update_menu_item(
    item_id: int,
    payload: MenuItemUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/menu-items/{item_id}", status_code=204)
def admin_delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return None


@router.patch("/menu-items/{item_id}/toggle", response_model=MenuItemResponse)
def admin_toggle_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    item.is_active = not item.is_active
    db.commit()
    db.refresh(item)
    return item


# ══════════════════════════════════════════════
# DINING ROOMS
# ══════════════════════════════════════════════

@router.get("/dining-rooms", response_model=List[DiningRoomRead])
def admin_list_dining_rooms(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return db.query(DiningRoom).order_by(DiningRoom.id.asc()).all()


@router.post("/dining-rooms", response_model=DiningRoomRead, status_code=201)
def admin_create_dining_room(
    payload: DiningRoomCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    room = DiningRoom(**payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.patch("/dining-rooms/{room_id}", response_model=DiningRoomRead)
def admin_update_dining_room(
    room_id: int,
    payload: DiningRoomCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    room = db.get(DiningRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(room, k, v)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/dining-rooms/{room_id}", status_code=204)
def admin_delete_dining_room(
    room_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    room = db.get(DiningRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")
    db.delete(room)
    db.commit()
    return None


@router.patch("/dining-rooms/{room_id}/toggle", response_model=DiningRoomRead)
def admin_toggle_dining_room(
    room_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    room = db.get(DiningRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")
    room.is_active = not room.is_active
    db.commit()
    db.refresh(room)
    return room


# ══════════════════════════════════════════════
# TABLES
# ══════════════════════════════════════════════

@router.get("/tables", response_model=List[TableRead])
def admin_list_tables(
    dining_room_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = db.query(Table)
    if dining_room_id:
        q = q.filter(Table.dining_room_id == dining_room_id)
    return q.order_by(Table.dining_room_id.asc(), Table.id.asc()).all()


@router.post("/tables", response_model=TableRead, status_code=201)
def admin_create_table(
    payload: TableCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    table = Table(**payload.model_dump())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@router.patch("/tables/{table_id}", response_model=TableRead)
def admin_update_table(
    table_id: int,
    payload: TableCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    table = db.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(table, k, v)
    db.commit()
    db.refresh(table)
    return table


@router.delete("/tables/{table_id}", status_code=204)
def admin_delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    table = db.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    db.delete(table)
    db.commit()
    return None


@router.patch("/tables/{table_id}/toggle", response_model=TableRead)
def admin_toggle_table(
    table_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    table = db.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    table.is_active = not table.is_active
    db.commit()
    db.refresh(table)
    return table


# ══════════════════════════════════════════════
# ORDERS (kitchen view)
# ══════════════════════════════════════════════

@router.get("/orders", response_model=List[OrderResponse])
def admin_list_orders(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    return q.order_by(Order.id.desc()).all()


@router.patch("/orders/{order_id}/fulfill", response_model=OrderResponse)
def admin_fulfill_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "fired":
        raise HTTPException(status_code=400, detail="Order must be fired before fulfilling")
    order.status = "fulfilled"
    db.commit()
    db.refresh(order)
    return order


@router.delete("/orders/{order_id}", status_code=204)
def admin_delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return None


# ══════════════════════════════════════════════
# MESSAGES
# ══════════════════════════════════════════════

@router.get("/messages")
def admin_list_messages(
    reservation_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = db.query(Message).options(selectinload(Message.sender))
    if reservation_id:
        q = q.filter(Message.reservation_id == reservation_id)
    return q.order_by(Message.created_at.desc()).all()


@router.delete("/messages/{message_id}", status_code=204)
def admin_delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message)
    db.commit()
    return None


# ══════════════════════════════════════════════
# SEAT ASSIGNMENTS
# ══════════════════════════════════════════════

@router.get("/seat-assignments")
def admin_list_seat_assignments(
    date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    q = db.query(SeatAssignment).options(
        selectinload(SeatAssignment.reservation),
        selectinload(SeatAssignment.table),
    )
    if date:
        q = q.join(Reservation).filter(Reservation.date == date)
    return q.order_by(SeatAssignment.id.asc()).all()


@router.delete("/seat-assignments/{assignment_id}", status_code=204)
def admin_delete_seat_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    assignment = db.get(SeatAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return None


# ══════════════════════════════════════════════
# DAILY VIEW
# ══════════════════════════════════════════════

@router.get("/daily")
def admin_daily_view(
    date: date = Query(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    reservations = (
        db.query(Reservation)
        .options(
            selectinload(Reservation.attendees),
            selectinload(Reservation.seat_assignment).selectinload(SeatAssignment.table),
            selectinload(Reservation.messages),
        )
        .filter(Reservation.date == date)
        .order_by(Reservation.start_time.asc())
        .all()
    )

    result = []
    for r in reservations:
        table_info = None
        if r.seat_assignment:
            t = r.seat_assignment.table
            table_info = {"table_id": t.id, "table_name": t.name, "seat_count": t.seat_count}

        result.append({
            "reservation_id": r.id,
            "user_id": r.user_id,
            "date": r.date,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "status": r.status,
            "notes": r.notes,
            "party_size": len(r.attendees),
            "table": table_info,
            "message_count": len(r.messages),
        })

    return {"date": date, "reservations": result, "total": len(result)}