import pandas as pd
import random

data = []

for _ in range(500):
    # Generate realistic academic lifestyle values
    sleep = random.randint(3, 9)          # hours per day
    screen = random.randint(1, 8)         # hours per day
    study = random.randint(1, 8)          # hours per day
    attendance = random.randint(50, 100)  # percentage
    stress = random.randint(1, 10)        # self rating (1-10)

    # Burnout Risk Scoring Logic
    score = 0

    if sleep < 5:
        score += 2
    if screen > 6:
        score += 1
    if study > 6:
        score += 1
    if attendance < 65:
        score += 1
    if stress > 7:
        score += 2

    # Controlled randomness to simulate real-world variation
    score += random.choice([0, 0, 1])

    # Assign burnout level based on score
    if score >= 5:
        burnout = "High"
    elif score >= 3:
        burnout = "Medium"
    else:
        burnout = "Low"

    data.append([
        sleep,
        screen,
        study,
        attendance,
        stress,
        burnout
    ])

# Create DataFrame
df = pd.DataFrame(data, columns=[
    "Sleep_Hours",
    "Screen_Time",
    "Study_Hours",
    "Attendance",
    "Stress_Level",
    "Burnout_Level"
])

# Save dataset
df.to_csv("dataset/burnout_data.csv", index=False)

print("Dataset Generated Successfully!")
print("Total Records:", len(df))
print(df.head())
