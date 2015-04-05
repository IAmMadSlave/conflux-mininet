# Define 2 vectors
udp <- c(0.806, 0.808, 1.04, 1.65, 2.08, 3.30, 4.16, 6.55, 8.32, 13.1, 16.6, 25.9, 31.4, 34.6, 32.6)
tcp <- c(0.959, 1.64, 3.30, 6.56, 13.1, 26.3, 27.5, 30.3, 30.3, 30.3, 30.3, 30.3, 30.3, 30.3, 30.3, 30.3, 30.3, 30.3)

# Graph cars using a y axis that ranges from 0 to 12
plot(udp, type="o", col="blue", ylim=c(0,40))

# Graph trucks with red dashed line and square points
lines(tcp, type="o", pch=22, lty=2, col="red")

# Create a title with a red, bold/italic font
title(main="Loopback Performance", col.main="red", font.main=4)
