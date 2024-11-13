# Import necessary libraries
import streamlit as st
#import pandas as pd
from datetime import datetime, timedelta
#import os

# Set up page configuration
st.set_page_config(page_title="Conference Room Booking", layout="centered")

# Define CSV file for persistent storage
BOOKINGS_FILE = "conference_bookings.csv"

# Load existing bookings from CSV file (or create it if it doesn’t exist)
if os.path.exists(BOOKINGS_FILE):
    bookings_df = pd.read_csv(BOOKINGS_FILE, parse_dates=['Date', 'Start', 'End'])
else:
    # Create an empty DataFrame with necessary columns
    bookings_df = pd.DataFrame(columns=["User", "Date", "Room", "Priority", "Description", "Start", "End"])
    bookings_df.to_csv(BOOKINGS_FILE, index=False)

# Function to save bookings to CSV
def save_bookings(df):
    df.to_csv(BOOKINGS_FILE, index=False)

# Title and description
st.title("Conference Room Booking App")
st.write("Select a date, room, priority level, and your preferred start and end times. You can also provide a description for your booking.")

# Step 1: Date selection
selected_date = st.date_input("Select Booking Date", min_value=datetime.today().date())

# Step 2: Display room, priority, and time selection only if a date is chosen
if selected_date:
    st.write("Now, select an available room, priority level, and specify your preferred times.")

    # Room selection
    room = st.selectbox("Select Room", ["Room A", "Room B", "Room C"])

    # Priority selection
    priority = st.selectbox("Select Priority Level", ["Low", "Medium-Low", "Medium", "Medium-High", "High"])

    # Time selection only appears if a room is selected
    if room:
        # Booking time selection form
        with st.form("booking_form"):
            # Start and end time selection
            selected_start_time = st.time_input("Select Start Time", value=datetime.now().time())
            selected_end_time = st.time_input("Select End Time", value=(datetime.now() + timedelta(hours=1)).time())

            # Combine date and time into datetime objects for start and end
            start_datetime = datetime.combine(selected_date, selected_start_time)
            end_datetime = datetime.combine(selected_date, selected_end_time)

            # User name input
            user_name = st.text_input("Enter Your Name")

            # Description text input
            description = st.text_area("Booking Description (optional)")

            # Submit button within the form
            submit = st.form_submit_button("Book Room")

            # Handle booking submission
            if submit and user_name:
                # Check for conflicts
                conflict = False
                for _, row in bookings_df[(bookings_df['Date'] == pd.Timestamp(selected_date)) & (bookings_df['Room'] == room)].iterrows():
                    existing_start = row['Start']
                    existing_end = row['End']
                    if (start_datetime < existing_end) and (end_datetime > existing_start):
                        conflict = True
                        break
                
                if conflict:
                    st.error("This time slot is already booked. Please select a different time.")
                else:
                    # Add new booking to DataFrame
                    new_booking = pd.DataFrame({
                        "User": [user_name],
                        "Date": [selected_date],
                        "Room": [room],
                        "Priority": [priority],
                        "Description": [description],
                        "Start": [start_datetime],
                        "End": [end_datetime]
                    })
                    bookings_df = pd.concat([bookings_df, new_booking], ignore_index=True)

                    # Save updated bookings to CSV
                    save_bookings(bookings_df)
                    st.success(f"Room {room} successfully booked from {start_datetime.strftime('%Y-%m-%d %H:%M')} to {end_datetime.strftime('%Y-%m-%d %H:%M')}.")

# Step 3: Display user-specific booking records with option to update or delete
st.write("### Your Bookings")

if 'user_name' in locals() and user_name:
    user_bookings = bookings_df[bookings_df["User"] == user_name]
    if not user_bookings.empty:
        # Display user's bookings in a table
        st.write(user_bookings)

        # Update or delete booking
        with st.expander("Update or Delete Bookings"):
            booking_to_modify = st.selectbox("Select Booking to Modify", user_bookings.index)

            if booking_to_modify is not None:
                selected_booking = user_bookings.loc[booking_to_modify]
                
                # Update room, priority, description, and start/end times
                updated_room = st.selectbox("Update Room", ["Room A", "Room B", "Room C"], index=["Room A", "Room B", "Room C"].index(selected_booking['Room']))
                updated_priority = st.selectbox("Update Priority Level", ["Low", "Medium-Low", "Medium", "Medium-High", "High"], index=["Low", "Medium-Low", "Medium", "Medium-High", "High"].index(selected_booking['Priority']))
                updated_description = st.text_area("Update Description", value=selected_booking['Description'])
                updated_start_time = st.time_input("Update Start Time", value=selected_booking['Start'].time())
                updated_end_time = st.time_input("Update End Time", value=selected_booking['End'].time())

                updated_start_datetime = datetime.combine(selected_date, updated_start_time)
                updated_end_datetime = datetime.combine(selected_date, updated_end_time)

                # Buttons to update or delete the booking
                if st.button("Update Booking"):
                    bookings_df.loc[booking_to_modify, 'Room'] = updated_room
                    bookings_df.loc[booking_to_modify, 'Priority'] = updated_priority
                    bookings_df.loc[booking_to_modify, 'Description'] = updated_description
                    bookings_df.loc[booking_to_modify, 'Start'] = updated_start_datetime
                    bookings_df.loc[booking_to_modify, 'End'] = updated_end_datetime
                    save_bookings(bookings_df)
                    st.success("Booking updated successfully.")
                
                if st.button("Delete Booking"):
                    bookings_df = bookings_df.drop(booking_to_modify)
                    save_bookings(bookings_df)
                    st.success("Booking deleted successfully.")
    else:
        st.write("No bookings found.")
