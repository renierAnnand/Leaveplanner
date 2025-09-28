import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, timedelta
import calendar
from typing import List, Dict, Tuple
import uuid

def init_session_state():
    if 'data' not in st.session_state:
        st.session_state.data = load_mock_data()
    if 'current_user' not in st.session_state:
        st.session_state.current_user = 'emp001'
    if 'selected_ranges' not in st.session_state:
        st.session_state.selected_ranges = []
    if 'temp_range_start' not in st.session_state:
        st.session_state.temp_range_start = None

def load_mock_data():
    return {
        "users": {
            "emp001": {
                "id": "emp001",
                "name": "Ahmed Al-Rashid",
                "role": "employee",
                "department": "Engineering",
                "manager": "mgr001",
                "leaveBalance": {
                    "annual": {"total": 30, "used": 8, "pending": 3},
                    "sick": {"total": 15, "used": 2, "pending": 0},
                    "personal": {"total": 5, "used": 1, "pending": 0}
                }
            },
            "emp002": {
                "id": "emp002",
                "name": "Sara Al-Mahmoud",
                "role": "employee",
                "department": "Marketing",
                "manager": "mgr001",
                "leaveBalance": {
                    "annual": {"total": 25, "used": 12, "pending": 2},
                    "sick": {"total": 15, "used": 3, "pending": 0}
                }
            },
            "mgr001": {
                "id": "mgr001",
                "name": "Fatima Al-Zahra",
                "role": "manager",
                "department": "Engineering",
                "manager": None,
                "leaveBalance": {
                    "annual": {"total": 35, "used": 12, "pending": 0},
                    "sick": {"total": 20, "used": 1, "pending": 0}
                }
            },
            "admin001": {
                "id": "admin001",
                "name": "Omar Al-Faisal",
                "role": "admin",
                "department": "HR",
                "manager": None,
                "leaveBalance": {
                    "annual": {"total": 40, "used": 5, "pending": 0}
                }
            }
        },
        "holidays": [
            {"date": "2024-01-01", "name": "New Year's Day", "type": "public"},
            {"date": "2024-09-23", "name": "Saudi National Day", "type": "public"},
            {"date": "2024-12-25", "name": "Christmas Day", "type": "public"},
            {"date": "2024-04-10", "name": "Eid al-Fitr", "type": "religious"},
            {"date": "2024-06-16", "name": "Eid al-Adha", "type": "religious"}
        ],
        "leaveRequests": {
            "req001": {
                "id": "req001",
                "employeeId": "emp001",
                "status": "pending",
                "type": "annual",
                "ranges": [
                    {"start": "2024-12-14", "end": "2024-12-15"},
                    {"start": "2024-12-18", "end": "2024-12-20"}
                ],
                "reason": "Family vacation",
                "daysCalculation": {
                    "workdays": 5,
                    "bridgeDays": 2,
                    "excludedHolidays": 0,
                    "totalDeducted": 7
                },
                "submittedAt": "2024-12-01T10:00:00Z",
                "managerComments": ""
            }
        },
        "settings": {
            "workweek": {"start": 0, "end": 4},
            "weekendBridging": True,
            "excludeHolidays": True,
            "leaveTypes": [
                {"id": "annual", "name": "Annual Leave", "color": "#4CAF50"},
                {"id": "sick", "name": "Sick Leave", "color": "#FF9800"},
                {"id": "personal", "name": "Personal Leave", "color": "#2196F3"},
                {"id": "emergency", "name": "Emergency Leave", "color": "#F44336"}
            ]
        }
    }

def is_workday(date_obj, settings):
    day_of_week = date_obj.weekday()
    day_of_week = (day_of_week + 1) % 7
    return settings["workweek"]["start"] <= day_of_week <= settings["workweek"]["end"]

def is_holiday(date_obj, holidays):
    date_str = date_obj.strftime("%Y-%m-%d")
    return any(h["date"] == date_str for h in holidays)

def calculate_leave_days(ranges, holidays, settings):
    if not ranges:
        return {"workdays": 0, "bridgeDays": 0, "excludedHolidays": 0, "totalDeducted": 0}
    
    total_workdays = 0
    bridge_days = 0
    excluded_holidays = 0
    
    for range_data in ranges:
        start_date = datetime.strptime(range_data["start"], "%Y-%m-%d").date()
        end_date = datetime.strptime(range_data["end"], "%Y-%m-%d").date()
        
        current_date = start_date
        while current_date <= end_date:
            if is_workday(current_date, settings):
                if not (settings["excludeHolidays"] and is_holiday(current_date, holidays)):
                    total_workdays += 1
                elif settings["excludeHolidays"] and is_holiday(current_date, holidays):
                    excluded_holidays += 1
            current_date += timedelta(days=1)
    
    return {
        "workdays": total_workdays,
        "bridgeDays": bridge_days,
        "excludedHolidays": excluded_holidays,
        "totalDeducted": total_workdays + bridge_days
    }

