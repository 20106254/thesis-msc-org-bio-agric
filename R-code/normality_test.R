args <- commandArgs(trailingOnly = TRUE)

if(length(args) < 1) {
  stop("Usage: Rscript cluster_analysis.R <input_csv>")
}

input_file <- args[1]

library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
source("custom_theme.R")
source("save_plot.R")

# Read and prepare data
data <- read.csv(input_file)

# Aggregate dominance by relevé and species
data.aggregated <- data %>%
  group_by(RELEVE_ID, SPECIES_NAME) %>%
  summarise(DOMIN = sum(DOMIN), .groups = "drop")

# Create community matrix
data.wide <- data.aggregated %>%
  pivot_wider(names_from = SPECIES_NAME, values_from = DOMIN, values_fill = 0)

data.numeric <- data.wide %>%
  select(-RELEVE_ID)

# Fuzzy clustering
membership.exponent <- 1.1
dissimilarity.matrix <- vegdist(data.numeric, method = "bray", memb.exp = membership.exponent)
fanny.result <- fanny(dissimilarity.matrix, k = 3, memb.exp = membership.exponent)
data.wide$FANNY.Cluster <- fanny.result$clustering

# Cluster counts plot
cluster.counts <- table(data.wide$FANNY.Cluster)
plot.data <- as.data.frame(cluster.counts)
colnames(plot.data) <- c("Cluster", "Count")

plot.data$Cluster <- factor(plot.data$Cluster, levels = c(1,2,3), labels = TREATMENT_LABELS)

cluster_plot <- ggplot(plot.data, aes(x = Cluster, y = Count, fill = Cluster)) +
  geom_bar(stat = "identity", color = "black") +
  scale_fill_manual(values = TREATMENT_COLOURS) +
  geom_text(
    aes(label = Count),
    vjust = -0.5,
    size = 5,
    color = "black",
    fontface = "bold"
  ) +
  custom_theme +
  labs(title = "Cluster Assignments", x = "Clusters", y = "No. of relevés")

save_plot(cluster_plot, "cluster_analysis.svg")

# Merge clusters back to original data
data.with.clusters <- data %>%
  left_join(data.wide %>% select(RELEVE_ID, FANNY.Cluster), by = "RELEVE_ID")

# Diagnostic plots ---------------------------------------------------------

# 1. Raw vs. log-transformed distributions
p_raw <- ggplot(data.with.clusters, aes(x = DOMIN)) +
  geom_histogram(bins = 30, fill = "gray70") +
  facet_wrap(~ FANNY.Cluster) +
  labs(title = "Raw Dominance Values", 
       subtitle = "Note: Many small values (0.1) visible at left edge")

p_log <- ggplot(data.with.clusters, aes(x = log10(DOMIN + 0.1))) +
  geom_histogram(bins = 30, fill = "steelblue") +
  facet_wrap(~ FANNY.Cluster) +
  labs(title = "Log-Transformed Values (DOMIN + 0.1)", 
       x = "log10(Dominance + 0.1)")

# 2. Q-Q plots (log-transformed recommended)
qq_plot <- ggplot(data.with.clusters, aes(sample = log10(DOMIN + 0.1))) +
  stat_qq() +
  stat_qq_line(color = "red", linewidth = 1) +
  facet_wrap(~ FANNY.Cluster) +
  labs(title = "Normality Check: Q-Q Plots (log-transformed)",
       subtitle = "Red line = expected normal distribution",
       x = "Theoretical Quantiles",
       y = "Sample Quantiles") +
  custom_theme

# Combine diagnostic plots
diagnostic_plots <- cowplot::plot_grid(
  p_raw, p_log, qq_plot,
  ncol = 1,
  labels = c("A", "B", "C")
)

save_plot(diagnostic_plots, "dominance_diagnostics.svg", width = 8, height = 12)

# Cluster characterization ------------------------------------------------

# Top species per cluster
top_species <- data.with.clusters %>%
  group_by(FANNY.Cluster, SPECIES_NAME) %>%
  summarise(
    Mean_Dominance = mean(DOMIN),
    Frequency = n() / n_distinct(RELEVE_ID),
    .groups = "drop"
  ) %>%
  group_by(FANNY.Cluster) %>%
  slice_max(Mean_Dominance, n = 5) %>%
  arrange(FANNY.Cluster, -Mean_Dominance)

cat("\nTop species per cluster:\n")
print(top_species, n = Inf)

# Summary statistics
cluster_stats <- data.with.clusters %>%
  group_by(FANNY.Cluster) %>%
  summarise(
    Releves = n_distinct(RELEVE_ID),
    Avg_Dominance = mean(DOMIN),
    Median_Dominance = median(DOMIN),
    .groups = "drop"
  )

cat("\nCluster summary statistics:\n")
print(cluster_stats)

# Interpretation guide
cat("\nINTERPRETATION GUIDE:\n")
cat("1. Check cluster_analysis.svg for group sizes\n")
cat("2. View dominance_diagnostics.svg for distribution shapes\n")
cat("3. Top species list shows characteristic taxa per cluster\n")
cat("4. Q-Q plots should follow red line for normality\n")
cat("   - Severe deviations suggest non-normal data\n")
cat("5. For non-normal data, consider:\n")
cat("   - Non-parametric tests (Kruskal-Wallis)\n")
cat("   - Data transformations in downstream analyses\n")
