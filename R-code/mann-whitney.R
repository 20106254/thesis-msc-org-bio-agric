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

data.numeric[data.numeric < 0] <- 0 

membership.exponent <- 1.1

dissimilarity.matrix <- vegdist(data.numeric, method = "bray", mem.exp = membership.exponent)

fanny.result <- fanny(dissimilarity.matrix, k = 3, memb.exp = membership.exponent)

data.wide$cluster <- fanny.result$clustering

print(data.wide$cluster)

print(fanny.result$membership)

cluster1_data <- subset(data.wide, cluster == 1)
cluster2_data <- subset(data.wide, cluster == 2)
cluster3_data <- subset(data.wide, cluster == 3)
print("Cluster 1 data")
print(cluster1_data)
print("Cluster 2 data")
print(cluster2_data)
print("Cluster 3 data")
print(cluster3_data)

table(data.wide$cluster)

summary(fanny.result$membership)

p <- ggplot(data, aes(x = RELEVE_ID, y = SPECIES_NAME)) +
  geom_point(size = 3) +
  labs(title = "FANNY Clustering Results", x = "RELEVE_ID", y = "SPECIES_NAME", color = "Cluster") +
  theme_minimal()

save_plot(p, "clusters.svg")

if (length(unique(data.wide$cluster)) > 2) {
  data.subset <- subset(data.wide, cluster %in% c(1, 2)) 
} else {
  data.subset <- data
}

result <- wilcox.test(RELEVE_ID ~ cluster, data = data.subset, exact = FALSE)
print(result)


