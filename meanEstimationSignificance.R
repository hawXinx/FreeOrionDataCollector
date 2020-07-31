
# The level of security (the same as throughout the program)
ALPHA = 0.1

# Read the mean values of all games
data = read.csv("meanAndEstimation.csv", sep = ";")
# Calculate the significance border
# Zero-Hypothesis: Mean_normalized = 0.5, Mean = 0
# For the normalized Z: We have to use the standard deviation estimated from the 
# Zero-Hypothesis
zero_hyp_mean = 0.5
std_deviation_normalized = sqrt(zero_hyp_mean * (1 - zero_hyp_mean) / data$Entries)
Z_normalized = (data$Mean_normalized - 0.5) / std_deviation_normalized
# When using non-normalized data, the standard error needs to be used
std_error = (sqrt(data$Variance) / sqrt(data$Entries))
Z = (data$Mean) / std_error

# Two-tailed testing: 
position_distribution_two_sided = qnorm(1-ALPHA / 2, mean = 0, sd = 1)
two_tailed_result_normalized <- abs(Z_normalized) > position_distribution_two_sided
# When using non-normalized data, the T-distribution needs to be taken
position_t_distr_two_sided = qt(1-ALPHA / 2, df = data$Entries - 1)
two_tailed_result <- abs(Z) > position_t_distr_two_sided


# One-tailed test: Zero-Hypothesis: Mean <= 0.5
position_normal_distribution_one_sided = qnorm(1-ALPHA, mean = 0, sd = 1)
one_tailed_result_normalized <- abs(Z_normalized) > position_normal_distribution_one_sided
# When using non-normalized data, the T-distribution needs to be taken
position_t_distr_one_sided = qt(1-ALPHA, df = data$Entries - 1)
one_tailed_result <- abs(Z) > position_t_distr_one_sided

# And now for the p-values (for the eurphoric ones)
p_normalized = 1 - pnorm(abs(Z_normalized))
p = 1 - pt(abs(Z), data$Entries - 1)


# Store the results

data_results = data.frame(data$File, data$Entries, data$Mean, data$Mean_normalized, 
                          data$Variance, data$Variance_normalized, two_tailed_result, 
                          two_tailed_result_normalized, one_tailed_result, 
                          one_tailed_result_normalized, p, p_normalized)
write.table(data_results, file = "meanAndSignificance.csv", sep = ";", row.names = FALSE)
