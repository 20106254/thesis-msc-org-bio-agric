library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
source("custom_theme.R")
source("save_plot.R")

data <- read.csv("../datasets/generated-data/generated-data-set.csv")
#data <- read.csv("../datasets/site-68-2025/COMBINED_MID_RANGE.csv")

data.aggregated <- data %>%
  group_by(RELEVE_ID, SPECIES_NAME) %>%
  summarise(DOMIN = sum(DOMIN), .groups = "drop")

data.wide <- data.aggregated %>%
  spread(key = SPECIES_NAME, value = DOMIN, fill = 0)

data.numeric <- data.wide %>%
  select(-RELEVE_ID) 

data.numeric[data.numeric < 0] <- 0 

membership.exponent <- 1.1

dissimilarity.matrix <- vegdist(data.numeric, method = "bray", mem.exp = membership.exponent)

fanny.result <- fanny(dissimilarity.matrix, k = 3, memb.exp = membership.exponent)

data.wide$FANNY.Cluster <- fanny.result$clustering

cluster.counts <- table(data.wide$FANNY.Cluster)

plot.data <- as.data.frame(cluster.counts)

colnames(plot.data) <- c("Cluster", "Count")

print(plot.data)

plot.data$Cluster <- factor(plot.data$Cluster, levels = c(1, 2, 3), labels = c("Low species richness", "Medium species richness", "High species richness"))

plot <- ggplot(plot.data, aes(x = Cluster, y = Count, fill = Cluster)) +
  geom_bar(stat = "identity", color = "black") +
  custom_theme +
  labs(title = "Cluster Counts", x = "Clusters", y = "Number of data points")

save_plot(plot, "cluster_analysis_bar_plot_with_membership.svg")

