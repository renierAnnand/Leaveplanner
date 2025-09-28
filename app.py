import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, date
import calendar
import hashlib

# Database setup
def init_db():
    conn = sqlite3.connect('leave_planner.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            full_name TEXT,
            role TEXT,
            department TEXT,
            annual_leave_balance INTEGER DEFAULT 30
        )
    ''')
    
    # Leave requests table
    c.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            leave_type TEXT,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            request_date TEXT,
            approved_by TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default admin user
    admin_password = hashlib.md5("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, full_name, role, department) VALUES (?, ?, ?, ?, ?)",
              ("admin", admin_password, "System Administrator", "admin", "IT"))
    
    # Create sample users
    sample_users = [
        ("ahmed.ali", hashlib.md5("password123".encode()).hexdigest(), "Ahmed Ali", "employee", "HR"),
        ("sara.hassan", hashlib.md5("password123".encode()).hexdigest(), "Sara Hassan", "employee", "Finance"),
        ("omar.khalil", hashlib.md5("password123".encode()).hexdigest(), "Omar Khalil", "manager", "Operations"),
        ("fatima.noor", hashlib.md5("password123".encode()).hexdigest(), "Fatima Noor", "employee", "Marketing"),
        ("mohammed.salem", hashlib.md5("password123".encode()).hexdigest(), "Mohammed Salem", "employee", "IT"),
        ("layla.ahmed", hashlib.md5("password123".encode()).hexdigest(), "Layla Ahmed", "employee", "Sales")
    ]
    
    for user in sample_users:
        c.execute("INSERT OR IGNORE INTO users (username, password, full_name, role, department) VALUES (?, ?, ?, ?, ?)", user)
    
    # Add sample leave requests
    sample_requests = [
        (2, "2024-10-15", "2024-10-17", "Annual Leave", "Family vacation", "approved", "2024-10-01", "admin"),
        (3, "2024-11-10", "2024-11-12", "Annual Leave", "Personal matters", "pending", "2024-10-25", ""),
        (4, "2024-11-05", "2024-11-07", "Sick Leave", "Medical appointment", "approved", "2024-10-28", "admin"),
        (2, "2024-12-20", "2024-12-22", "Annual Leave", "Wedding", "pending", "2024-11-01", ""),
        (5, "2024-11-15", "2024-11-16", "Annual Leave", "Personal", "approved", "2024-11-01", "admin"),
        (6, "2024-12-01", "2024-12-03", "Annual Leave", "Holiday", "pending", "2024-11-15", "")
    ]
    
    for req in sample_requests:
        c.execute("INSERT OR IGNORE INTO leave_requests (user_id, start_date, end_date, leave_type, reason, status, request_date, approved_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", req)
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = sqlite3.connect('leave_planner.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

def get_user_leave_requests(user_id):
    conn = sqlite3.connect('leave_planner.db')
    df = pd.read_sql_query("SELECT * FROM leave_requests WHERE user_id = ? ORDER BY request_date DESC", conn, params=(user_id,))
    conn.close()
    return df

def get_all_leave_requests():
    conn = sqlite3.connect('leave_planner.db')
    query = """
    SELECT lr.*, u.full_name, u.department 
    FROM leave_requests lr 
    JOIN users u ON lr.user_id = u.id 
    ORDER BY lr.request_date DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_team_leave_requests(manager_department):
    conn = sqlite3.connect('leave_planner.db')
    query = """
    SELECT lr.*, u.full_name, u.department 
    FROM leave_requests lr 
    JOIN users u ON lr.user_id = u.id 
    WHERE u.department = ? AND u.role != 'manager'
    ORDER BY lr.request_date DESC
    """
    df = pd.read_sql_query(query, conn, params=(manager_department,))
    conn.close()
    return df

def submit_leave_request(user_id, start_date, end_date, leave_type, reason):
    conn = sqlite3.connect('leave_planner.db')
    c = conn.cursor()
    request_date = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO leave_requests (user_id, start_date, end_date, leave_type, reason, request_date) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, start_date, end_date, leave_type, reason, request_date))
    conn.commit()
    conn.close()

def update_leave_status(request_id, status, approved_by):
    conn = sqlite3.connect('leave_planner.db')
    c = conn.cursor()
    c.execute("UPDATE leave_requests SET status = ?, approved_by = ? WHERE id = ?", (status, approved_by, request_id))
    conn.commit()
    conn.close()

def get_leave_for_date_range(start_date, end_date, user_id=None):
    conn = sqlite3.connect('leave_planner.db')
    if user_id:
        query = """
        SELECT lr.*, u.full_name, u.department 
        FROM leave_requests lr 
        JOIN users u ON lr.user_id = u.id 
        WHERE lr.user_id = ? AND lr.start_date <= ? AND lr.end_date >= ?
        """
        df = pd.read_sql_query(query, conn, params=(user_id, end_date, start_date))
    else:
        query = """
        SELECT lr.*, u.full_name, u.department 
        FROM leave_requests lr 
        JOIN users u ON lr.user_id = u.id 
        WHERE lr.start_date <= ? AND lr.end_date >= ?
        """
        df = pd.read_sql_query(query, conn, params=(end_date, start_date))
    conn.close()
    return df

def get_saudi_holidays():
    # Saudi Arabia public holidays (approximate dates for 2024-2025)
    holidays = {
        "2024-01-01": "New Year's Day",
        "2024-04-10": "Eid al-Fitr (Day 1)",
        "2024-04-11": "Eid al-Fitr (Day 2)",
        "2024-04-12": "Eid al-Fitr (Day 3)",
        "2024-06-16": "Eid al-Adha (Day 1)",
        "2024-06-17": "Eid al-Adha (Day 2)",
        "2024-06-18": "Eid al-Adha (Day 3)",
        "2024-07-07": "Islamic New Year",
        "2024-09-16": "Prophet's Birthday",
        "2024-09-23": "Saudi National Day",
        "2024-11-01": "Foundation Day",
        "2025-01-01": "New Year's Day",
        "2025-03-30": "Eid al-Fitr (Day 1)",
        "2025-03-31": "Eid al-Fitr (Day 2)",
        "2025-04-01": "Eid al-Fitr (Day 3)",
        "2025-06-06": "Eid al-Adha (Day 1)",
        "2025-06-07": "Eid al-Adha (Day 2)",
        "2025-06-08": "Eid al-Adha (Day 3)",
        "2025-06-26": "Islamic New Year",
        "2025-09-05": "Prophet's Birthday",
        "2025-09-23": "Saudi National Day",
        "2025-11-01": "Foundation Day"
    }
    return holidays

def calculate_working_days(start_date, end_date):
    """Calculate working days excluding weekends and holidays"""
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    holidays = get_saudi_holidays()
    
    working_days = 0
    current_date = start
    
    while current_date <= end:
        # Skip weekends (Friday=4, Saturday=5 in Saudi Arabia)
        if current_date.weekday() not in [4, 5]:
            # Skip holidays
            if current_date.strftime("%Y-%m-%d") not in holidays:
                working_days += 1
        current_date += timedelta(days=1)
    
    return working_days

def create_admin_calendar_view():
    st.subheader("📅 Admin Calendar - All Staff Leave")
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("Select Month", range(1, 13), 
                                    format_func=lambda x: calendar.month_name[x],
                                    index=datetime.now().month - 1)
    with col2:
        selected_year = st.selectbox("Select Year", range(2024, 2027), 
                                   index=0)
    
    # Get calendar data
    cal = calendar.monthcalendar(selected_year, selected_month)
    holidays = get_saudi_holidays()
    
    # Get all leave requests for the selected month
    start_date = date(selected_year, selected_month, 1)
    if selected_month == 12:
        end_date = date(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(selected_year, selected_month + 1, 1) - timedelta(days=1)
    
    leave_data = get_leave_for_date_range(start_date.strftime("%Y-%m-%d"), 
                                        end_date.strftime("%Y-%m-%d"))
    
    # Create legend
    st.markdown("### Legend")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("🟢 **Approved Leave**")
    with col2:
        st.markdown("🟡 **Pending Leave**")
    with col3:
        st.markdown("🔴 **Rejected Leave**")
    with col4:
        st.markdown("🔵 **Public Holiday**")
    with col5:
        st.markdown("⚪ **Regular Day**")
    
    # Display calendar
    st.markdown(f"### {calendar.month_name[selected_month]} {selected_year}")
    
    # Create calendar grid
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Header row
    header_cols = st.columns(7)
    for i, day in enumerate(days):
        with header_cols[i]:
            st.markdown(f"**{day}**")
    
    # Calendar rows
    for week in cal:
        week_cols = st.columns(7)
        for i, day in enumerate(week):
            with week_cols[i]:
                if day == 0:
                    st.markdown("&nbsp;")
                else:
                    current_date = date(selected_year, selected_month, day)
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    # Check for holidays
                    if date_str in holidays:
                        st.markdown(f"🔵 **{day}**\n{holidays[date_str][:10]}...")
                    else:
                        # Check for leave requests on this date
                        day_leave = []
                        for _, leave in leave_data.iterrows():
                            leave_start = datetime.strptime(leave['start_date'], "%Y-%m-%d").date()
                            leave_end = datetime.strptime(leave['end_date'], "%Y-%m-%d").date()
                            
                            if leave_start <= current_date <= leave_end:
                                status_emoji = {
                                    'approved': '🟢',
                                    'pending': '🟡',
                                    'rejected': '🔴'
                                }.get(leave['status'], '⚪')
                                
                                day_leave.append({
                                    'name': leave['full_name'],
                                    'status': leave['status'],
                                    'emoji': status_emoji,
                                    'type': leave['leave_type'],
                                    'department': leave['department']
                                })
                        
                        if day_leave:
                            # Group by status for display
                            status_counts = {}
                            for leave in day_leave:
                                status = leave['status']
                                if status not in status_counts:
                                    status_counts[status] = {'count': 0, 'emoji': leave['emoji'], 'names': []}
                                status_counts[status]['count'] += 1
                                status_counts[status]['names'].append(leave['name'])
                            
                            # Display day with leave info
                            display_text = f"**{day}**\n"
                            for status, info in status_counts.items():
                                display_text += f"{info['emoji']} {info['count']} "
                            
                            st.markdown(display_text)
                            
                            # Show details in expander
                            with st.expander(f"Details for {day}/{selected_month}"):
                                for leave in day_leave:
                                    st.write(f"{leave['emoji']} **{leave['name']}** ({leave['department']})")
                                    st.write(f"   └─ {leave['type']} - {leave['status'].title()}")
                        else:
                            st.markdown(f"⚪ **{day}**")
    
    # Summary statistics
    st.markdown("### Monthly Summary")
    if not leave_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            approved_count = len(leave_data[leave_data['status'] == 'approved'])
            st.metric("Approved Requests", approved_count)
        
        with col2:
            pending_count = len(leave_data[leave_data['status'] == 'pending'])
            st.metric("Pending Requests", pending_count)
        
        with col3:
            rejected_count = len(leave_data[leave_data['status'] == 'rejected'])
            st.metric("Rejected Requests", rejected_count)
        
        with col4:
            total_days = 0
            for _, leave in leave_data.iterrows():
                start = datetime.strptime(leave['start_date'], "%Y-%m-%d").date()
                end = datetime.strptime(leave['end_date'], "%Y-%m-%d").date()
                total_days += (end - start).days + 1
            st.metric("Total Leave Days", total_days)
        
        # Department breakdown
        st.markdown("### Department Breakdown")
        if not leave_data.empty:
            dept_summary = leave_data.groupby(['department', 'status']).size().unstack(fill_value=0)
            st.dataframe(dept_summary, use_container_width=True)
        
        # Detailed leave list
        st.markdown("### Detailed Leave List")
        display_df = leave_data[['full_name', 'department', 'leave_type', 'start_date', 'end_date', 'status', 'reason']].copy()
        display_df.columns = ['Employee', 'Department', 'Leave Type', 'Start Date', 'End Date', 'Status', 'Reason']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No leave requests found for this month.")

def create_user_calendar_view(user_id):
    st.subheader("📅 My Leave Calendar")
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("Month", range(1, 13), 
                                    format_func=lambda x: calendar.month_name[x],
                                    index=datetime.now().month - 1)
    with col2:
        selected_year = st.selectbox("Year", range(2024, 2027), 
                                   index=0)
    
    # Get calendar data
    cal = calendar.monthcalendar(selected_year, selected_month)
    holidays = get_saudi_holidays()
    
    # Get user's leave requests for the selected month
    start_date = date(selected_year, selected_month, 1)
    if selected_month == 12:
        end_date = date(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(selected_year, selected_month + 1, 1) - timedelta(days=1)
    
    leave_data = get_leave_for_date_range(start_date.strftime("%Y-%m-%d"), 
                                        end_date.strftime("%Y-%m-%d"), user_id)
    
    # Create legend
    st.markdown("### Legend")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("🟢 **Approved Leave**")
    with col2:
        st.markdown("🟡 **Pending Leave**")
    with col3:
        st.markdown("🔴 **Rejected Leave**")
    with col4:
        st.markdown("🔵 **Public Holiday**")
    
    # Display calendar
    st.markdown(f"### {calendar.month_name[selected_month]} {selected_year}")
    
    # Create calendar grid
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Header row
    header_cols = st.columns(7)
    for i, day in enumerate(days):
        with header_cols[i]:
            st.markdown(f"**{day}**")
    
    # Calendar rows
    for week in cal:
        week_cols = st.columns(7)
        for i, day in enumerate(week):
            with week_cols[i]:
                if day == 0:
                    st.markdown("&nbsp;")
                else:
                    current_date = date(selected_year, selected_month, day)
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    # Check for holidays
                    if date_str in holidays:
                        st.markdown(f"🔵 **{day}**\n{holidays[date_str][:8]}...")
                    else:
                        # Check for leave requests on this date
                        has_leave = False
                        leave_status = None
                        leave_type = None
                        
                        for _, leave in leave_data.iterrows():
                            leave_start = datetime.strptime(leave['start_date'], "%Y-%m-%d").date()
                            leave_end = datetime.strptime(leave['end_date'], "%Y-%m-%d").date()
                            
                            if leave_start <= current_date <= leave_end:
                                has_leave = True
                                leave_status = leave['status']
                                leave_type = leave['leave_type']
                                break
                        
                        if has_leave:
                            status_emoji = {
                                'approved': '🟢',
                                'pending': '🟡',
                                'rejected': '🔴'
                            }.get(leave_status, '⚪')
                            st.markdown(f"{status_emoji} **{day}**\n{leave_type[:8]}...")
                        else:
                            st.markdown(f"⚪ **{day}**")

def main():
    st.set_page_config(page_title="Leave Planning System", page_icon="📅", layout="wide")
    
    # Initialize database
    init_db()
    
    st.title("🏢 Leave Planning System - Saudi Arabia")
    st.markdown("*Comprehensive leave management system with Saudi labor law compliance*")
    st.markdown("---")
    
    # Session state for login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_data = None
    
    # Login page
    if not st.session_state.logged_in:
        st.subheader("🔐 Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.container():
                st.markdown("### Welcome to Leave Planning System")
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                if st.button("🚀 Login", use_container_width=True, type="primary"):
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                
                st.markdown("---")
                st.info("""
                **🎯 Demo Accounts:**
                
                **Admin Access:**
                - Username: `admin`
                - Password: `admin123`
                
                **Employee Access:**
                - Username: `ahmed.ali`
                - Password: `password123`
                
                **Manager Access:**
                - Username: `omar.khalil`
                - Password: `password123`
                """)
    
    else:
        # Main application
        user_data = st.session_state.user_data
        
        # Sidebar navigation
        st.sidebar.title(f"👋 Welcome, {user_data[3]}")
        st.sidebar.markdown(f"**🎭 Role:** {user_data[4].title()}")
        st.sidebar.markdown(f"**🏢 Department:** {user_data[5]}")
        st.sidebar.markdown(f"**📊 Leave Balance:** {user_data[6]} days")
        st.sidebar.markdown("---")
        
        # Menu options based on role
        if user_data[4] == 'admin':
            menu_options = ["🗓️ Admin Calendar", "⚙️ Manage Requests", "📝 Submit Leave", "📅 My Calendar", "📋 My Requests"]
        elif user_data[4] == 'manager':
            menu_options = ["📅 My Calendar", "📋 My Requests", "📝 Submit Leave", "👥 Team Requests"]
        else:
            menu_options = ["📅 My Calendar", "📋 My Requests", "📝 Submit Leave"]
        
        selected_menu = st.sidebar.selectbox("🧭 Navigation", menu_options)
        
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()
        
        # Main content based on menu selection
        if selected_menu == "🗓️ Admin Calendar":
            create_admin_calendar_view()
        
        elif selected_menu == "📅 My Calendar":
            create_user_calendar_view(user_data[0])
        
        elif selected_menu == "📝 Submit Leave":
            st.subheader("📝 Submit Leave Request")
            st.markdown("*Please fill out the form below to submit your leave request*")
            
            with st.form("leave_request_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    start_date = st.date_input("📅 Start Date", 
                                             min_value=datetime.now().date(),
                                             help="Select the first day of your leave")
                    leave_type = st.selectbox("📋 Leave Type", 
                                            ["Annual Leave", "Sick Leave", "Emergency Leave", 
                                             "Maternity Leave", "Paternity Leave", "Hajj Leave"],
                                            help="Select the type of leave you're requesting")
                
                with col2:
                    end_date = st.date_input("📅 End Date", 
                                           min_value=start_date if 'start_date' in locals() else datetime.now().date(),
                                           help="Select the last day of your leave")
                    reason = st.text_area("📝 Reason for Leave", 
                                        placeholder="Please provide a detailed reason for your leave request...",
                                        help="Explain why you need this leave")
                
                # Calculate working days
                if start_date and end_date:
                    working_days = calculate_working_days(start_date.strftime("%Y-%m-%d"), 
                                                        end_date.strftime("%Y-%m-%d"))
                    total_days = (end_date - start_date).days + 1
                    st.info(f"📊 **Leave Summary:** {total_days} total days ({working_days} working days)")
                
                submitted = st.form_submit_button("🚀 Submit Request", type="primary", use_container_width=True)
                
                if submitted:
                    if start_date and end_date and reason.strip():
                        if end_date >= start_date:
                            submit_leave_request(user_data[0], start_date.strftime("%Y-%m-%d"), 
                                               end_date.strftime("%Y-%m-%d"), leave_type, reason)
                            st.success("✅ Leave request submitted successfully! Your manager will review it soon.")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ End date must be after or equal to start date")
                    else:
                        st.error("❌ Please fill in all required fields")
        
        elif selected_menu == "📋 My Requests":
            st.subheader("📋 My Leave Requests")
            st.markdown("*View and track all your leave requests*")
            
            requests_df = get_user_leave_requests(user_data[0])
            if not requests_df.empty:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    approved = len(requests_df[requests_df['status'] == 'approved'])
                    st.metric("✅ Approved", approved)
                with col2:
                    pending = len(requests_df[requests_df['status'] == 'pending'])
                    st.metric("⏳ Pending", pending)
                with col3:
                    rejected = len(requests_df[requests_df['status'] == 'rejected'])
                    st.metric("❌ Rejected", rejected)
                with col4:
                    total_days = sum([(datetime.strptime(r['end_date'], "%Y-%m-%d") - 
                                     datetime.strptime(r['start_date'], "%Y-%m-%d")).days + 1 
                                    for _, r in requests_df.iterrows() if r['status'] == 'approved'])
                    st.metric("📅 Days Used", total_days)
                
                st.markdown("---")
                
                # Display requests
                for _, request in requests_df.iterrows():
                    status_config = {
                        'pending': {'color': '🟡', 'bg': '#FFF3CD', 'text': 'Pending Review'},
                        'approved': {'color': '🟢', 'bg': '#D4EDDA', 'text': 'Approved'},
                        'rejected': {'color': '🔴', 'bg': '#F8D7DA', 'text': 'Rejected'}
                    }
                    
                    config = status_config.get(request['status'], status_config['pending'])
                    
                    with st.expander(f"{config['color']} {request['leave_type']} - {request['start_date']} to {request['end_date']} ({config['text']})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**📊 Status:** {request['status'].title()}")
                            st.markdown(f"**📋 Type:** {request['leave_type']}")
                            st.markdown(f"**📅 Duration:** {request['start_date']} to {request['end_date']}")
                            
                            # Calculate days
                            start = datetime.strptime(request['start_date'], "%Y-%m-%d").date()
                            end = datetime.strptime(request['end_date'], "%Y-%m-%d").date()
                            total_days = (end - start).days + 1
                            working_days = calculate_working_days(request['start_date'], request['end_date'])
                            st.markdown(f"**⏱️ Days:** {total_days} total ({working_days} working)")
                            
                        with col2:
                            st.markdown(f"**📝 Reason:** {request['reason']}")
                            st.markdown(f"**📤 Submitted:** {request['request_date']}")
                            if request['approved_by']:
                                st.markdown(f"**✅ Approved by:** {request['approved_by']}")
            else:
                st.info("📭 No leave requests found. Submit your first request using the 'Submit Leave' option.")
        
        elif selected_menu == "⚙️ Manage Requests" and user_data[4] == 'admin':
            st.subheader("⚙️ Manage All Leave Requests")
            st.markdown("*Review and approve/reject leave requests from all employees*")
            
            all_requests = get_all_leave_requests()
            if not all_requests.empty:
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Approved", "Rejected"])
                with col2:
                    dept_filter = st.selectbox("Filter by Department", ["All"] + list(all_requests['department'].unique()))
                with col3:
                    if st.button("🔄 Refresh", use_container_width=True):
                        st.rerun()
                
                # Apply filters
                filtered_requests = all_requests.copy()
                if status_filter != "All":
                    filtered_requests = filtered_requests[filtered_requests['status'] == status_filter.lower()]
                if dept_filter != "All":
                    filtered_requests = filtered_requests[filtered_requests['department'] == dept_filter]
                
                st.markdown(f"**📊 Showing {len(filtered_requests)} of {len(all_requests)} requests**")
                st.markdown("---")
                
                for _, request in filtered_requests.iterrows():
                    status_config = {
                        'pending': {'color': '🟡', 'bg': '#FFF3CD'},
                        'approved': {'color': '🟢', 'bg': '#D4EDDA'},
                        'rejected': {'color': '🔴', 'bg': '#F8D7DA'}
                    }
                    
                    config = status_config.get(request['status'], status_config['pending'])
                    
                    with st.expander(f"{config['color']} **{request['full_name']}** - {request['leave_type']} ({request['start_date']} to {request['end_date']})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**👤 Employee:** {request['full_name']}")
                            st.markdown(f"**🏢 Department:** {request['department']}")
                            st.markdown(f"**📋 Type:** {request['leave_type']}")
                            st.markdown(f"**📊 Status:** {request['status'].title()}")
                        
                        with col2:
                            st.markdown(f"**📅 Start Date:** {request['start_date']}")
                            st.markdown(f"**📅 End Date:** {request['end_date']}")
                            st.markdown(f"**📤 Requested:** {request['request_date']}")
                            
                            # Calculate days
                            start = datetime.strptime(request['start_date'], "%Y-%m-%d").date()
                            end = datetime.strptime(request['end_date'], "%Y-%m-%d").date()
                            total_days = (end - start).days + 1
                            working_days = calculate_working_days(request['start_date'], request['end_date'])
                            st.markdown(f"**⏱️ Duration:** {total_days} total ({working_days} working)")
                        
                        with col3:
                            st.markdown(f"**📝 Reason:** {request['reason']}")
                            
                            if request['status'] == 'pending':
                                st.markdown("**🎯 Actions:**")
                                col_approve, col_reject = st.columns(2)
                                with col_approve:
                                    if st.button(f"✅ Approve", key=f"approve_{request['id']}", use_container_width=True):
                                        update_leave_status(request['id'], 'approved', user_data[1])
                                        st.success("✅ Request approved!")
                                        st.rerun()
                                with col_reject:
                                    if st.button(f"❌ Reject", key=f"reject_{request['id']}", use_container_width=True):
                                        update_leave_status(request['id'], 'rejected', user_data[1])
                                        st.success("❌ Request rejected!")
                                        st.rerun()
                            elif request['approved_by']:
                                st.markdown(f"**✅ Processed by:** {request['approved_by']}")
            else:
                st.info("📭 No leave requests found.")
        
        elif selected_menu == "👥 Team Requests" and user_data[4] == 'manager':
            st.subheader("👥 Team Leave Requests")
            st.markdown(f"*Managing leave requests for {user_data[5]} department*")
            
            team_requests = get_team_leave_requests(user_data[5])
            if not team_requests.empty:
                for _, request in team_requests.iterrows():
                    status_color = {
                        'pending': '🟡',
                        'approved': '🟢',
                        'rejected': '🔴'
                    }.get(request['status'], '⚪')
                    
                    with st.expander(f"{status_color} **{request['full_name']}** - {request['leave_type']} ({request['start_date']} to {request['end_date']})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**👤 Employee:** {request['full_name']}")
                            st.write(f"**📋 Type:** {request['leave_type']}")
                            st.write(f"**📊 Status:** {request['status'].title()}")
                        with col2:
                            st.write(f"**📅 Dates:** {request['start_date']} to {request['end_date']}")
                            st.write(f"**📤 Requested:** {request['request_date']}")
                        with col3:
                            st.write(f"**📝 Reason:** {request['reason']}")
                            
                            if request['status'] == 'pending':
                                col_approve, col_reject = st.columns(2)
                                with col_approve:
                                    if st.button(f"✅ Approve", key=f"approve_{request['id']}"):
                                        update_leave_status(request['id'], 'approved', user_data[1])
                                        st.success("✅ Request approved!")
                                        st.rerun()
                                with col_reject:
                                    if st.button(f"❌ Reject", key=f"reject_{request['id']}"):
                                        update_leave_status(request['id'], 'rejected', user_data[1])
                                        st.success("❌ Request rejected!")
                                        st.rerun()
            else:
                st.info("📭 No team leave requests found.")

if __name__ == "__main__":
    main()