def render_dashboard():
    user = st.session_state.data["users"][st.session_state.current_user]
    
    st.title(f"Welcome, {user['name']}")
    st.caption(f"Role: {user['role'].title()} | Department: {user['department']}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_balance = sum(b["total"] for b in user["leaveBalance"].values())
    total_used = sum(b["used"] for b in user["leaveBalance"].values())
    total_pending = sum(b["pending"] for b in user["leaveBalance"].values())
    
    with col1:
        st.metric("Total Leave Balance", total_balance)
    with col2:
        st.metric("Used This Year", total_used)
    with col3:
        st.metric("Pending Requests", total_pending)
    with col4:
        st.metric("Available", total_balance - total_used - total_pending)
    
    st.markdown("---")
    
    st.subheader("Recent Leave Requests")
    user_requests = [req for req in st.session_state.data["leaveRequests"].values() 
                    if req["employeeId"] == st.session_state.current_user]
    
    if user_requests:
        for req in sorted(user_requests, key=lambda x: x["submittedAt"], reverse=True)[:3]:
            with st.expander(f"{req['type'].title()} Leave - {req['status'].title()}"):
                st.write(f"**Dates:** {', '.join([f\"{r['start']} to {r['end']}\" for r in req['ranges']])}")
                st.write(f"**Reason:** {req['reason']}")
                st.write(f"**Days:** {req['daysCalculation']['totalDeducted']}")
                if req.get("managerComments"):
                    st.write(f"**Manager Comments:** {req['managerComments']}")
    else:
        st.info("No leave requests found. Click 'Plan Leave' to create your first request!")

def render_plan_leave():
    st.title("📅 Plan Leave")
    
    user = st.session_state.data["users"][st.session_state.current_user]
    
    st.subheader("Select Leave Dates")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today())
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    if start_date and end_date and start_date <= end_date:
        ranges = [{"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")}]
        calculation = calculate_leave_days(ranges, st.session_state.data["holidays"], st.session_state.data["settings"])
        
        st.subheader("Leave Calculation")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Workdays", calculation["workdays"])
        with col2:
            st.metric("Bridge Days", calculation["bridgeDays"])
        with col3:
            st.metric("Total Deducted", calculation["totalDeducted"])
        
        leave_type = st.selectbox("Leave Type", 
                                 options=[lt["id"] for lt in st.session_state.data["settings"]["leaveTypes"]],
                                 format_func=lambda x: next(lt["name"] for lt in st.session_state.data["settings"]["leaveTypes"] if lt["id"] == x))
        
        reason = st.text_area("Reason for Leave", height=100)
        
        if st.button("Submit Leave Request"):
            if reason.strip():
                request_id = f"req_{uuid.uuid4().hex[:8]}"
                new_request = {
                    "id": request_id,
                    "employeeId": st.session_state.current_user,
                    "status": "pending",
                    "type": leave_type,
                    "ranges": ranges,
                    "reason": reason,
                    "daysCalculation": calculation,
                    "submittedAt": datetime.now().isoformat(),
                    "managerComments": ""
                }
                
                st.session_state.data["leaveRequests"][request_id] = new_request
                user["leaveBalance"][leave_type]["pending"] += calculation["totalDeducted"]
                
                st.success("Leave request submitted successfully!")
                st.rerun()
            else:
                st.error("Please provide a reason for your leave request.")

def render_my_requests():
    st.title("📋 My Leave Requests")
    
    user_requests = [req for req in st.session_state.data["leaveRequests"].values() 
                    if req["employeeId"] == st.session_state.current_user]
    
    if not user_requests:
        st.info("You haven't submitted any leave requests yet.")
        return
    
    for req in sorted(user_requests, key=lambda x: x["submittedAt"], reverse=True):
        status_color = {
            "pending": "🟠", 
            "approved": "🟢",
            "rejected": "🔴"
        }.get(req["status"], "⚪")
        
        with st.expander(f"{status_color} {req['type'].title()} Leave - {req['status'].title()}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Request ID:** {req['id']}")
                st.write(f"**Type:** {req['type'].title()}")
                st.write(f"**Status:** {req['status'].title()}")
                st.write(f"**Submitted:** {req['submittedAt'][:10]}")
            
            with col2:
                st.write(f"**Total Days:** {req['daysCalculation']['totalDeducted']}")
                st.write(f"**Reason:** {req['reason']}")
            
            st.write("**Date Ranges:**")
            for range_data in req["ranges"]:
                st.write(f"• {range_data['start']} to {range_data['end']}")
            
            if req.get("managerComments"):
                st.info(f"**Manager Comments:** {req['managerComments']}")

