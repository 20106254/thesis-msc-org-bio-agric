library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
source("custom_theme.R")
source("save_plot.R")

# Load data
data <- read.csv("../datasets/site-68-2025/COMBINED_MID_RANGE.csv")

# Data processing with complete cases
data.aggregated <- data %>%
  group_by(RELEVE_ID, SPECIES_NAME) %>%
  summarise(DOMIN = sum(DOMIN), .groups = "drop") %>%
  complete(RELEVE_ID, SPECIES_NAME, fill = list(DOMIN = 0))

# Create wide format
data.wide <- data.aggregated %>%
  pivot_wider(names_from = SPECIES_NAME, values_from = DOMIN)

# Prepare numeric matrix (ensure no NAs)
data.numeric <- data.wide %>%
  select(-RELEVE_ID) %>%
  mutate(across(everything(), ~replace(., is.na(.), 0)))

# Clustering
dissimilarity.matrix <- vegdist(data.numeric, method = "bray")
fanny.result <- fanny(dissimilarity.matrix, k = 3, memb.exp = 1.1)

# Add clusters to data
data.wide$FANNY.Cluster <- fanny.result$clustering

# Create and save cluster count plot (YOUR ORIGINAL METHOD)
cluster.counts <- table(data.wide$FANNY.Cluster)
plot.data <- as.data.frame(cluster.counts)
colnames(plot.data) <- c("Cluster", "Count")

print(plot.data)

plot.data$Cluster <- factor(plot.data$Cluster, 
                           levels = c(1, 2, 3), 
                           labels = c("Low species richness", 
                                     "Medium species richness", 
                                     "High species richness"))

plot <- ggplot(plot.data, aes(x = Cluster, y = Count, fill = Cluster)) +
  geom_bar(stat = "identity", color = "black") +
  custom_theme +
  labs(title = "Cluster Counts", 
       x = "Clusters", 
       y = "Number of data points") +
  geom_text(aes(label = Count), vjust = -0.5)  # Add count labels

# Save plot using your original function
save_plot(plot, "cluster_analysis_bar_plot_with_membership.svg")

# Additional diagnostics
cat("\nCluster quality metrics:\n")
print(summary(silhouette(fanny.result$clustering, dissimilarity.matrix)))
cat("\nAverage membership strength:", 
    mean(apply(fanny.result$membership, 1, max)), "\n")
