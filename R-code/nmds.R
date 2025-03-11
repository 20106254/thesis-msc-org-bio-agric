library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
source("custom_theme.R")
source("save_plot.R")

data <- read.csv("../python/generated-data-set.csv")

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
data.wide$FANNY.Cluster <- fanny.result$clustering

nmds.result <- metaMDS(data.wide, distance = "bray", k = 3, trymax = 500)
nmds.points <- data.frame(nmds.result$points)
nmds.points$RELEVE_ID <- data.wide$RELEVE_ID
nmds.points$FANNY.Cluster <- as.factor(data.wide$FANNY.Cluster)

p <- ggplot(nmds.points, aes(x = MDS1, y = MDS2, color = FANNY.Cluster, label = RELEVE_ID)) +
  geom_point(size = 0.25) +
  geom_text(aes(label = RELEVE_ID), hjust = 1.5, vjust = 1.5, size = 1) +  
  ggtitle("NMDS Ordination with FANNY Clustering") +
  custom_theme +
  theme(axis.title = element_blank(), axis.text = element_blank(), axis.ticks = element_blank())

save_plot(p, "nmds-generated-data.svg")
