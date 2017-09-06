rm(list=ls())

library(tidyverse)

setwd('~/insight/manypeoplearesaying/')

clustered.tweets <- read.csv('post_data/tweets_clustered.csv')
head(clustered.tweets)
#table(clustered.tweets$cluster)

ggplot(filter(clustered.tweets, cluster == -1), aes(x = long, y = lat)) +
    geom_point(size=0.1) +
    
    geom_point(data = filter(clustered.tweets, cluster >= 0),
               aes(colour=cluster, x = long, y = lat),
               size=0.1) +
    scale_colour_gradientn(colours = rainbow(5)) +
    
    scale_x_continuous(expand = c(0, 0)) +
    scale_y_continuous(expand = c(0, 0)) +
    theme_bw()

clustered.tweets %>% head
clustered.tweets %>%
    ggplot(aes(x=cluster)) +
    geom_bar(stat='count') +
    coord_cartesian(ylim = c(0, 1000))
