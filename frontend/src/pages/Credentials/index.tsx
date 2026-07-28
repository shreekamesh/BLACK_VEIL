import React from 'react'
import { Box, Paper, Typography, Grid, Chip, Card, CardContent, Button, LinearProgress, Stack } from '@mui/material'
import { Key, VpnKey, Speed, AutoAwesome } from '@mui/icons-material'
import { motion } from 'framer-motion'

const credentials = [
  { id: 'CRED-001', type: 'API Key', service: 'AWS IAM', status: 'active', entropy: 0.85, generation: 2, fitness: 0.78 },
  { id: 'CRED-002', type: 'SSH Key', service: 'GitHub', status: 'active', entropy: 0.92, generation: 1, fitness: 0.91 },
  { id: 'CRED-003', type: 'Password', service: 'Admin Portal', status: 'mutated', entropy: 0.76, generation: 3, fitness: 0.65 },
  { id: 'CRED-004', type: 'API Key', service: 'Database', status: 'active', entropy: 0.88, generation: 2, fitness: 0.82 },
  { id: 'CRED-005', type: 'SSH Key', service: 'Server Farm', status: 'expired', entropy: 0.71, generation: 1, fitness: 0.45 },
]

const CredentialsPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Credential Genome</Typography>
          <Typography variant="body2" color="text.secondary">DCMM - Dynamic Credential Mutation Model</Typography>
        </Box>
        <Button variant="contained" startIcon={<VpnKey />}>Generate Credential</Button>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[
          { label: 'Active Credentials', value: credentials.filter(c => c.status === 'active').length, icon: <Key />, color: 'success.main' },
          { label: 'Avg Entropy', value: '82%', icon: <Speed />, color: 'primary.main' },
          { label: 'Avg Fitness', value: '72%', icon: <AutoAwesome />, color: 'info.main' },
          { label: 'Expired', value: credentials.filter(c => c.status === 'expired').length, icon: <VpnKey />, color: 'error.main' },
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
        {credentials.map((cred, i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="subtitle2">{cred.id}</Typography>
                    <Chip label={cred.status} size="small" color={cred.status === 'active' ? 'success' : cred.status === 'mutated' ? 'info' : 'default'} />
                  </Box>
                  <Typography variant="h6">{cred.type}</Typography>
                  <Typography variant="body2" color="text.secondary">{cred.service}</Typography>
                  <Stack spacing={1} sx={{ mt: 2 }}>
                    <Stack direction="row" justifyContent="space-between"><Typography variant="caption">Entropy</Typography><Typography variant="caption">{Math.round(cred.entropy * 100)}%</Typography></Stack>
                    <LinearProgress variant="determinate" value={cred.entropy * 100} color="primary" sx={{ height: 4, borderRadius: 2 }} />
                    <Stack direction="row" justifyContent="space-between"><Typography variant="caption">Fitness</Typography><Typography variant="caption">{Math.round(cred.fitness * 100)}%</Typography></Stack>
                    <LinearProgress variant="determinate" value={cred.fitness * 100} color={cred.fitness > 0.7 ? 'success' : 'warning'} sx={{ height: 4, borderRadius: 2 }} />
                    <Stack direction="row" justifyContent="space-between"><Typography variant="caption">Generation</Typography><Chip label={`Gen ${cred.generation}`} size="small" variant="outlined" /></Stack>
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

export default CredentialsPage
