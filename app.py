import streamlit as st
  
    # Team calendar overview
    st.markdown("---")
    st.subheader("📅 Team Leave Calendar")
  
    approved_requests = [req for req in st.session_state.data["leaveRequests"].values() 
                        if req["status"] == "approved" and 
                        req["employeeId"] in [member["id"] for member in team_members]]
  
    if approved_requests:
        calendar_data = []
        for req in approved_requests:
            employee = st.session_state.data["users"][req["employeeId"]]
            for range_data in req["ranges"]:
                calendar_data.append({
                    "Employee": employee["name"],
                    "Department": employee["department"],
                    "Start Date": range_data["start"],
                    "End Date": range_data["end"],
                    "Leave Type": req["type"].title(),
                    "Days": req["daysCalculation"]["totalDeducted"]
                })
      
        df = pd.DataFrame(calendar_data)
        st.dataframe(df, use_container_width=True)
      
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Approved Leaves", len(approved_requests))
        with col2:
            total_days = sum(req["daysCalculation"]["totalDeducted"] for req in approved_requests)
            st.metric("Total Days Approved", total_days)
        with col3:
            departments = len(set(st.session_state.data["users"][req["employeeId"]]["department"] 
                                for req in approved_requests))
            st.metric("Departments Affected", departments)
    else:
        st.info("No approved leaves to display.")

def approve_request(request_id, comments):
    """Approve a leave request"""
    req = st.session_state.data["leaveRequests"][request_id]
    employee = st.session_state.data["users"][req["employeeId"]]
  
    # Update request status
    req["status"] = "approved"
    req["managerComments"] = comments
    req["approvedBy"] = st.session_state.current_user
    req["approvedAt"] = datetime.now().isoformat()
  
    # Update employee balance
    employee["leaveBalance"][req["type"]]["used"] += req["daysCalculation"]["totalDeducted"]
    employee["leaveBalance"][req["type"]]["pending"] -= req["daysCalculation"]["totalDeducted"]

def reject_request(request_id, comments):
    """Reject a leave request"""
    req = st.session_state.data["leaveRequests"][request_id]
    employee = st.session_state.data["users"][req["employeeId"]]
  
    # Update request status
    req["status"] = "rejected"
    req["managerComments"] = comments
    req["approvedBy"] = st.session_state.current_user
    req["approvedAt"] = datetime.now().isoformat()
  
    # Return pending balance
    employee["leaveBalance"][req["type"]]["pending"] -= req["daysCalculation"]["totalDeducted"]

def render_settings():
    """Render settings page"""
    st.title("⚙️ Settings")
  
    user = st.session_state.data["users"][st.session_state.current_user]
  
    # Personal Settings
    st.subheader("👤 Personal Settings")
  
    with st.expander("Leave Balance Management"):
        st.write("Update your annual leave balance:")
      
        for leave_type in st.session_state.data["settings"]["leaveTypes"]:
            current_balance = user["leaveBalance"].get(leave_type["id"], {"total": 0, "used": 0, "pending": 0})
          
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{leave_type['name']}**")
            with col2:
                new_total = st.number_input(
                    f"Total {leave_type['name']} Days",
                    min_value=0,
                    value=current_balance["total"],
                    key=f"balance_{leave_type['id']}"
                )
              
                if new_total != current_balance["total"]:
                    if st.button(f"Update {leave_type['name']}", key=f"update_{leave_type['id']}"):
                        user["leaveBalance"][leave_type["id"]]["total"] = new_total
                        st.success(f"{leave_type['name']} balance updated!")
                        st.rerun()
  
    # System Settings (Admin only)
    if user["role"] == "admin":
        st.markdown("---")
        st.subheader("🔧 System Settings")
      
        with st.expander("Workweek Configuration"):
            st.write("Configure the standard workweek:")
          
            days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            current_settings = st.session_state.data["settings"]
          
            workweek_start = st.selectbox("Workweek Start", days, 
                                        index=current_settings["workweek"]["start"])
            workweek_end = st.selectbox("Workweek End", days,
                                      index=current_settings["workweek"]["end"])
          
            weekend_bridging = st.checkbox("Enable Weekend Bridging Rule", 
                                         value=current_settings["weekendBridging"])
            exclude_holidays = st.checkbox("Exclude Holidays from Leave Count",
                                         value=current_settings["excludeHolidays"])
    main()
