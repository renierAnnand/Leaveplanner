import streamlit as st
            current_settings = st.session_state.data["settings"]
          
            workweek_start = st.selectbox("Workweek Start", days, 
                                        index=current_settings["workweek"]["start"])
            workweek_end = st.selectbox("Workweek End", days,
                                      index=current_settings["workweek"]["end"])
          
            weekend_bridging = st.checkbox("Enable Weekend Bridging Rule", 
                                         value=current_settings["weekendBridging"])
            exclude_holidays = st.checkbox("Exclude Holidays from Leave Count",
                                         value=current_settings["excludeHolidays"])
          
            if st.button("Update Workweek Settings"):
                current_settings["workweek"]["start"] = days.index(workweek_start)
                current_settings["workweek"]["end"] = days.index(workweek_end)
                current_settings["weekendBridging"] = weekend_bridging
                current_settings["excludeHolidays"] = exclude_holidays
                st.success("Workweek settings updated!")
                st.rerun()
      
        with st.expander("Holiday Management"):
            st.write("Manage public holidays:")
          
            holidays_df = pd.DataFrame(st.session_state.data["holidays"])
            st.dataframe(holidays_df, use_container_width=True)
          
            st.write("Add New Holiday:")
            col1, col2, col3 = st.columns(3)
            with col1:
                new_holiday_date = st.date_input("Holiday Date")
            with col2:
                new_holiday_name = st.text_input("Holiday Name")
            with col3:
                new_holiday_type = st.selectbox("Holiday Type", ["public", "religious", "national"])
          
            if st.button("Add Holiday"):
                if new_holiday_name:
                    new_holiday = {
                        "date": new_holiday_date.strftime("%Y-%m-%d"),
                        "name": new_holiday_name,
                        "type": new_holiday_type
                    }
                    st.session_state.data["holidays"].append(new_holiday)
                    st.success("Holiday added!")
                    st.rerun()

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
        st.session_state.selected_ranges = []
        st.session_state.temp_range_start = None
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
    nav_options.append("Settings")
  
    selected_page = st.sidebar.radio("Go to:", nav_options)
  
    page_mapping = {
        "Dashboard": "dashboard",
        "Plan Leave": "plan_leave", 
        "My Requests": "my_requests",
        "Team View": "team_view",
        "Settings": "settings"
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
    main()
