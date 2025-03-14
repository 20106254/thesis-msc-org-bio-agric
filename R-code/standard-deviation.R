library(dplyr)
library(ggplot2)
source("save_plot.R")

data <- read.csv("../python/generated-data-set.csv")

std_dev <- data %>%
  group_by(SPECIES_NAME) %>%
  summarise(std_dev = sd(DOMIN, na.rm = TRUE))

print(std_dev)

p <- ggplot(data, aes(x = DOMIN, fill = SPECIES_NAME)) +
  geom_density(alpha = 0.5) +  # Density plot with transparency
  labs(title = "Probability Distribution of DOMIN by Species",
       x = "DOMIN",
       y = "Density") +
  theme_minimal() +
  theme(legend.position = "bottom")  # Move legend to the bottom

save_plot(p, "std-deviation.svg")
