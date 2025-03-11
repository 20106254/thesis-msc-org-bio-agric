save_plot <- function(plot, filename, width = 10, height = 7, units = "cm") {
  ggsave(filename = filename, plot = plot, width = width, height = height)
  print(paste("Plot saved as:", filename))
}
