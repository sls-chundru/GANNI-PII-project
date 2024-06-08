library(data.table)
library(ggplot2)
library(forecast)
library(randomForest)
library(factoextra)
#Load the Data:
data <- fread("household_power_consumption.txt", sep=";", na.strings="?",, nrows=10000)
# Convert Date and Time into POSIXct
#data[, datetime := as.POSIXct(paste(Date, Time), format="%d/%m/%Y %H:%M:%S")]
# Convert other columns to numeric, handling NAs
cols <- c("Global_active_power", "Global_reactive_power", "Voltage", "Global_intensity", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3")
#data[, (cols) := lapply(.SD, as.numeric), .SDcols = cols]

# Remove rows with NA values
data <- na.omit(data)

# Remove outliers based on Global_active_power
qnt <- quantile(data$Global_active_power, probs=c(.25, .75), na.rm = TRUE)
caps <- quantile(data$Global_active_power, probs=c(.01, .99), na.rm = TRUE)
iqr <- IQR(data$Global_active_power)
data <- data[Global_active_power > (qnt[1] - 1.5*iqr) & Global_active_power < (qnt[2] + 1.5*iqr) & Global_active_power >= caps[1] & Global_active_power <= caps[2]]

summary_stats <- summary(data)
print(summary_stats)