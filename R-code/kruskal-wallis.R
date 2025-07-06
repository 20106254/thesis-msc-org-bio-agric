library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
library(FSA)
library(ggsignif)
source("custom_theme.R")
source("save_plot.R")

data <- read.csv("../datasets/generated-data/generated-data-set.csv")

data.aggregated <- data %>%
  group_by(RELEVE_ID, SPECIES_NAME) %>%
  summarise(DOMIN = sum(DOMIN), .groups = "drop")

data.wide <- data.aggregated %>%
  spread(key = SPECIES_NAME, value = DOMIN, fill = 0)

data.numeric <- data.wide %>%
  select(-RELEVE_ID)

membership.exponent <- 1.1
dissimilarity.matrix <- vegdist(data.numeric, method = "bray", memb.exp = membership.exponent)
fanny.result <- fanny(dissimilarity.matrix, k = 3, memb.exp = membership.exponent)
clusters <- fanny.result$clustering

data.richness <- data.numeric %>%
  rowwise() %>%
  mutate(species_richness = sum(c_across(everything()) > 0))

cluster_medians <- data.frame(cluster = clusters, richness = data.richness$species_richness) %>%
  group_by(cluster) %>%
  summarise(median_richness = median(richness)) %>%
  arrange(median_richness)

cluster_labels <- c("Low", "Medium", "High")
names(cluster_labels) <- cluster_medians$cluster

data_df <- data.frame(data.richness, cluster = as.factor(clusters))
data_df$cluster_label <- factor(cluster_labels[as.character(data_df$cluster)], 
                               levels = c("Low", "Medium", "High"))

kruskal_result <- kruskal.test(species_richness ~ cluster, data = data_df)
print(kruskal_result)

if (kruskal_result$p.value < 0.05) {
  print("p value less than 0.05, so we can do a post-hoc test")
  dunn_result <- dunnTest(species_richness ~ cluster, data = data_df, method = "bonferroni")
  print(dunn_result)
}

p <- ggplot(data_df, aes(x = cluster_label, y = species_richness)) +
  geom_boxplot(width = 0.6, fill = "lightblue") +
  labs(
    title = "Species Richness by Cluster [Generated data set]",
    x = "Species Richness Level",
    y = "Species Richness Count"
  ) +
  custom_theme

save_plot(p, "kruskal-wallis-box-plot.svg")
