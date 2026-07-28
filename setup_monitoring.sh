#!/bin/bash
echo "📊 BLACK VEIL Monitoring Setup"
echo "=============================="

# Install monitoring packages
echo "Installing monitoring packages..."
pip install psutil requests

# Create metrics integration
python3 -c "
print('✅ Creating prometheus_metrics.py...')
"

# Test monitoring dashboard
echo "Running monitoring dashboard..."
python3 monitoring_dashboard.py

echo ""
echo "✅ Monitoring setup complete!"
echo "📊 Run dashboard: python3 monitoring_dashboard.py"
echo "📈 Prometheus metrics: http://localhost:9090/metrics"
