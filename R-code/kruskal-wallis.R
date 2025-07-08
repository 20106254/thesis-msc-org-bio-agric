args <- commandArgs(trailingOnly = TRUE)

if(length(args) < 1) {
  stop("Usage: Rscript kruskal-wallace.R <input_csv>")
}

input_file <- args[1]


library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
library(FSA)
library(ggsignif)
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

cluster_labels <- TREATMENT_LABELS
names(cluster_labels) <- cluster_medians$cluster

data_df <- data.frame(data.richness, cluster = as.factor(clusters))
data_df$cluster_label <- factor(cluster_labels[as.character(data_df$cluster)],
                               levels = TREATMENT_LABELS)

kruskal_result <- kruskal.test(species_richness ~ cluster, data = data_df)
print(kruskal_result)

if (kruskal_result$p.value < 0.05) {
  print("Perform post-hoc test")
  dunn_result <- dunnTest(species_richness ~ cluster, data = data_df, method = "bonferroni")
  print(dunn_result)
}
p <- ggplot(data_df, aes(x = cluster_label, y = species_richness)) +
  geom_boxplot(width = 0.6, fill = "lightblue") +
  geom_text(data = cluster_medians,
            aes(x = cluster_labels[as.character(cluster)],
                y = median_richness,
                label = round(median_richness, 1)),
            vjust = -0.5, size = 5, color = "darkred") +
  labs(
    title = "Species Richness by treatment [Survey data]",
    x = "Species Richness Level",
    y = "Species Richness Count"
  ) +
  custom_theme

save_plot(p, "kruskal-wallis.svg")
