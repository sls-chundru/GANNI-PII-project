# Read CSV File
ev_data <- read.csv("C:/Users/sri/OneDrive/Documents/GitHub/GANNI-PII-project/data-analysis-template-main/Electric_Vehicle_Population_Data.csv")
head(data) # First 6 rows of the data


# Checking for Null values:
total_na <- sum(is.na(ev_data))
print(total_na)

# Removing null values:
ev_data_filtered <- na.omit(ev_data) # FIltered data with NA values removed

# Checking for duplicates:
duplicates <- duplicated(ev_data_filtered) # Check for duplicates
num_duplicates <- sum(duplicates) # Count of duplicates
print(num_duplicates)

#For Electric.Range:
Q1 <- quantile(ev_data_filtered$Electric.Range , 0.25, na.rm = TRUE) # First Quartile
Q3 <- quantile(ev_data_filtered$Electric.Range , 0.75, na.rm = TRUE) # Third Quartile
IQR <- Q3 - Q1 # Compute Interquartile Range
lower_bound <- Q1 - 1.5 * IQR # Compute Lower Bound based on IQR
upper_bound <- Q3 + 1.5 * IQR # Compute Upper Bound based on IQR

# Filter out outliers:
ev_data_Filtered_2 <- ev_data_filtered[ev_data_filtered$Electric.Range > lower_bound & ev_data_filtered$Electric.Range < upper_bound, ]

