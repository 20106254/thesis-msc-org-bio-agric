library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
source("custom_theme.R")
source("save_plot.R")

data <- read.csv("../datasets/site-68-2025/COMBINED_MID_RANGE.csv")
#data <- read.csv("../python/generated-data-set.csv")

data.aggregated <- data %>%
  group_by(RELEVE_ID, SPECIES_NAME) %>%
  summarise(DOMIN = sum(DOMIN), .groups = "drop")

data.wide <- data.aggregated %>%
  spread(key = SPECIES_NAME, value = DOMIN, fill = 0)

data.numeric <- data.wide %>%
  select(-RELEVE_ID) 

membership.exp <- 1.1
dissimilarity.matrix <- vegdist(data.numeric, method = "bray", memb.exp = membership.exp)

fanny.result <- fanny(dissimilarity.matrix, k = 2, memb.exp = membership.exp)
print(fanny.result)

data.wide$FANNY.Cluster <- fanny.result$clustering

nmds.result <- metaMDS(data.wide, distance = "bray", k = 3, trymax = 500)
cat("Stress value:", nmds.result$stress, "\n")
nmds.points <- data.frame(nmds.result$points)
nmds.points$RELEVE_ID <- data.wide$RELEVE_ID
nmds.points$FANNY.Cluster <- as.factor(data.wide$FANNY.Cluster)
print(nmds.points)

p <- ggplot(nmds.points, aes(x = MDS1, y = MDS2)) +
  geom_point(aes(color = FANNY.Cluster), size = 1.5) +
  geom_text(aes(label = RELEVE_ID), hjust = 1.75, vjust = 1.75, size = 2.0, fontface = "bold") +
  ggtitle("NMDS Ordination on generated data set") +
  scale_color_manual(values = c("1" = "red", "2" = "blue"), labels = c("Grazing + Fertiliser", "Organic Management")) +
  custom_theme

save_plot(p, "nmds-generated-data.svg")
