#The following docstring descibes the purpose of this script.

"""Calculate student grades by combining data from many sources.

Using Pandas, this script combines data from the:

* Roster
* Homework & Exam grades
* Quiz grades

to calculate final grades for a class.
"""

#1). DATA NEEDS TO BE LOADED.

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats

#Two constants, HERE and DATA_FOLDER, will keep track of the currently executing file. Also, where the folder where the data's stored.
HERE = Path(__file__).parent #To get the parent directory of the directory containing the script (regardless of the current working directory), you will need to use __file__.. .parent refers to the parent directory.
DATA_FOLDER = HERE / "data"

roster = pd.read_csv( #Read  comma-separated values roster file.
    DATA_FOLDER / "roster.csv",
    converters={"NetID": str.lower, "Email Address": str.lower}, #Convert all charactes to lowercase to compare strings.
    usecols=["Section", "Email Address", "NetID"], #Return a subset of columns
    index_col="NetID", #Use NetID column as index.
)

hw_exam_grades = pd.read_csv( 
    DATA_FOLDER / "hw_exam_grades.csv", #Read the comma-separated hw_exam_grades file from DATA_FOLDER
    converters={"SID": str.lower}, #Convert all SID characters to lowercase.
    usecols=lambda x: "Submission" not in x, #Ignore the submission times columns.
    index_col="SID", #SID is declared as the index column to match the roster Dataframe.
)

quiz_grades = pd.DataFrame() #Create an empty DataFrame called quiz_grades.
for file_path in DATA_FOLDER.glob("quiz_*_grades.csv"): #All quiz CSV files will be found and loaded with pandas.
    quiz_name = " ".join(file_path.stem.title().split("_")[:2])
    quiz = pd.read_csv( #Read comma-separated quiz_*_grades files.
        file_path,
        converters={"Email": str.lower}, #Converter all Email characters to lowercase.
        index_col=["Email"],  #Use Email column as index.
        usecols=["Email", "Grade"],
    ).rename(columns={"Grade": quiz_name}) #Name of Grade column changed to Quiz 1, 2, 3, 4, 5, etc.
    quiz_grades = pd.concat([quiz_grades, quiz], axis = 1) #Axis=1 is passed to pd.concat(), meaning that pandas will concatenate columns instead of rows.
#In addition, each new quiz will be added to its own column.

#END THE LOADING OF DATA.

#2). MERGING THE DATAFRAMES

#Data from all three dataframes can now be combined.

final_data = pd.merge( #pd.merge() combines both the roster and hw_exam_grades DataFrames
    roster,
    hw_exam_grades,
    left_index=True, #Use the left index (roster) and the right index(hw_exam_grades).
    right_index=True,
)
final_data = pd.merge(  #pd.merge() combines both final_data and guiz_grades DataFrames.
    final_data, quiz_grades, left_on="Email Address", right_index=True #Use the Email Address column from the final_data DataFrame, and use the quiz_grades DataFrame.
)
final_data = final_data.fillna(0) #This will assign a number to all nan values in the final_data DataFrame.

#3). CALCULATING GRADES

#Exams, Homework, and Quizzes are assinged a weight toward each student's final score.

#By multiplying the weight by the total score from all three categories, and summing the values, you can calculate the final score. Then, each final score is converted to a letter grade.

#A for loop will be used to calculate the total score for each individual exam.

n_exams = 3 #n_exams = 3 exams
for n in range(1, n_exams + 1):
    final_data[f"Exam {n} Score"] = (
        final_data[f"Exam {n}"] / final_data[f"Exam {n} - Max Points"]
    )
#Each exam will be looped through to calculate the score by dividing  the raw score by the max points for that exam.

homework_scores = final_data.filter(regex=r"^Homework \d\d?$", axis = 1) #final_data.filter collects all the columns with homework data.
homework_max_points = final_data.filter(regex=r"^Homework \d\d? -", axis = 1) #Regex filters final_data. Column names that don't match the regex won't be included in the DataFrame.
#Axis = 1 passes through the final_data.filter(), which tells it to look for all columns that match the regex.

sum_of_hw_scores = homework_scores.sum(axis = 1) #homework_scores.sum will add up all the values for all the rows in each column due to axis = 1.
sum_of_hw_max = homework_max_points.sum(axis = 1) #The same as above.
final_data["Total Homework"] = sum_of_hw_scores / sum_of_hw_max #A new column called "Total Homework" is added to final_data.
#Then, sum_of_hw_scores is divided by sum_of_hw_max to determine the Total Homework Scores.

hw_max_renamed = homework_max_points.set_axis(homework_scores.columns, axis = 1) #homework_max_points.set_axis() changes the column names for homework_max_points to match the names in homework_scores.
#A new DataFrame called hw_max_renamed is created, and the axis is set to the columns in order to have the same names as the columns in homework_scores.
average_hw_scores = (homework_scores / hw_max_renamed).sum(axis = 1)
#The average_hw_scores is calculated by dividing homework_scores by hw_max_renamed.
#Then, the sum is determined by adding the ratios together for all homework in each row with .sum and axis = 1.
final_data["Average Homework"] = average_hw_scores / homework_scores.shape[1]
#Average_hw_scores is divided by homework_scores.shape[1]
#homework_scores.shape gets the number of assignments for homework_scores.
#homework_scores.shape will return a tuple of (n_rows, n_columns).
#The second value will be taken from the tuple, which gives you the number of columns in homework_scores. This is eqal to the number of assigments.
#Afteer that, the result of the division is assigned to a new column in final_data called Average Homework.