def render_team_view():
    st.title("👥 Team View")
    
    if st.session_state.data["users"][st.session_state.current_user]["role"] not in ["manager", "admin"]:
        st.error("Access denied. Manager role required.")
        return
    
    current_user = st.session_state.data["users"][st.session_state.current_user]
    if current_user["role"] == "admin":
        team_members = list(st.session_state.data["users"].values())
    else:
        team_members = [user for user in st.session_state.data["users"].values() 
                       if user.get("manager") == st.session_state.current_user]
    
    pending_requests = [req for req in st.session_state.data["leaveRequests"].values() 
                       if req["status"] == "pending" and 
                       req["employeeId"] in [member["id"] for member in team_members]]
    
    if pending_requests:
        st.subheader(f"🔔 Pending Approvals ({len(pending_requests)})")
        
        for req in pending_requests:
            employee = st.session_state.data["users"][req["employeeId"]]
            
            with st.expander(f"{employee['name']} - {req['type'].title()} Leave"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Employee:** {employee['name']}")
                    st.write(f"**Department:** {employee['department']}")
                    st.write(f"**Leave Type:** {req['type'].title()}")
                    st.write(f"**Total Days:** {req['daysCalculation']['totalDeducted']}")
                
                with col2:
                    st.write(f"**Submitted:** {req['submittedAt'][:10]}")
                    st.write(f"**Reason:** {req['reason']}")
                
                st.write("**Date Ranges:**")
                for range_data in req["ranges"]:
                    st.write(f"• {range_data['start']} to {range_data['end']}")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{req['id']}"):
                        approve_request(req["id"], "")
                        st.success("Request approved!")
                        st.rerun()
                
                with col2:
                    if st.button(f"❌ Reject", key=f"reject_{req['id']}"):
                        reject_request(req["id"], "Request rejected by manager")
                        st.success("Request rejected!")
                        st.rerun()
    else:
        st.info("No pending requests to review.")

def approve_request(request_id, comments):
    req = st.session_state.data["leaveRequests"][request_id]
    employee = st.session_state.data["users"][req["employeeId"]]
    
    req["status"] = "approved"
    req["managerComments"] = comments
    req["approvedBy"] = st.session_state.current_user
    req["approvedAt"] = datetime.now().isoformat()
    
    employee["leaveBalance"][req["type"]]["used"] += req["daysCalculation"]["totalDeducted"]
    employee["leaveBalance"][req["type"]]["pending"] -= req["daysCalculation"]["totalDeducted"]

def reject_request(request_id, comments):
    req = st.session_state.data["leaveRequests"][request_id]
    employee = st.session_state.data["users"][req["employeeId"]]
    
    req["status"] = "rejected"
    req["managerComments"] = comments
    req["approvedBy"] = st.session_state.current_user
    req["approvedAt"] = datetime.now().isoformat()
    
    employee["leaveBalance"][req["type"]]["pending"] -= req["daysCalculation"]["totalDeducted"]

def render_role_switcher():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Demo Role Switcher")
    
    users = st.session_state.data["users"]
    user_options = {f"{user['name']} ({user['role']})": user_id 
                   for user_id, user in users.items()}
    
    current_selection = f"{users[st.session_state.current_user]['name']} ({users[st.session_state.current_user]['role']})"
    
    selected_user = st.sidebar.selectbox(
        "Switch User Role:",
        options=list(user_options.keys()),
        index=list(user_options.keys()).index(current_selection)
    )
    
    if user_options[selected_user] != st.session_state.current_user:
        st.session_state.current_user = user_options[selected_user]
        st.rerun()

def main():
    st.set_page_config(
        page_title="Leave Planning System",
        page_icon="📅",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    
    render_role_switcher()
    
    user = st.session_state.data["users"][st.session_state.current_user]
    
    st.sidebar.markdown("## 🧭 Navigation")
    
    nav_options = ["Dashboard", "Plan Leave", "My Requests"]
    if user["role"] in ["manager", "admin"]:
        nav_options.append("Team View")
    
    selected_page = st.sidebar.radio("Go to:", nav_options)
    
    page_mapping = {
        "Dashboard": "dashboard",
        "Plan Leave": "plan_leave", 
        "My Requests": "my_requests",
        "Team View": "team_view"
    }
    
    if page_mapping[selected_page] != st.session_state.page:
        st.session_state.page = page_mapping[selected_page]
        st.rerun()
    
    if st.session_state.page == "dashboard":
        render_dashboard()
    elif st.session_state.page == "plan_leave":
        render_plan_leave()
    elif st.session_state.page == "my_requests":
        render_my_requests()
    elif st.session_state.page == "team_view":
        render_team_view()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Info")
    st.sidebar.info(f"""
    **Current User:** {user['name']}  
    **Role:** {user['role'].title()}  
    **Department:** {user['department']}
    
    **Weekend Bridging:** {'✅' if st.session_state.data['settings']['weekendBridging'] else '❌'}  
    **Exclude Holidays:** {'✅' if st.session_state.data['settings']['excludeHolidays'] else '❌'}
    """)

if __name__ == "__main__":
    main()
