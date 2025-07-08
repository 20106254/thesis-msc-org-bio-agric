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

data <- read.csv(input_file)

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

plot.data$Cluster <- factor(plot.data$Cluster, levels = c(1,2,3), labels = TREATMENT_LABELS)

plot <- ggplot(plot.data, aes(x = Cluster, y = Count, fill = Cluster)) +
  geom_bar(stat = "identity", color = "black") +
  scale_fill_manual(values = TREATMENT_COLOURS) + 
  custom_theme +
  labs(title = "Cluster Assignments", x = "Clusters", y = "No. of relevés per cluster")

save_plot(plot, "cluster_analysis.svg")

