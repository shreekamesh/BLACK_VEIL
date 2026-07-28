import React, { useState } from 'react'
import { Box, Paper, Typography, Grid, Chip, Tabs, Tab, Button, Card, CardContent, LinearProgress, Stack } from '@mui/material'
import { Psychology, Refresh, Cloud, Storage, Memory } from '@mui/icons-material'
import { motion } from 'framer-motion'

const models = [
  { name: 'CNN', version: '2.1.0', type: 'Neural Network', domain: 'Network', accuracy: 0.96, status: 'active', latency: 12 },
  { name: 'DNN', version: '1.8.0', type: 'Neural Network', domain: 'IoT', accuracy: 0.93, status: 'active', latency: 8 },
  { name: 'XGBoost', version: '3.0.0', type: 'Gradient Boosting', domain: 'CICIDS', accuracy: 0.95, status: 'active', latency: 5 },
  { name: 'Random Forest', version: '2.0.0', type: 'Ensemble', domain: 'User', accuracy: 0.91, status: 'active', latency: 4 },
  { name: 'Transformer', version: '1.0.0', type: 'Transformer', domain: 'Fusion', accuracy: 0.94, status: 'training', latency: 15 },
]

const AIPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>AI Models & Predictions</Typography>
          <Typography variant="body2" color="text.secondary">Multi-domain ensemble inference engine</Typography>
        </Box>
        <Button variant="outlined" startIcon={<Refresh />}>Refresh Models</Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { label: 'Active Models', value: models.filter(m => m.status === 'active').length, icon: <Cloud />, color: 'success.main' },
          { label: 'Avg Accuracy', value: '94.2%', icon: <Psychology />, color: 'primary.main' },
          { label: 'Training', value: models.filter(m => m.status === 'training').length, icon: <Memory />, color: 'warning.main' },
          { label: 'Total Predictions', value: '12,847', icon: <Storage />, color: 'info.main' },
        ].map((stat, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ color: stat.color }}>{stat.icon}</Box>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: stat.color }}>{stat.value}</Typography>
                  <Typography variant="caption" color="text.secondary">{stat.label}</Typography>
                </Box>
              </Paper>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tab label="Model Registry" />
        <Tab label="Predictions" />
        <Tab label="Training" />
        <Tab label="Explainability" />
      </Tabs>

      {tabValue === 0 && (
        <Grid container spacing={2}>
          {models.map((model, i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6">{model.name}</Typography>
                      <Chip label={model.status} size="small" color={model.status === 'active' ? 'success' : 'warning'} />
                    </Box>
                    <Typography variant="body2" color="text.secondary">v{model.version} | {model.type}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>Domain: {model.domain}</Typography>
                    <Box sx={{ mt: 2 }}>
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="caption">Accuracy:</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>{(model.accuracy * 100).toFixed(1)}%</Typography>
                      </Stack>
                      <LinearProgress variant="determinate" value={model.accuracy * 100} color={model.accuracy > 0.93 ? 'success' : 'warning'} sx={{ height: 4, borderRadius: 2, mb: 1 }} />
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="caption">Latency:</Typography>
                        <Typography variant="caption">{model.latency}ms</Typography>
                      </Stack>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}

      {tabValue === 1 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Psychology sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography color="text.secondary">Prediction panel with real-time input/output interface</Typography>
          <Typography variant="caption" color="text.disabled">Select models and provide input data to run predictions</Typography>
        </Paper>
      )}

      {tabValue === 2 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Memory sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography color="text.secondary">Training management with job history and metrics</Typography>
          <Typography variant="caption" color="text.disabled">Configure, start, and monitor model training jobs</Typography>
        </Paper>
      )}

      {tabValue === 3 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Psychology sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography color="text.secondary">SHAP/LIME feature importance and explanation viewer</Typography>
          <Typography variant="caption" color="text.disabled">Understand model decisions with explainable AI</Typography>
        </Paper>
      )}
    </Box>
  )
}

export default AIPage
