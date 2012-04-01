#!/usr/bin/env Rscript
args = commandArgs(T)

# Setup graph, with axis etcetera
pdf(file='precision-recall.pdf',
    pointsize=10,
    width=5,
    height=5)
plot.new()
par(xaxs='i', yaxs='i')
plot.window(c(0, 1), c(0, 1))
axis(side=1)
axis(side=2)
box()
title(main="Precision Recall Graph",
      xlab="Recall",
      ylab="Precision")

# Draw a precision-recall line for every input file
n = 1 # Loop counter
for (filename in args) {
    filename
    data = read.table(filename, header=F, row.names=1)
    precision = vector('numeric', 10)
    precision[1] = data['ircl_prn.0.00',2]
    precision[2] = data['ircl_prn.0.10',2]
    precision[3] = data['ircl_prn.0.20',2]
    precision[4] = data['ircl_prn.0.30',2]
    precision[5] = data['ircl_prn.0.40',2]
    precision[6] = data['ircl_prn.0.50',2]
    precision[7] = data['ircl_prn.0.60',2]
    precision[8] = data['ircl_prn.0.70',2]
    precision[9] = data['ircl_prn.0.80',2]
    precision[10] = data['ircl_prn.0.90',2]
    precision[11] = data['ircl_prn.1.00',2]
    recall = seq(0, 1, 0.1)
    lines(recall, precision, type='o', pch=n)
    n = n + 1
}

# Makes filenames more printable for legend
names = vapply(args,
    function (name) {
        name = basename(name)
        name = sub('-as$', '', name)
        name = gsub('-', ' ', name, fixed=T)
    },
    'character')

legend(.1, 0.95,
       legend=names,
       pch=seq(1, length(args))
       )
