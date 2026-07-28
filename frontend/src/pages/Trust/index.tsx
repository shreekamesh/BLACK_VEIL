import React, { useEffect, useState } from 'react'
import {
  Box, Paper, Typography, Grid, Chip, Tabs, Tab,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, TextField, InputAdornment,
} from '@mui/material'
import { Search, Refresh, TrendingUp, TrendingDown, Security } from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import { RootState, AppDispatch } from '@/store'
import { fetchTrustSummary } from '@/store/slices/trustSlice'
import { motion } from 'framer-motion'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
  </div>
)

const TrustPage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { summary } = useSelector((state: RootState) => state.trust)
  const [tabValue, setTabValue] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    dispatch(fetchTrustSummary())
  }, [dispatch])

  const entities = [
    { id: 'network-01', name: 'Network Agent', type: 'Network', score: 87, level: 'HIGH', change: 2.1 },
    { id: 'iot-01', name: 'IoT Agent', type: 'IoT', score: 82, level: 'HIGH', change: -0.5 },
    { id: 'user-01', name: 'User Agent', type: 'User', score: 74, level: 'MEDIUM', change: -3.2 },
    { id: 'cicids-01', name: 'CICIDS Agent', type: 'CICIDS', score: 80, level: 'HIGH', change: 1.8 },
    { id: 'fusion-01', name: 'Fusion Engine', type: 'Fusion', score: 91, level: 'VERY_HIGH', change: 0.3 },
  ]

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success.main'
    if (score >= 60) return 'warning.main'
    return 'error.main'
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'VERY_HIGH': case 'HIGH': return 'success' as const
      case 'MEDIUM': return 'warning' as const
      case 'LOW': case 'CRITICAL': return 'error' as const
      default: return 'default' as const
    }
  }

  const filteredEntities = entities.filter(e =>
    e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.id.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Trust Management</Typography>
          <Typography variant="body2" color="text.secondary">ATCN - Adaptive Trust Cognitive Network</Typography>
        </Box>
        <Button variant="outlined" startIcon={<Refresh />} onClick={() => dispatch(fetchTrustSummary())}>Refresh</Button>
      </Box>
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h3" sx={{ color: getScoreColor(summary?.avgTrust || 82), fontWeight: 700 }}>
                {summary?.avgTrust || 82}%
              </Typography>
              <Typography variant="body2" color="text.secondary">Average Trust Score</Typography>
            </Paper>
          </motion.div>
        </Grid>
        <Grid item xs={12} md={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h3" color="success.main" sx={{ fontWeight: 700 }}>
                {entities.filter(e => e.level === 'HIGH' || e.level === 'VERY_HIGH').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">High Trust Entities</Typography>
            </Paper>
          </motion.div>
        </Grid>
        <Grid item xs={12} md={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h3" color="warning.main" sx={{ fontWeight: 700 }}>
                {entities.filter(e => e.level === 'MEDIUM').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">Medium Trust Entities</Typography>
            </Paper>
          </motion.div>
        </Grid>
        <Grid item xs={12} md={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h3" color="error.main" sx={{ fontWeight: 700 }}>
                {entities.filter(e => e.level === 'LOW' || e.level === 'CRITICAL').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">Low Trust Entities</Typography>
            </Paper>
          </motion.div>
        </Grid>
      </Grid>
      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
          <Tab label="Trust Scores" />
          <Tab label="Trust Graph" />
          <Tab label="History" />
          <Tab label="Relationships" />
        </Tabs>
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ px: 2, pb: 2 }}>
            <TextField placeholder="Search entities..." size="small" value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{ mb: 2, maxWidth: 300 }}
              InputProps={{ startAdornment: <InputAdornment position="start"><Search /></InputAdornment> }}
            />
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Entity</TableCell>
                    <TableCell>ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Trust Score</TableCell>
                    <TableCell>Level</TableCell>
                    <TableCell>Change</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredEntities.map((entity) => (
                    <TableRow key={entity.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Security sx={{ color: getScoreColor(entity.score), fontSize: 20 }} />
                          {entity.name}
                        </Box>
                      </TableCell>
                      <TableCell><Typography variant="caption">{entity.id}</Typography></TableCell>
                      <TableCell>{entity.type}</TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: getScoreColor(entity.score) }}>{entity.score}%</Typography>
                      </TableCell>
                      <TableCell><Chip label={entity.level} size="small" color={getLevelColor(entity.level)} /></TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          {entity.change >= 0 ? <TrendingUp sx={{ color: 'success.main', fontSize: 16 }} /> : <TrendingDown sx={{ color: 'error.main', fontSize: 16 }} />}
                          <Typography variant="caption" color={entity.change >= 0 ? 'success.main' : 'error.main'}>
                            {entity.change >= 0 ? '+' : ''}{entity.change}%
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ p: 2, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            
            <Typography color="text.secondary">Trust graph visualization coming soon with Cytoscape.js</Typography>
          </Box>
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          <Box sx={{ p: 2, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">Trust history timeline visualization coming soon with Recharts</Typography>
          </Box>
        </TabPanel>
        <TabPanel value={tabValue} index={3}>
          <Box sx={{ p: 2, minHeight: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">Trust relationship graph visualization coming soon with Cytoscape.js</Typography>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  )
}

export default TrustPage
