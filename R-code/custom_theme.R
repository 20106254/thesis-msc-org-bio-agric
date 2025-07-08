library(dplyr)
library(ggthemes)
library(ggplot2)
library(readr)
library(tidyverse)
library(showtext)
library(ggtext)
library(waffle)



font_add_google("Outfit", "title_font")
font_add_google("Cabin", "body_font")
showtext_auto()

TREATMENT_LABELS <- c(
  grazing = "Grazing + fertiliser",
  mowing = "Mowing + fertiliser",
  organic = "Organic Management (Mowing only)"
)

NMDS_LABELS <- c(
  "1" = "Grazing + fertiliser",
  "2" = "Mowing + fertiliser",
  "3" = "Organic Management (Mowing only)"
)

TREATMENT_COLOURS <- c(
  "Grazing + fertiliser" = "#FFA500",      
  "Mowing + fertiliser" = "#FF0000",     
  "Organic Management (Mowing only)" = "#1E90FF"  
)

title_font <- "title_font"
body_font <- "body_font"


title_text <- "Basic Box Plot"
subtitle_text <- "Subtitle"
caption_text <- "Caption"

custom_theme <- theme_minimal() +
    theme(
        axis.title.x = element_text(family = body_font, size=10, margin = margin(t = 10)),
        axis.title.y = element_text(family = body_font, size=10, margin = margin(r = 10)),
        axis.text.x = element_text(family = title_font, size=10),
        axis.text.y = element_text(family = body_font, size=10),
        legend.position = "top",
        legend.title = element_blank(),
        legend.spacing = unit(0.5, 'cm'),
        legend.key.height= unit(0.5, 'cm'),
        legend.key.width= unit(0.7, 'cm'),
        legend.text = element_text(family = body_font, size=13, face = 'plain', color = "grey10"),
        plot.title.position = "plot",
        plot.title = element_textbox(margin = margin(20, 0, 10, 0), size = 20, family = title_font, face = "bold", width = unit(55, "lines")),
        plot.subtitle = element_text(margin = margin(10, 0, 20, 0), size = 16, family = body_font, color = "grey15"),
        plot.caption = element_text(family=body_font, face="plain", size=14, color="grey40", hjust=.5, margin=margin(20,0,0,0)),
        plot.background = element_rect(color="white", fill="white"),
        plot.margin = margin(20, 40, 20, 40)
    )
