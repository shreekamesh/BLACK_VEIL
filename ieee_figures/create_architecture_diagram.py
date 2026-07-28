import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 12))

# Title
ax.text(0.5, 0.95, 'BLACK VEIL System Architecture', 
        ha='center', va='center', fontsize=14, fontweight='bold')

# Define layers
layers = [
    ('🧠 Cognitive Intelligence', 0.5, 0.85),
    ('🛡️ Threat Intelligence', 0.5, 0.75),
    ('🔐 Trust Intelligence (TTRM)', 0.5, 0.65),
    ('🧬 Credential Intelligence (DCMM)', 0.5, 0.55),
    ('🎭 Reality Fabric', 0.5, 0.45),
    ('📊 Knowledge Layer (LAMG)', 0.5, 0.35),
    ('⚙️ Operations Intelligence', 0.5, 0.25),
    ('📈 Learning Layer', 0.5, 0.15),
    ('🚀 Response Layer', 0.5, 0.05),
]

# Draw layers
for name, x, y in layers:
    rect = patches.FancyBboxPatch((x-0.2, y-0.03), 0.4, 0.06,
                                   boxstyle="round,pad=0.02",
                                   facecolor='lightblue', edgecolor='black')
    ax.add_patch(rect)
    ax.text(x, y, name, ha='center', va='center', fontsize=10)

# ACDO Orchestrator - highlight
rect = patches.FancyBboxPatch((0.25, 0.88), 0.5, 0.1,
                               boxstyle="round,pad=0.02",
                               facecolor='lightgreen', edgecolor='black', linewidth=2)
ax.add_patch(rect)
ax.text(0.5, 0.93, 'ACDO Orchestrator', ha='center', va='center', fontsize=12, fontweight='bold')

# Arrows
for i in range(len(layers)-1):
    y1 = layers[i][2] - 0.03
    y2 = layers[i+1][2] + 0.03
    ax.annotate('', xy=(0.5, y2), xytext=(0.5, y1),
                arrowprops=dict(arrowstyle='->', color='gray'))

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')
plt.tight_layout()
plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Architecture diagram created: architecture_diagram.png")
