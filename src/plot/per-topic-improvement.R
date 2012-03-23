#!/usr/bin/env Rscript
args = commandArgs(T)
filename1 = args[1]
data1 = read.table(filename1)
filename2 = args[2]
data2 = read.table(filename2)
topics = unique(data1[2])
topics = topics[topics != 'all']
map_diff = vector('numeric')
for (t in topics) {
    map1 = as.numeric(data1[(data1[2] == t) & (data1[1] == 'map')][3])
    map2 = as.numeric(data2[(data2[2] == t) & (data2[1] == 'map')][3])
    map_diff[t] = (map2-map1)
}
map_diff = sort(map_diff, decreasing=T)
pdf(file='diff.pdf',
    width=10,
    height=6,
    fonts=)
par(xaxs='i', yaxs='i', mar=c(2, 4, 2, 2))
labels.xpos = barplot(map_diff,
        axisnames=F,
        main=paste(filename1, " and ", filename2, " MAP Difference"),
        ylim=c(-1, 1),
        ylab=expression(paste(Delta, " MAP")))
labels.ypos = pmax(map_diff, -1)
labels.ypos = pmin(labels.ypos, 1)
text(labels.xpos, labels.ypos, names(map_diff), srt=90, cex=0.9, adj=c(-0.1,0.5))
box()
