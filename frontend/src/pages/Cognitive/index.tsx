import React from 'react'
import { Box, Paper, Typography, Grid, Chip, Card, CardContent, LinearProgress, Stack } from '@mui/material'
import { Grain, Psychology, Memory, Visibility, Sensors, Hub } from '@mui/icons-material'
import { motion } from 'framer-motion'

const layers = [
  { name: 'Perception', icon: <Visibility />, status: 'active', data: { sensors: 5, events: 234, rate: '45/s' }, color: 'info.main' },
  { name: 'Reasoning', icon: <Psychology />, status: 'active', data: { engines: 4, inferences: 189, accuracy: 0.92 }, color: 'success.main' },
  { name: 'Memory', icon: <Memory />, status: 'active', data: { episodic: 850, semantic: 400, procedural: 125 }, color: 'warning.main' },
  { name: 'Meta-Cognitive', icon: <Hub />, status: 'monitoring', data: { awareness: 'high', anomalies: 0, health: 'healthy' }, color: 'secondary.main' },
]

const CognitivePage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Cognitive State</Typography>
        <Typography variant="body2" color="text.secondary">Cognitive Security Layer - Perception, Reasoning, Memory, Meta-Cognition</Typography>
      </Box>

      <Grid container spacing={3}>
        {layers.map((layer, i) => (
          <Grid item xs={12} md={6} key={i}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.15 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ color: layer.color }}>{layer.icon}</Box>
                      <Typography variant="h6">{layer.name}</Typography>
                    </Box>
                    <Chip label={layer.status} size="small" color={layer.status === 'active' ? 'success' : 'info'} />
                  </Box>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 2, mt: 2 }}>
                    {Object.entries(layer.data).map(([key, val]) => (
                      <Box key={key} sx={{ textAlign: 'center' }}>
                        <Typography variant="h6" sx={{ color: layer.color, fontWeight: 700 }}>{val}</Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'capitalize' }}>{key.replace('_', ' ')}</Typography>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>Consensus Engine</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>Multi-AI consensus across all cognitive layers</Typography>
        <Stack direction="row" spacing={2}>
          {['Network', 'IoT', 'User', 'CICIDS', 'Fusion'].map((domain) => (
            <Box key={domain} sx={{ flex: 1, textAlign: 'center' }}>
              <Typography variant="caption">{domain}</Typography>
              <LinearProgress variant="determinate" value={85 + Math.random() * 10} sx={{ height: 6, borderRadius: 3, mt: 1 }} color="primary" />
              <Typography variant="h6" sx={{ mt: 0.5 }}>{Math.floor(85 + Math.random() * 10)}%</Typography>
            </Box>
          ))}
        </Stack>
      </Paper>
    </Box>
  )
}

export default CognitivePage