final_data["Homework Score"] = final_data[
    ["Total Homework", "Average Homework"]
].max(axis = 1)
#The two columns created above are selected, and the maximum value is assigned to a new column called Homework Score.
#The maximum for each student is taken with axis = 1

quiz_scores = final_data.filter(regex=r"^Quiz \d$", axis = 1)
quiz_max_points = pd.Series( #A pandas series is created to hold information since the maximum grade on each quiz isn't specified in the quiz data tables.
    {"Quiz 1": 11, "Quiz 2": 15, "Quiz 3": 17, "Quiz 4": 14, "Quiz 5": 12} #The keys of the dictionary become index labels and dictionary values become the Series values.
)

sum_of_quiz_scores = quiz_scores.sum(axis = 1)
sum_of_quiz_max = quiz_max_points.sum()
final_data["Total Quizzes"] = sum_of_quiz_scores / sum_of_quiz_max

average_quiz_scores = (quiz_scores / quiz_max_points).sum(axis = 1)
final_data["Average Quizzes"] = average_quiz_scores / quiz_scores.shape[1]

final_data["Quiz Score"] = final_data[
    ["Total Quizzes", "Average Quizzes"]
].max(axis = 1)

#All calculations for the final grade are now completed.

#The weightings are given to each compoent of the class.
weightings = pd.Series(
    {
        "Exam 1 Score": 0.05,
        "Exam 2 Score": 0.1,
        "Exam 3 Score": 0.15,
        "Quiz Score": 0.30,
        "Homework Score": 0.4,
    }
)

final_data["Final Score"] = (final_data[weightings.index] * weightings).sum( #The columns with the same names as the index in weights are selected.
    axis = 1 #Take the sum of the columns for each student with (final_data[weightings.index] * weightings).sum(axis = 1), and assign the result of this to a new column called Final Score.
)
final_data["Ceiling Score"] = np.ceil(final_data["Final Score"] * 100)
#Round each students grade up by multiplying each Final Score by 100 to put it on a scale from 0 to 100.
#Use np.ceil() to round each score to the next highest integer.
#The value is assigned to a new column called Ceiling Score.

#Now each ceiling score will be mapped onto a letter grade.

grades = { #This dictionary stores the mapping between lower limit of each letter grade and the letter.
    90: "A",
    80: "B",
    70: "C",
    60: "D",
    0: "F",
}

def grade_mapping(value): #Defined grade_mapping, which takes as an argument the value of a row from the ceiling score Series.
    for key, letter in grades.items(): #For loop over the items in grades to compare value to the key from the dictionary.
        if value >= key: #If the value is greather than or equal to the key, then the student falls in the bracket and the appropriate lettter grade is returned.
            return letter

letter_grades = final_data["Ceiling Score"].map(grade_mapping) #Letter_grades is created by mapping grade_mapping() onto the ceiling score column from final_data.
final_data["Final Grade"] = pd.Categorical( #Create a categorical colunn called Final Grade
    letter_grades, categories = grades.values(), ordered = True
)

#END CALCULATING GRADES

#4). GROUPING THE DATA

#Each student will be separated intedo each section and sorted by their last name, to put the grades into the student adminitration system.

#The following code will group the data by the students' section number and sort the grouped result by their name.

for section, table in final_data.groupby("Section"): #final_data.groupby is used to group by the Section column.
    section_file = DATA_FOLDER / f"section {section} Grades.csv" #Section file will pull section from the Grades.csv
    num_students = table.shape[0]
    print(
        f"In Section {section} there are {num_students} students saved to "
        f"file {section_file}."
    )
    table.sort_values(by=["Last Name", "First Name"]).to_csv(section_file) #table.sort_values will sort the grouped results.
    #The sorted data is saved to a CSV file.

#END GROUPING THE DATA

#5). PLOTTING SUMMARY STATISTICS

#The following code will let you see a distribution of the letter grades in the class.

grade_counts = final_data["Final Grade"].value_counts().sort_index() #final_data["Final Grade"].value_counts() will be used on the Final Grade column in final_data to calculate how many of each of the letters appear.
#Series.sort_index() is used to sort the grades into the order that is specified when  the Categorical column wsa defined.
grade_counts.plot.bar()  #This will use Matplotlib and produce a bar plot of the grade counts. 
plt.show() #The plot will be shown.

#Next, we will plot a histopgram.
final_data["Final Score"].plot.hist(bins=20, label="Histogram") #final_data["Final Score"].plot.hist() is used to plot a histogram of the final scores.
final_data["Final Score"].plot.density( #final_data["Final Score"].plot.density() is used from the SciPy library to calculate a kernel density estimate.
    linewidth=4, label="Kernel Density Estimate"
)

#You can guess that the data will be normally distributed and manually calculate a normal distribution with the mean and standard deviation from ryour cata.

final_data["Final Score"].plot.density( #This will plot the kernel density estimate for the date
    linewidth=4, label="Kernel Density Estimate"
)

final_mean = final_data["Final Score"].mean()#The mean and standard deviation of your Final Score data are calculated using DataFrame.mean() and DataFrame.std().
final_std = final_data["Final Score"].std()
x = np.linspace(final_mean - 5 * final_std, final_mean + 5 * final_std, 200) #np.linespace() is used to generate a set of x-values from -5 to +5 standard deviations away from the mean.
normal_dist = scipy.stats.norm.pdf(x, loc=final_mean, scale=final_std) #normal_dist is calculated by plugging into the formula for the standard normal distribution.
plt.plot(x, normal_dist, label="Normal Distribution", linewidth=4) #plot x VS normal_dist and adjust the line width and add a label.
plt.legend()
plt.show()