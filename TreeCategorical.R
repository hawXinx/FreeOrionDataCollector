# install.packages("tree")

library(tree)

# To guarantee good treatment
set.seed(1)

# Read the data
data = read.csv("./pruningDataCategorical.csv", sep = ";")
data <- data[data$Turn >= 100, ]
data$X <- NULL

data$Category <- as.factor(data$Category)

# Add additional informations which could be useful (faster comparison)
Planet.comparison = (data$Planet_count_KI_1 - data$Planet_count_KI_6) / 
  (data$Planet_count_KI_1 + data$Planet_count_KI_6 + 1)
Research.comparison = (data$Research_KI_1 - data$Research_KI_6) / (data$Research_KI_1 + data$Research_KI_6 + 1)
Industry.comparison = (data$Industry_KI_1 - data$Industry_KI_6) / (data$Industry_KI_1 + data$Industry_KI_6 + 1)
Ships.comparison = (data$Ships_KI_1 - data$Ships_KI_6) / (data$Ships_KI_1 + data$Ships_KI_6 + 1)
Population.comparison = (data$Population_KI_1 - data$Population_KI_6) / 
  (data$Population_KI_1 + data$Population_KI_6 + 1)

Planet.comparison.abs = (data$Planet_count_KI_1 - data$Planet_count_KI_6)
Research.comparison.abs = (data$Research_KI_1 - data$Research_KI_6)
Industry.comparison.abs = (data$Industry_KI_1 - data$Industry_KI_6)
Ships.comparison.abs = (data$Ships_KI_1 - data$Ships_KI_6)
Population.comparison.abs = (data$Population_KI_1 - data$Population_KI_6)

# Combine all data into one table
comparison = data.frame(data, Planet.comparison, Research.comparison, 
                        Industry.comparison, Ships.comparison, Population.comparison, 
                        Planet.comparison.abs, Research.comparison.abs, Industry.comparison.abs, 
                        Ships.comparison.abs, Population.comparison.abs)

# Calculate the decision tree
tree = tree(Category ~., data=comparison)
# Give back the results
tree$frame
summary(tree)
plot(tree)
text(tree, pretty=0)
