#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = TRUE)

# Get the directory where this script is located
initial_options <- commandArgs(trailingOnly = FALSE)
file_arg_name <- "--file="
script_name <- sub(file_arg_name, "", initial_options[grep(file_arg_name, initial_options)])
script_dir <- dirname(script_name)

# Set default paths if no arguments provided
if (length(args) < 2) {
  input_path <- file.path(dirname(script_dir), "datasets", "site-68-2025", "COMBINED_MID_RANGE.csv")
  output_dir <- file.path(dirname(script_dir), "results")
} else {
  input_path <- args[1]
  output_dir <- args[2]
}

# Load libraries
library(dplyr)
library(tidyr)
library(vegan)
library(ggplot2)
library(cluster)

# Create output directory if it doesn't exist
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# Load custom theme and plotting functions
source(file.path(script_dir, "custom_theme.R"))
source(file.path(script_dir, "save_plot.R"))


# Load and prepare data (NO rare species filtering)
data <- read.csv(input_path) %>%
  group_by(RELEVE_ID, SPECIES_NAME) %>%
  summarise(DOMIN = sum(DOMIN), .groups = "drop") %>%  # Sum dominance per species per relevé
  pivot_wider(
    names_from = SPECIES_NAME, 
    values_from = DOMIN, 
    values_fill = 0  # Fill missing species with 0
  )

# Remove species with TOTAL abundance = 0 (if any)
data.numeric <- data %>%
  select(-RELEVE_ID) %>%
  select(where(~sum(.) > 0)) %>%  # Drop species columns that are all 0
  as.data.frame()
rownames(data.numeric) <- data$RELEVE_ID

empty_releves <- data.numeric[rowSums(data.numeric) == 0, ]
if (nrow(empty_releves) > 0) {
  cat("The following relevés were excluded for having no species data:\n")
  print(rownames(empty_releves))  # Should show RELEVE_IDs like '9'
}

# Hellinger transform (improves handling of zeros)
hel_data <- decostand(data.numeric, "hellinger")

# Fuzzy clustering (k=3) on Bray-Curtis dissimilarity
diss.matrix <- vegdist(hel_data, "bray")
set.seed(123)
fanny.clust <- fanny(diss.matrix, k = 3, memb.exp = 1.2)
data$Management <- c("Grazing + Fertiliser", "Mowing + Fertiliser", "Organic Management")[fanny.clust$clustering]

# NMDS (3D for stability)
set.seed(123)
nmds <- metaMDS(
  hel_data,
  distance = "bray",
  k = 3,
  trymax = 500,
  autotransform = FALSE  # Already Hellinger-transformed
)

cat("Relevés in NMDS results:", rownames(nmds$points), "\n")
cat("Missing relevés:", setdiff(data$RELEVE_ID, rownames(nmds$points)), "\n")
cat("NMDS points for 9", nmds$points["9", ] ,  "\n")
stressplot(nmds)

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

# Create convex hulls
hulls <- plot_data %>%
  group_by(Management) %>%
  slice(chull(MDS1, MDS2))

# Visualization with triangles
cat("Creating visualization...\n")
p <- ggplot(plot_data, aes(x = MDS1, y = MDS2)) +
  geom_polygon(
    data = hulls,
    aes(fill = Management, color = Management),
    alpha = 0.1,
    linewidth = 0.5  # Reduced from 0.7
  ) +
  geom_point(
    aes(color = Management, shape = Management),
    size = 1.5,  # Reduced from 3
    alpha = 0.8
  ) +
  scale_shape_manual(
    values = c(
      "Grazing + Fertiliser" = 17,
      "Mowing + Fertiliser" = 15,
      "Organic Management" = 18
    )
  ) +
  geom_text(
    aes(label = RELEVE_ID),
    hjust = 1.3,  # Adjusted from 1.5
    vjust = 1.3,  # Adjusted from 1.5
    size = 2,     # Reduced from 2.5
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
    title = "NMDS Ordination",
    subtitle = paste0("Stress: ", round(nmds$stress, 3)),
    x = "NMDS1",
    y = "NMDS2",
    shape = NULL,  # Remove legend title
    color = NULL   # Remove legend title
  ) +
  theme_minimal(base_size = 10) +  # Reduced base font size
  theme(
    plot.title = element_text(size = 11, face = "bold", hjust = 0.5),
    plot.subtitle = element_text(size = 10, hjust = 0.5),
    axis.title = element_text(size = 9),
    legend.position = "bottom",
    legend.box = "horizontal",
    legend.spacing.x = unit(0.2, 'cm'),
    legend.key.size = unit(0.4, 'cm'),  # Smaller legend key boxes
    legend.text = element_text(size = 8),  # Smaller legend text
    plot.margin = margin(5, 5, 5, 5, "pt")  # Reduced margins
  ) +
  guides(
    color = guide_legend(nrow = 1),
    shape = guide_legend(nrow = 1),
    fill = "none"  # Hide fill legend (redundant with color)
  )

# Save plot and results
output_plot <- file.path(output_dir, "nmds_plot.svg")
output_data <- file.path(output_dir, "nmds_results.csv")

cat("Saving results to:", output_dir, "\n")
save_plot(p, output_plot)
write.csv(data, output_data, row.names = FALSE)

# Cluster diagnostics
cat("\nCluster sizes:\n")
print(table(data$Management))

# Save metrics
metrics <- list(
  stress_value = nmds$stress,
  n_species = ncol(data.numeric),
  n_releves = nrow(data.numeric),
  cluster_sizes = as.list(table(data$Management))
)

writeLines(
  jsonlite::toJSON(metrics, auto_unbox = TRUE, pretty = TRUE),
  file.path(output_dir, "nmds_metrics.json")
)

cat("\nAnalysis complete. Results saved to:", output_dir, "\n")
