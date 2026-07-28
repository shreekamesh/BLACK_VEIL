import React, { useState } from 'react'
import { Box, Paper, Typography, Grid, Chip, Card, CardContent, Button, LinearProgress, Stack } from '@mui/material'
import { AutoAwesome, TrackChanges, History, DeleteOutline } from '@mui/icons-material'

interface EvtHistory {
  id: string
  type: string
  icon: 'primary' | 'secondary' | 'success' | 'warning'
  desc: string
  date: string
}

const EvolutionPage: React.FC = () => {
  const [evoState] = useState({
    learningRate: 0.01,
    explorationRate: 0.1,
    generation: 42,
    totalAdaptations: 156,
    knowledgeForgotten: 23,
  })

  const [evoHistory] = useState<EvtHistory[]>([
    { id: 'evt-001', type: 'model_update', desc: 'Updated network detection model accuracy from 0.94 to 0.95', date: '2024-01-15', icon: 'primary' },
    { id: 'evt-002', type: 'feature_adaptation', desc: 'Added 3 new features for IoT anomaly detection', date: '2024-01-14', icon: 'secondary' },
    { id: 'evt-003', type: 'threshold_adjustment', desc: 'Adjusted CICIDS confidence threshold from 0.8 to 0.75', date: '2024-01-13', icon: 'warning' },
    { id: 'evt-004', type: 'knowledge_forgetting', desc: 'Removed 23 outdated attack patterns from memory', date: '2024-01-12', icon: 'success' },
  ])

  const stats = [
    { label: 'Generation', value: evoState.generation, icon: <AutoAwesome />, color: '#00d4ff' },
    { label: 'Learning Rate', value: evoState.learningRate, icon: <TrackChanges />, color: '#7c3aed' },
    { label: 'Adaptations', value: evoState.totalAdaptations, icon: <History />, color: '#10b981' },
    { label: 'Forgotten', value: evoState.knowledgeForgotten, icon: <DeleteOutline />, color: '#f59e0b' },
  ]

  const [metrics] = useState([
    { label: 'Learning Rate', value: 0.01, max: 0.1 },
    { label: 'Exploration Rate', value: 0.1, max: 1.0 },
    { label: 'Model Updates', value: 45, max: 100 },
    { label: 'Feature Adaptations', value: 23, max: 50 },
    { label: 'Knowledge Forgotten', value: 23, max: 100 },
  ])

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
        Evolution Engine
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Continuous learning, adaptation, and self-reorganization system
      </Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {stats.map((stat, i) => (
          <Grid item xs={6} sm={3} key={i}>
            <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ color: stat.color }}>{stat.icon}</Box>
              <Box>
                <Typography variant="h5">{stat.value}</Typography>
                <Typography variant="caption" color="text.secondary">{stat.label}</Typography>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Evolution Metrics</Typography>
              {metrics.map((metric) => (
                <Box key={metric.label} sx={{ mb: 2 }}>
                  <Stack direction="row" justifyContent="space-between">
                    <Typography variant="caption">{metric.label}</Typography>
                    <Typography variant="caption" sx={{ fontWeight: 600 }}>
                      {metric.label.includes('Rate') ? metric.value : Math.round(metric.value)}
                    </Typography>
                  </Stack>
                  <LinearProgress variant="determinate" value={(metric.value / metric.max) * 100} sx={{ height: 4, borderRadius: 2 }} />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Evolution History</Typography>
              {evoHistory.map((evt, i) => (
                <Box key={evt.id} sx={{ display: 'flex', gap: 2, mb: 2, pb: i < evoHistory.length - 1 ? 2 : 0, borderBottom: i < evoHistory.length - 1 ? '1px solid rgba(148,163,184,0.12)' : 'none' }}>
                  <Chip label={evt.type.replace('_', ' ')} size="small" color={evt.icon as any} />
                  <Box>
                    <Typography variant="body2">{evt.desc}</Typography>
                    <Typography variant="caption" color="text.secondary">{evt.date}</Typography>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default EvolutionPage
