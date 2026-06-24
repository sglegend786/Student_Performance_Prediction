import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

data = {
    'Attendance':[90,85,75,60,95,80,70,88,92,65],
    'Assignment':[85,80,70,60,95,75,65,85,90,55],
    'Internal':[88,82,72,58,96,78,68,84,92,60],
    'Quiz':[80,75,68,55,90,72,60,82,88,50],
    'PreviousMarks':[85,80,70,60,92,75,65,82,90,58],
    'FinalMarks':[87,81,71,59,94,77,66,84,91,57]
}

df = pd.DataFrame(data)

X = df[['Attendance',
        'Assignment',
        'Internal',
        'Quiz',
        'PreviousMarks']]

y = df['FinalMarks']

model = LinearRegression()

model.fit(X, y)

pickle.dump(model,
            open('student_model.pkl', 'wb'))

print("Model Saved Successfully")