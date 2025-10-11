# Simple convolution-like demonstration
image = [[3, 3, 2, 0],
         [0, 0, 1, 1],
         [3, 2, 2, 2],
         [0, 0, 1, 3]]

kernel = [[1, 0],
          [0, -1]]

output = []
for i in range(3):
    row = []
    for j in range(3):
        val = (image[i][j]*kernel[0][0] + image[i][j+1]*kernel[0][1] +
               image[i+1][j]*kernel[1][0] + image[i+1][j+1]*kernel[1][1])
        row.append(val)
    output.append(row)

print("Detected lane edges:", output)
