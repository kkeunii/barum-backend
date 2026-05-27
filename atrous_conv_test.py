import torch

def atrous_conv(kernel: torch.Tensor, dilation: int) -> torch.Tensor:
    # kernel shape: (out_channels, in_channels, kernel_height, kernel_width)
    out_c, in_c, k, _ = kernel.shape
    # when applying dilation, the effective kernel size becomes: k + (k - 1) * (dilation - 1)
    k_dil = k + (k - 1) * (dilation - 1)
    # create a kernel filled with zeros for the dilated kernel size
    dilated_kernel = torch.zeros((out_c, in_c, k_dil, k_dil), dtype=kernel.dtype)
    # place original kernel values into the dilated kernel at intervals of `dilation`
    # step by dilation along height and width dimensions
    dilated_kernel[:, :, ::dilation, ::dilation] = kernel
    return dilated_kernel

# Test input: a single 2x2 kernel with batch size 1 and input channel 1
kernel = torch.tensor([[[[1, 2],
                         [3, 4]]]], dtype=torch.float32)

# Expected dilated kernel shape: (1, 1, 3, 3) when dilation=2
# because a 2x2 kernel with dilation 2 inserts one zero row/column between elements

# run the atrous convolution dilation transform
dilated = atrous_conv(kernel, dilation=2)

print("Original kernel shape:", kernel.shape)
print("Dilated kernel shape:", dilated.shape)
print(dilated)
