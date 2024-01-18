import pandas as pd
from datetime import timedelta

def analyze_employee_schedule(file_path):
    # Loaded the excel file into a pandas 
    df = pd.read_excel(file_path)

    #  the excel file has columns 'Position ID', 'Position Status', 'Time', 'Time Out', 'Timecard Hours (as Time)',
    # 'Pay Cycle Start Date', 'Pay Cycle End Date', 'Employee Name', 'File Number'


    # converted 'Time' and 'Time Out' columns to datetime format
    df['Time'] = pd.to_datetime(df['Time'])
    df['Time Out'] = pd.to_datetime(df['Time Out'])

    # converted 'Timecard Hours (as Time)' column to timedelta
    try:
        df['Timecard Hours (as Time)'] = pd.to_timedelta(df['Timecard Hours (as Time)'], errors='coerce')
    except ValueError as e:
        print(f"Error converting 'Timecard Hours (as Time)' to timedelta: {e}")
        return

    # sorted the Dataset by 'Position ID' and 'Time'
    df.sort_values(by=['Position ID', 'Time'], inplace=True)

    # Keep track of processed positions to avoid duplicate output
    processed_positions = set()

    # Iterating through the Data for each position to analyze the schedule
    for index, row in df.iterrows():
        position_id = row['Position ID']

        # Skip if already processed 
        if position_id in processed_positions:
            continue

        position_df = df[df['Position ID'] == position_id]

        # Initialize flags to check if conditions are fulfilled
        worked_14_hours = False
        less_than_10_hours = False
        worked_7_days = False

        # Iterate through the Data for each position to check 
        for _, position_row in position_df.iterrows():
            current_employee = position_row['Employee Name']
            current_hours = position_row['Timecard Hours (as Time)']

            # Check for employees who have worked for 14 hours
            if pd.notna(current_hours) and current_hours > timedelta(hours=14):
                worked_14_hours = True

            # Check for employees with less than 10 hours but greater than 1 hour between shifts
            if less_than_10_hours_between_shifts(position_df, position_row):
                less_than_10_hours = True

            # Check for employees who have worked for 7 consecutive days
            if worked_7_consecutive_days(position_df, position_row):
                worked_7_days = True

        # Producing the final output for each 'Position ID'
        output = f"For Position ID {position_id}: "
        if worked_7_days:
            output += f"{current_employee} worked for 7 consecutive days. "
        elif worked_14_hours:
            output += f"{current_employee} worked for more than 14 hours. "
        elif less_than_10_hours:
            output += f"{current_employee} has less than 10 hours but greater than 1 hour between shifts. "
        
        else :
            output += f"{current_employee} doesn't have proper data. "
        #final output
        print(output)

        # Marked the position as processed
        processed_positions.add(position_id)

def less_than_10_hours_between_shifts(position_df, current_row):
    current_time_out = current_row['Time Out']
    time_between_shifts = position_df[(position_df['Employee Name'] == current_row['Employee Name'])
                                    & (position_df['Time'] > current_time_out - pd.Timedelta(hours=1))
                                    & (position_df['Time'] < current_time_out + pd.Timedelta(hours=10))]
    return not time_between_shifts.empty

def worked_7_consecutive_days(position_df, current_row):
    current_time_in = current_row['Time']
    consecutive_days = position_df[(position_df['Employee Name'] == current_row['Employee Name'])
                                  & (position_df['Time'] >= current_time_in)
                                  & (position_df['Time'] < current_time_in + pd.DateOffset(days=7))]
    return len(consecutive_days) == 7

# storing file name in file_path

file_path = 'Assignment_Timecard.xlsx'
analyze_employee_schedule(file_path)
