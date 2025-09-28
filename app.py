import streamlit as st
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
                if req['daysCalculation']['bridgeDays'] > 0:
                    st.write(f"**Bridge Days:** {req['daysCalculation']['bridgeDays']}")
                st.write(f"**Reason:** {req['reason']}")
          
            st.write("**Date Ranges:**")
            for range_data in req["ranges"]:
                st.write(f"• {range_data['start']} to {range_data['end']}")
          
            if req.get("managerComments"):
                st.info(f"**Manager Comments:** {req['managerComments']}")
          
            # Actions based on status
            if req["status"] == "draft":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_{req['id']}"):
                        # Load request data for editing
                        st.session_state.selected_ranges = req["ranges"].copy()
                        st.session_state.page = "plan_leave"
                        st.rerun()
                with col2:
                    if st.button(f"📤 Submit", key=f"submit_{req['id']}"):
                        req["status"] = "pending"
                        user = st.session_state.data["users"][st.session_state.current_user]
                        user["leaveBalance"][req["type"]]["pending"] += req["daysCalculation"]["totalDeducted"]
                        st.success("Request submitted for approval!")
                        st.rerun()

def render_team_view():
    """Render manager's team view"""
    st.title("👥 Team View")
  
    if st.session_state.data["users"][st.session_state.current_user]["role"] not in ["manager", "admin"]:
        st.error("Access denied. Manager role required.")
        return
  
    # Get team members
    current_user = st.session_state.data["users"][st.session_state.current_user]
    if current_user["role"] == "admin":
        team_members = list(st.session_state.data["users"].values())
    else:
        team_members = [user for user in st.session_state.data["users"].values() 
                       if user.get("manager") == st.session_state.current_user]
  
    # Pending approvals
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
                    if req['daysCalculation']['bridgeDays'] > 0:
                        st.write(f"**Bridge Days:** {req['daysCalculation']['bridgeDays']} 🌉")
              
                st.write("**Date Ranges:**")
                for range_data in req["ranges"]:
                    st.write(f"• {range_data['start']} to {range_data['end']}")
              
                # Manager actions
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
              
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{req['id']}"):
                        approve_request(req["id"], "")
                        st.success("Request approved!")
                        st.rerun()
              
                with col2:
                    if st.button(f"❌ Reject", key=f"reject_{req['id']}"):
                        st.session_state.rejecting_request = req["id"]
              
                with col3:
                    if st.button(f"✏️ Amend", key=f"amend_{req['id']}"):
                        st.session_state.amending_request = req["id"]
              
                # Handle rejection
                if st.session_state.get("rejecting_request") == req["id"]:
                    with st.form(f"reject_form_{req['id']}"):
                        rejection_reason = st.text_area("Reason for rejection:")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.form_submit_button("Confirm Rejection"):
                                reject_request(req["id"], rejection_reason)
                                st.session_state.rejecting_request = None
    main()