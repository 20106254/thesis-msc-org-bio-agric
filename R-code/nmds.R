args <- commandArgs(trailingOnly = TRUE)

if(length(args) < 1) {
  stop("Usage: Rscript nmds_analysis.R <input_csv>")
}

input_file <- args[1]

options(showtext.opts = list(dpi = 96, device = "pdf")) 

options(ragg.use_downloadable_fonts = FALSE)  

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

dissimilarity.matrix <- vegdist(data.numeric, method = "bray", memb.exp = membership.exponent)

fanny.result <- fanny(dissimilarity.matrix, k = 3, memb.exp = membership.exponent)

data.wide$FANNY.Cluster <- fanny.result$clustering

nmds.result <- metaMDS(data.wide, 
                       distance = "bray", 
                       k = 3, 
                       trymax = 500, 
                       memb.exp = membership.exponent)

print(nmds.result)
cat("Stress value:", nmds.result$stress, "\n")
nmds.points <- data.frame(nmds.result$points)
nmds.points$RELEVE_ID <- data.wide$RELEVE_ID
nmds.points$FANNY.Cluster <- as.factor(data.wide$FANNY.Cluster)
print(nmds.points)

p <- ggplot(nmds.points, aes(x = MDS1, y = MDS2)) +
  geom_point(aes(color = FANNY.Cluster), size = 1.5) +
  geom_text(aes(label = RELEVE_ID), hjust = 1.75, vjust = 1.75, size = 2.0, fontface = "bold") +
  labs(
    title = "NMDS Ordination of Survey Data",
    subtitle = sprintf("Stress  %.5f", nmds.result$stress), 
    x = "MDS1",
    y = "MDS2"
  ) +
  scale_color_manual(values = c("1" = "#FFA500", "2" = "#FF0000", "3" = "#1E90FF"), labels = NMDS_LABELS) +
  custom_theme

save_plot(p, "nmds-ordination.svg")
