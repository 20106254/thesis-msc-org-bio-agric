install.packages("Ellenberg")

library(Ellenberg)

species_df <- read.csv("../datasets/2007-survey-latin.txt")

ellenberg_f <- ellenberg(species_df$Species, indicator = "F")

print(ellenberg_f)
