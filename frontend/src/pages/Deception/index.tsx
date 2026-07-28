import React from 'react'
import { Box, Paper, Typography, Grid, Chip, Card, CardContent, Button, LinearProgress, Stack } from '@mui/material'
import { Devices, Security, TrackChanges, AutoAwesome } from '@mui/icons-material'
import { motion } from 'framer-motion'

const deceptions = [
  { id: 'DEC-001', type: 'Honeypot', subtype: 'SSH', status: 'active', effectiveness: 0.85, interactions: 47, generation: 3 },
  { id: 'DEC-002', type: 'Honeypot', subtype: 'Web', status: 'active', effectiveness: 0.72, interactions: 23, generation: 2 },
  { id: 'DEC-003', type: 'Digital Twin', subtype: 'Database', status: 'active', effectiveness: 0.91, interactions: 12, generation: 1 },
  { id: 'DEC-004', type: 'Honeypot', subtype: 'API', status: 'evolved', effectiveness: 0.78, interactions: 56, generation: 4 },
  { id: 'DEC-005', type: 'Decoy', subtype: 'Endpoint', status: 'active', effectiveness: 0.64, interactions: 8, generation: 1 },
]

const DeceptionPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Deception Management</Typography>
          <Typography variant="body2" color="text.secondary">ACDM - Adaptive Cyber Deception Model</Typography>
        </Box>
        <Button variant="contained" startIcon={<Security />}>Deploy New</Button>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[
          { label: 'Active Deceptions', value: deceptions.filter(d => d.status === 'active').length, icon: <Devices />, color: 'success.main' },
          { label: 'Avg Effectiveness', value: '78%', icon: <TrackChanges />, color: 'primary.main' },
          { label: 'Total Interactions', value: deceptions.reduce((s, d) => s + d.interactions, 0), icon: <Security />, color: 'info.main' },
          { label: 'Generations', value: Math.max(...deceptions.map(d => d.generation)), icon: <AutoAwesome />, color: 'secondary.main' },
        ].map((stat, i) => (
          <Grid item xs={6} sm={3} key={i}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ color: stat.color }}>{stat.icon}</Box>
                <Box><Typography variant="h4" sx={{ fontWeight: 700, color: stat.color }}>{stat.value}</Typography><Typography variant="caption" color="text.secondary">{stat.label}</Typography></Box>
              </Paper>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={2}>
        {deceptions.map((d, i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="subtitle2">{d.id}</Typography>
                    <Chip label={d.status} size="small" color={d.status === 'active' ? 'success' : 'default'} />
                  </Box>
                  <Typography variant="h6">{d.subtype} {d.type}</Typography>
                  <Stack spacing={1} sx={{ mt: 2 }}>
                    <Stack direction="row" justifyContent="space-between"><Typography variant="caption">Effectiveness</Typography><Typography variant="caption">{Math.round(d.effectiveness * 100)}%</Typography></Stack>
                    <LinearProgress variant="determinate" value={d.effectiveness * 100} color={d.effectiveness > 0.8 ? 'success' : 'warning'} sx={{ height: 4, borderRadius: 2 }} />
                    <Stack direction="row" justifyContent="space-between"><Typography variant="caption">Interactions</Typography><Typography variant="caption">{d.interactions}</Typography></Stack>
                    <Stack direction="row" justifyContent="space-between"><Typography variant="caption">Generation</Typography><Chip label={`Gen ${d.generation}`} size="small" variant="outlined" /></Stack>
                    </Stack>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default DeceptionPage
