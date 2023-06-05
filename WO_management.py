import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import base64

def create_work_order():
    with st.form("create form",clear_on_submit=True):
        submitted_by = st.text_input("Submitted by: ")
        department  = st.text_input("Department", st.session_state["k_department"], disabled=True)
        location = st.text_input("Location:")
        equipment = st.text_input("Equipment:")
        description = st.text_area("Description:")
        urgency = st.selectbox("Urgency:",["Low","Medium","High"])

        submit_button = st.form_submit_button(label="Submit")

        # validate user inputs for mandatory fields
        if submit_button and (st.session_state["k_department"]== "" or submitted_by==""):
            st.error("Please fill out the mandatory fields")
        elif submit_button and st.session_state["k_department"] and submitted_by:
            work_order_number = "wo" + str(datetime.timestamp(datetime.now())).replace(".","")[:-3]
            date_submitted = datetime.today().strftime("%Y-%m-%d")

            with sqlite3.connect(r"demo_DB.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO work_orders (work_order_number, date_submitted, submitted_by, department, location, equipment, description, urgency) VALUES(?,?,?,?,?,?,?,?)",
                    (work_order_number, date_submitted, submitted_by, department, location, equipment, description, urgency)
                )
                conn.commit()
                st.success("Work order is created")
                st.write("Work order Number: ", work_order_number)
                #st.write("Date Submitted: ",date_submitted)




def fetch_wo_by_department(department=None):
    with sqlite3.connect(r"demo_DB.db") as conn:
        cursor = conn.cursor()
        if department and department != "":
            cursor.execute(
                "SELECT * FROM work_orders WHERE department = ? order by work_order_number desc", (department,)
            )
        elif department !="":
            cursor.execute(
                "SELECT * FROM work_orders  order by work_order_number desc"
            )
        data = cursor.fetchall()
        if len(data)== 0:
            return pd.DataFrame(
                columns=["Work Order ID",
                         "Date Submitted",
                         "Submitted By",
                         "Department",
                         "LOcation",
                         "Equipment",
                         "Description",
                         "Urgency"]
            )

        df = pd.DataFrame( data,
            columns=["Work Order ID",
                     "Date Submitted",
                     "Submitted By",
                     "Department",
                     "LOcation",
                     "Equipment",
                     "Description",
                     "Urgency"]
        )
        return df


def show_work_orders(department):
   # st.write('fine')
    data = fetch_wo_by_department(department)
    if len(data) > 0:
        st.write(data.to_html(index=False), unsafe_allow_html=True)
        st.write("#")
        st.download_button("Download WOs", data=data.to_csv(index=False),
                           file_name="WorkOrders.csv",
                           mime="str/csv")




def main():

    #Define sidebar
    with st.sidebar:
        st.subheader("Select Department")
        departments = ["","Sales","Marketing","Engineering","Lab Service"]
        department = st.selectbox("Department",departments,key="k_department")

        contain = st.sidebar.container()
        check_show_wo = contain.checkbox("Show Work Orders", key='k_check_show_wo')
        if check_show_wo:
            rd_show_wo = contain.radio("Select your Options: ",options=("By Department", "All WOs"), key="k_rd_show_wo")

    # Define Tabs and tab widgets
    tab1, tab2 = st.tabs(["**Create**:sunglasses:", "**Display**:sunglasses:"])
    with tab1:
            create_work_order()
    with tab2:
        if st.session_state["k_check_show_wo"]:
            if st.session_state["k_rd_show_wo"] == "All WOs":
                st.subheader("Displaying all Work orders")
                show_work_orders(department=None)
            else:
                if st.session_state["k_department"] != "":
                    st.subheader(f"{st.session_state['k_department']} Work Orders")
                    show_work_orders(department=st.session_state['k_department'])



if __name__ == "__main__":
    st.set_page_config(page_title="Work Order App",layout="wide")
    st.title("Work Order Management")

    # Define session variable
    if "k_department" not in st.session_state:
        st.session_state["k_department"] = ''
        st.session_state["k_check_show_wo"] = False
    main()