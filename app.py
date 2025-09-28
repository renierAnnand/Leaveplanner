import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import uuid

def init_session_state():
    if 'data' not in st.session_state:
        st.session_state.data = load_mock_data()
    if 'current_user' not in st.session_state:
        st.session_state.current_user = 'emp001'

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
                "start_date": "2024-12-14",
                "end_date": "2024-12-20",
                "reason": "Family vacation",
                "total_days": 5,
                "submittedAt": "2024-12-01T10:00:00Z",
                "managerComments": ""
            },
            "req002": {
                "id": "req002",
                "employeeId": "emp001",
                "status": "approved",
                "type": "annual",
                "start_date": "2025-01-15",
                "end_date": "2025-01-17",
                "reason": "Personal time",
                "total_days": 3,
                "submittedAt": "2024-11-15T10:00:00Z",
                "managerComments": "Approved"
            },
            "req003": {
                "id": "req003",
                "employeeId": "emp002",
                "status": "approved",
                "type": "sick",
                "start_date": "2024-12-10",
                "end_date": "2024-12-12",
                "reason": "Medical appointment",
                "total_days": 3,
                "submittedAt": "2024-12-05T10:00:00Z",
                "managerComments": "Get well soon"
            },
            "req004": {
                "id": "req004",
                "employeeId": "mgr001",
                "status": "approved",
                "type": "annual",
                "start_date": "2025-01-20",
                "end_date": "2025-01-24",
                "reason": "Conference attendance",
                "total_days": 5,
                "submittedAt": "2024-12-01T10:00:00Z",
                "managerComments": "Auto-approved"
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

def is_workday(date_obj):
    day_of_week = date_obj.weekday()
    return day_of_week < 5

def calculate_workdays(start_date, end_date):
    workdays = 0
    current_date = start_date
    while current_date <= end_date:
        if is_workday(current_date):
            workdays += 1
        current_date += timedelta(days=1)
    return workdays

def get_leave_for_date(check_date, user_id=None):
    """Get leave information for a specific date"""
    date_str = check_date.strftime("%Y-%m-%d")
    leave_info = []
    
    for req in st.session_state.data["leaveRequests"].values():
        if user_id and req["employeeId"] != user_id:
            continue
            
        start_date = datetime.strptime(req["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(req["end_date"], "%Y-%m-%d").date()
        
        if start_date <= check_date <= end_date:
            employee = st.session_state.data["users"][req["employeeId"]]
            leave_info.append({
                "employee": employee["name"],
                "type": req["type"],
                "status": req["status"],
                "reason": req["reason"]
            })
    
    return leave_info

def render_calendar_view():
    st.title("📅 Leave Calendar")
    
    # Calendar navigation
    if 'calendar_year' not in st.session_state:
        st.session_state.calendar_year = date.today().year
    if 'calendar_month' not in st.session_state:
        st.session_state.calendar_month = date.today().month
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("◀ Year"):
            st.session_state.calendar_year -= 1
            st.rerun()
    
    with col2:
        if st.button("◀ Month"):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
            st.rerun()
    
    with col3:
        st.markdown("### " + calendar.month_name[st.session_state.calendar_month] + " " + str(st.session_state.calendar_year))
    
    with col4:
        if st.button("Month ▶"):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()
    
    with col5:
        if st.button("Year ▶"):
            st.session_state.calendar_year += 1
            st.rerun()
    
    # View options
    view_mode = st.radio("View Mode:", ["My Leave Only", "Team View (All Users)"], horizontal=True)
    
    # Color legend
    st.markdown("### 🎨 Color Legend")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("🟡 **Pending** - Awaiting approval")
    with col2:
        st.markdown("🟢 **Approved** - Confirmed leave")
    with col3:
        st.markdown("🔴 **Rejected** - Denied request")
    with col4:
        st.markdown("🔵 **Holiday** - Public holiday")
    
    st.markdown("---")
    
    # Generate calendar
    cal = calendar.monthcalendar(st.session_state.calendar_year, st.session_state.calendar_month)
    
    # Day headers
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown("**" + day + "**")
    
    # Calendar days
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    current_date = date(st.session_state.calendar_year, st.session_state.calendar_month, day)
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    # Check for holidays
                    is_holiday = any(h["date"] == date_str for h in st.session_state.data["holidays"])
                    
                    # Get leave information
                    if view_mode == "My Leave Only":
                        leave_info = get_leave_for_date(current_date, st.session_state.current_user)
                    else:
                        leave_info = get_leave_for_date(current_date)
                    
                    # Determine background color and content
                    if is_holiday:
                        holiday_name = next(h["name"] for h in st.session_state.data["holidays"] if h["date"] == date_str)
                        st.markdown(
                            "<div style='background-color: #E3F2FD; border: 2px solid #2196F3; padding: 8px; border-radius: 5px; text-align: center; min-height: 60px;'>"
                            "<strong>" + str(day) + "</strong><br>"
                            "<small>🔵 " + holiday_name + "</small>"
                            "</div>", 
                            unsafe_allow_html=True
                        )
                    elif leave_info:
                        # Determine color based on status
                        status_colors = {
                            "pending": "#FFF3E0",
                            "approved": "#E8F5E8", 
                            "rejected": "#FFEBEE"
                        }
                        status_borders = {
                            "pending": "#FF9800",
                            "approved": "#4CAF50",
                            "rejected": "#F44336"
                        }
                        status_icons = {
                            "pending": "🟡",
                            "approved": "🟢",
                            "rejected": "🔴"
                        }
                        
                        # Use the first leave request's status for coloring
                        primary_status = leave_info[0]["status"]
                        bg_color = status_colors.get(primary_status, "#F5F5F5")
                        border_color = status_borders.get(primary_status, "#CCCCCC")
                        status_icon = status_icons.get(primary_status, "⚪")
                        
                        # Build content
                        content = "<div style='background-color: " + bg_color + "; border: 2px solid " + border_color + "; padding: 8px; border-radius: 5px; text-align: center; min-height: 60px;'>"
                        content += "<strong>" + str(day) + "</strong><br>"
                        
                        for leave in leave_info:
                            if view_mode == "Team View (All Users)":
                                content += "<small>" + status_icons[leave["status"]] + " " + leave["employee"] + "</small><br>"
                            else:
                                content += "<small>" + status_icons[leave["status"]] + " " + leave["type"].title() + "</small><br>"
                        
                        content += "</div>"
                        st.markdown(content, unsafe_allow_html=True)
                        
                        # Show details on hover/click
                        if st.button("ℹ️", key="info_" + str(st.session_state.calendar_year) + "_" + str(st.session_state.calendar_month) + "_" + str(day)):
                            st.session_state.show_date_details = current_date
                    else:
                        # Regular day
                        is_weekend = current_date.weekday() >= 5
                        bg_color = "#F5F5F5" if is_weekend else "#FFFFFF"
                        
                        st.markdown(
                            "<div style='background-color: " + bg_color + "; border: 1px solid #E0E0E0; padding: 8px; border-radius: 5px; text-align: center; min-height: 60px;'>"
                            "<strong>" + str(day) + "</strong>"
                            "</div>", 
                            unsafe_allow_html=True
                        )
    
    # Show details panel if a date is selected
    if hasattr(st.session_state, 'show_date_details'):
        selected_date = st.session_state.show_date_details
        st.markdown("---")
        st.subheader("📋 Details for " + selected_date.strftime("%B %d, %Y"))
        
        if view_mode == "My Leave Only":
            leave_details = get_leave_for_date(selected_date, st.session_state.current_user)
        else:
            leave_details = get_leave_for_date(selected_date)
        
        if leave_details:
            for leave in leave_details:
                status_icon = {"pending": "🟡", "approved": "🟢", "rejected": "🔴"}.get(leave["status"], "⚪")
                
                with st.expander(status_icon + " " + leave["employee"] + " - " + leave["type"].title()):
                    st.write("**Status:** " + leave["status"].title())
                    st.write("**Leave Type:** " + leave["type"].title())
                    st.write("**Reason:** " + leave["reason"])
        else:
            st.info("No leave requests for this date.")
        
        if st.button("Close Details"):
            del st.session_state.show_date_details
            st.rerun()

def render_dashboard():
    user = st.session_state.data["users"][st.session_state.current_user]
    
    st.title("Welcome, " + user['name'])
    st.caption("Role: " + user['role'].title() + " | Department: " + user['department'])
    
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
        for req in user_requests:
            with st.expander(req['type'].title() + " Leave - " + req['status'].title()):
                st.write("**Start Date:** " + req['start_date'])
                st.write("**End Date:** " + req['end_date'])
                st.write("**Reason:** " + req['reason'])
                st.write("**Days:** " + str(req['total_days']))
                if req.get("managerComments"):
                    st.write("**Manager Comments:** " + req['managerComments'])
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
        total_days = calculate_workdays(start_date, end_date)
        
        st.subheader("Leave Calculation")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Days", (end_date - start_date).days + 1)
        with col2:
            st.metric("Workdays", total_days)
        with col3:
            st.metric("Weekends", (end_date - start_date).days + 1 - total_days)
        
        leave_type = st.selectbox("Leave Type", 
                                 options=[lt["id"] for lt in st.session_state.data["settings"]["leaveTypes"]],
                                 format_func=lambda x: next(lt["name"] for lt in st.session_state.data["settings"]["leaveTypes"] if lt["id"] == x))
        
        reason = st.text_area("Reason for Leave", height=100)
        
        if st.button("Submit Leave Request"):
            if reason.strip():
                request_id = "req_" + uuid.uuid4().hex[:8]
                new_request = {
                    "id": request_id,
                    "employeeId": st.session_state.current_user,
                    "status": "pending",
                    "type": leave_type,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "reason": reason,
                    "total_days": total_days,
                    "submittedAt": datetime.now().isoformat(),
                    "managerComments": ""
                }
                
                st.session_state.data["leaveRequests"][request_id] = new_request
                user["leaveBalance"][leave_type]["pending"] += total_days
                
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
    
    for req in user_requests:
        status_color = {
            "pending": "🟠", 
            "approved": "🟢",
            "rejected": "🔴"
        }.get(req["status"], "⚪")
        
        with st.expander(status_color + " " + req['type'].title() + " Leave - " + req['status'].title()):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Request ID:** " + req['id'])
                st.write("**Type:** " + req['type'].title())
                st.write("**Status:** " + req['status'].title())
                st.write("**Submitted:** " + req['submittedAt'][:10])
            
            with col2:
                st.write("**Start Date:** " + req['start_date'])
                st.write("**End Date:** " + req['end_date'])
                st.write("**Total Days:** " + str(req['total_days']))
                st.write("**Reason:** " + req['reason'])
            
            if req.get("managerComments"):
                st.info("**Manager Comments:** " + req['managerComments'])

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
        st.subheader("🔔 Pending Approvals (" + str(len(pending_requests)) + ")")
        
        for req in pending_requests:
            employee = st.session_state.data["users"][req["employeeId"]]
            
            with st.expander(employee['name'] + " - " + req['type'].title() + " Leave"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Employee:** " + employee['name'])
                    st.write("**Department:** " + employee['department'])
                    st.write("**Leave Type:** " + req['type'].title())
                    st.write("**Total Days:** " + str(req['total_days']))
                
                with col2:
                    st.write("**Start Date:** " + req['start_date'])
                    st.write("**End Date:** " + req['end_date'])
                    st.write("**Submitted:** " + req['submittedAt'][:10])
                    st.write("**Reason:** " + req['reason'])
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Approve", key="approve_" + req['id']):
                        approve_request(req["id"], "")
                        st.success("Request approved!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Reject", key="reject_" + req['id']):
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
    
    employee["leaveBalance"][req["type"]]["used"] += req["total_days"]
    employee["leaveBalance"][req["type"]]["pending"] -= req["total_days"]

def reject_request(request_id, comments):
    req = st.session_state.data["leaveRequests"][request_id]
    employee = st.session_state.data["users"][req["employeeId"]]
    
    req["status"] = "rejected"
    req["managerComments"] = comments
    req["approvedBy"] = st.session_state.current_user
    req["approvedAt"] = datetime.now().isoformat()
    
    employee["leaveBalance"][req["type"]]["pending"] -= req["total_days"]

def render_role_switcher():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Demo Role Switcher")
    
    users = st.session_state.data["users"]
    user_options = {}
    for user_id, user in users.items():
        user_options[user['name'] + " (" + user['role'] + ")"] = user_id
    
    current_user_data = users[st.session_state.current_user]
    current_selection = current_user_data['name'] + " (" + current_user_data['role'] + ")"
    
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
    
    nav_options = ["Dashboard", "Plan Leave", "My Requests", "Calendar View"]
    if user["role"] in ["manager", "admin"]:
        nav_options.append("Team View")
    
    selected_page = st.sidebar.radio("Go to:", nav_options)
    
    page_mapping = {
        "Dashboard": "dashboard",
        "Plan Leave": "plan_leave", 
        "My Requests": "my_requests",
        "Calendar View": "calendar_view",
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
    elif st.session_state.page == "calendar_view":
        render_calendar_view()
    elif st.session_state.page == "team_view":
        render_team_view()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Info")
    user_info = "**Current User:** " + user['name'] + "  \n"
    user_info += "**Role:** " + user['role'].title() + "  \n"
    user_info += "**Department:** " + user['department'] + "\n\n"
    user_info += "**Weekend Bridging:** ✅  \n"
    user_info += "**Exclude Holidays:** ✅"
    st.sidebar.info(user_info)

if __name__ == "__main__":
    main()
