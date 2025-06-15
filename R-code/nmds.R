library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)
source("custom_theme.R")
source("save_plot.R")

# Load and prepare data
data <- read.csv("../datasets/site-68-2025/COMBINED_MID_RANGE.csv") %>%
  group_by(RELEVE_ID, SPECIES_NAME) %>%
  summarise(DOMIN = sum(DOMIN), .groups = "drop") %>%
  group_by(SPECIES_NAME) %>%
  filter(sum(DOMIN > 0) >= 3) %>%  # Remove rare species (<5 occurrences)
  ungroup() %>%
  pivot_wider(names_from = SPECIES_NAME, values_from = DOMIN, values_fill = 0)

# Remove zero-variance species and empty samples
data.numeric <- data %>%
  select(-RELEVE_ID) %>%
  select(where(~sum(.) > 0)) %>%
  as.data.frame()
rownames(data.numeric) <- data$RELEVE_ID

# Hellinger-transformed Bray-Curtis dissimilarity
diss.matrix <- vegdist(decostand(data.numeric, "hellinger"), "bray")

# Fuzzy clustering (k=3)
set.seed(123)
fanny.clust <- fanny(diss.matrix, k = 3, memb.exp = 1.2)
data$Management <- c("Grazing + Fertiliser", "Mowing + Fertiliser", "Organic Management")[fanny.clust$clustering]

# NMDS (3D for better stress)
set.seed(123)
nmds <- metaMDS(
  decostand(data.numeric, "hellinger"),
  distance = "bray",
  k = 3,
  trymax = 500,
  autotransform = FALSE
)
cat("Final stress:", nmds$stress, "\n")

# Prepare plot data
plot_data <- data.frame(
  MDS1 = nmds$points[,1],
  MDS2 = nmds$points[,2],
  Management = factor(data$Management,
                     levels = c("Grazing + Fertiliser", 
                              "Mowing + Fertiliser", 
                              "Organic Management")),
  RELEVE_ID = data$RELEVE_ID
)

# Create convex hulls (more stable than ellipses)
hulls <- plot_data %>%
  group_by(Management) %>%
  slice(chull(MDS1, MDS2))

# Visualization
p <- ggplot(plot_data, aes(x = MDS1, y = MDS2)) +
  geom_polygon(
    data = hulls,
    aes(fill = Management, color = Management),
    alpha = 0.1,
    linewidth = 0.7
  ) +
  geom_point(
    aes(color = Management),
    size = 2.5,
    alpha = 0.8
  ) +
  geom_text(
    aes(label = RELEVE_ID),
    hjust = 1.5,
    vjust = 1.5,
    size = 2.5,
    check_overlap = TRUE
  ) +
  scale_color_manual(
    values = c(
      "Grazing + Fertiliser" = "#E41A1C",
      "Mowing + Fertiliser" = "#377EB8",
      "Organic Management" = "#4DAF4A"
    )
  ) +
  scale_fill_manual(
    values = c(
      "Grazing + Fertiliser" = "#E41A1C",
      "Mowing + Fertiliser" = "#377EB8",
      "Organic Management" = "#4DAF4A"
    )
  ) +
  labs(
    title = "NMDS of Grassland Management Approaches",
    subtitle = paste("Stress =", round(nmds$stress, 3)),
    x = "NMDS Axis 1",
    y = "NMDS Axis 2"
  ) +
  custom_theme +
  theme(legend.position = "right")

# Save plot
save_plot(p, "nmds_three_management_types.svg")

# Cluster diagnostics
cat("\nCluster sizes:\n")
print(table(data$Management))
