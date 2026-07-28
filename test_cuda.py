import torch
import time

print("="*60)
print("CUDA TEST")
print("="*60)

if not torch.cuda.is_available():
    print("❌ CUDA not available!")
    print("Try installing with:")
    print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    exit(1)

device = torch.device('cuda')
print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
print(f"✅ Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

# Simple test
print("\nRunning simple test...")
a = torch.randn(1000, 1000).cuda()
b = torch.randn(1000, 1000).cuda()

start = time.time()
c = torch.mm(a, b)
torch.cuda.synchronize()
elapsed = time.time() - start

print(f"✅ Matrix multiplication: {elapsed:.4f}s")
print("\n✅ CUDA is working correctly!")
