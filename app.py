import streamlit as st
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
