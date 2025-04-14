# Load required packages
library(ggplot2)
library(dplyr)
library(tidyr)
library(svglite)

# 1. Read data from local CSV file
file_path <- "../datasets/site-68-2025/RELEVE_SURVEY.txt"  # Update with your actual file path
df <- read.csv(file_path, stringsAsFactors = FALSE)

# 2. Clean and prepare data
df_clean <- df %>%
  # Convert Domin scores to numeric (handling any non-numeric values)
  mutate(DOMIN = as.numeric(DOMIN)) %>%
  # Remove rows with NA Domin scores
  filter(!is.na(DOMIN)) %>%
  # Convert Relevé ID to factor
  mutate(RELEVE_ID = as.factor(RELEVE_ID))

# 3. Calculate summary statistics by relevé
releve_stats <- df_clean %>%
  group_by(RELEVE_ID) %>%
  summarize(
    Total_Domin = sum(DOMIN, na.rm = TRUE),
    Mean_Domin = mean(DOMIN, na.rm = TRUE),
    Richness = n_distinct(SPECIES_NAME),
    .groups = 'drop'
  )

# 4. Create output directory
if(!dir.exists("graphs")) dir.create("graphs")

# 5. Custom theme for all plots
custom_theme <- theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(size = 14, face = "bold", hjust = 0.5),
    axis.title = element_text(size = 12),
    legend.position = "right",
    panel.grid.minor = element_blank()
  )

# 6. Plot 1: Total Domin per Relevé
ggplot(releve_stats, aes(x = RELEVE_ID, y = Total_Domin, fill = RELEVE_ID)) +
  geom_col(show.legend = FALSE) +
  labs(title = "Total Domin Score by Relevé",
       x = "Relevé ID",
       y = "Total Domin Score") +
  custom_theme +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("graphs/total_domin_by_releve.svg", width = 8, height = 6, device = svglite)

# 7. Plot 2: Species Richness vs Domin
ggplot(releve_stats, aes(x = Richness, y = Total_Domin)) +
  geom_point(size = 3, color = "#66c2a5") +
  geom_smooth(method = "lm", color = "#fc8d62", se = FALSE) +
  labs(title = "Species Richness vs Total Domin Score",
       x = "Number of Species (Richness)",
       y = "Total Domin Score") +
  custom_theme

ggsave("graphs/richness_vs_domin.svg", width = 8, height = 6, device = svglite)

# 8. Plot 3: Domin Distribution by Relevé
ggplot(df_clean, aes(x = RELEVE_ID, y = DOMIN, fill = RELEVE_ID)) +
  geom_boxplot(show.legend = FALSE) +
  labs(title = "Domin Score Distribution by Relevé",
       x = "Relevé ID",
       y = "Domin Score") +
  custom_theme +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("graphs/domin_distribution_by_releve.svg", width = 8, height = 6, device = svglite)

# 9. Calculate site-wide statistics
site_stats <- df_clean %>%
  summarize(
    Site_Total_Domin = sum(DOMIN),
    Site_Mean_Domin = mean(DOMIN),
    Site_Richness = n_distinct(SPECIES_NAME),
    Number_Releves = n_distinct(RELEVE_ID)
  )

# 10. Save site statistics to CSV
write.csv(site_stats, "site_summary_statistics.csv", row.names = FALSE)

# Print summary to console
cat("Site-wide Summary Statistics:\n")
print(site_stats)
