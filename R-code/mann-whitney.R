library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
source("save_plot.R")

data <- read.csv("../python/generated-data-set.csv")

data.aggregated <- data %>%
  group_by(RELEVE_ID, SPECIES_NAME) %>%
  summarise(DOMIN = sum(DOMIN), .groups = "drop")

data.wide <- data.aggregated %>%
  spread(key = SPECIES_NAME, value = DOMIN, fill = 0)

data.numeric <- data.wide %>%
  select(-RELEVE_ID) 

dissimilarity.matrix <- vegdist(data.numeric, method = "bray")

fanny.result <- fanny(dissimilarity.matrix, k = 2)

clusters <- fanny.result$clustering

data_df <- data.frame(data.numeric, cluster = clusters)

data.richness <- data.numeric %>%
  rowwise() %>%
  mutate(species_richness = sum(c_across(everything()) > 0))

data_df <- data.frame(data.richness, cluster = clusters)

mann_whitney_result <- wilcox.test(data_df$species_richness ~ data_df$cluster)

print(mann_whitney_result)

svg("mann-whitney-box.svg")
boxplot(data_df$species_richness ~ data_df$cluster, main = "Boxplot of Variable by Cluster", xlab = "Cluster", ylab = "Species Richness")
dev.off()

