
library(ggplot2)
library(dplyr)
source("custom_theme.R")
source("save_plot.R")

data <- read.csv("../python/generated-data-set.csv")

data$Group <- case_when(
  data$RELEVE_ID %in% 1:20 ~ "Intensive Management",
  data$RELEVE_ID %in% 21:60 ~ "Traditional Management",
)

species_richness <- data %>%
  group_by(Group, RELEVE_ID) %>%
  summarise(Species_Richness = n_distinct(SPECIES_NAME)) %>%
  ungroup()  


summary_stats <- species_richness %>%
  group_by(Group) %>%
  summarise(
    Mean_Richness = mean(Species_Richness),
    Median_Richness = median(Species_Richness),
    Q1 = quantile(Species_Richness, 0.25),
    Q3 = quantile(Species_Richness, 0.75),
    Min_Richness = min(Species_Richness),
    Max_Richness = max(Species_Richness),
    SD_Richness = sd(Species_Richness)
  )


print(summary_stats)


p <- ggplot(species_richness, aes(x = Group, y = Species_Richness)) +
  geom_boxplot(fill = "lightblue", color = "black") +
  geom_jitter(width = 0.2, color = "red", alpha = 0.5) +
  labs(title = "Species Richness per Group (IM, TM)",
       x = "Group",
       y = "Species Richness") +
   custom_theme

save_plot(p, "species_richness_per_group.svg")


