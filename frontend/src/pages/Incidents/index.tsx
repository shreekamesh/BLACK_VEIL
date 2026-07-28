import React, { useState } from 'react'
import { Box, Paper, Typography, Grid, Chip, Tabs, Tab, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, InputAdornment, IconButton, Menu, MenuItem, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material'
import { Search, FilterList, MoreVert, Refresh, Error as ErrorIcon, Warning, Info, CheckCircle } from '@mui/icons-material'
import { motion } from 'framer-motion'

interface Incident {
  id: string; title: string; severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'; status: string; source: string; timestamp: string; assignedTo?: string
}

const incidents: Incident[] = [
  { id: 'INC-001', title: 'Suspicious Outbound Traffic', severity: 'CRITICAL', status: 'NEW', source: 'Network Agent', timestamp: '2024-01-15T10:30:00Z' },
  { id: 'INC-002', title: 'IoT Device Anomaly Detected', severity: 'HIGH', status: 'INVESTIGATING', source: 'IoT Agent', timestamp: '2024-01-15T09:15:00Z', assignedTo: 'Analyst-01' },
  { id: 'INC-003', title: 'Brute Force Attempt', severity: 'MEDIUM', status: 'CONTAINED', source: 'CICIDS Agent', timestamp: '2024-01-15T08:00:00Z' },
  { id: 'INC-004', title: 'DNS Tunneling Detection', severity: 'HIGH', status: 'INVESTIGATING', source: 'Network Agent', timestamp: '2024-01-15T07:45:00Z' },
  { id: 'INC-005', title: 'Policy Violation', severity: 'LOW', status: 'RESOLVED', source: 'User Agent', timestamp: '2024-01-14T22:30:00Z', assignedTo: 'Analyst-02' },
]

const severityColors: Record<string, 'error' | 'warning' | 'info' | 'success'> = { CRITICAL: 'error', HIGH: 'error', MEDIUM: 'warning', LOW: 'info' }
const severityIcons: Record<string, React.ReactNode> = { CRITICAL: <ErrorIcon />, HIGH: <Warning />, MEDIUM: <Warning />, LOW: <Info /> }

const IncidentsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null)

  const filtered = incidents.filter(i => i.title.toLowerCase().includes(searchTerm.toLowerCase()) || i.id.toLowerCase().includes(searchTerm.toLowerCase()))

  const handleMenuOpen = (e: React.MouseEvent<HTMLElement>, incident: Incident) => { setAnchorEl(e.currentTarget); setSelectedIncident(incident) }
  const handleMenuClose = () => { setAnchorEl(null) }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Incidents</Typography>
          <Typography variant="body2" color="text.secondary">Security incident management and response</Typography>
        </Box>
        <Button variant="outlined" startIcon={<Refresh />}>Refresh</Button>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[
          { label: 'Total Incidents', value: incidents.length, color: 'text.primary' },
          { label: 'Critical', value: incidents.filter(i => i.severity === 'CRITICAL').length, color: 'error.main' },
          { label: 'Investigating', value: incidents.filter(i => i.status === 'INVESTIGATING').length, color: 'warning.main' },
          { label: 'Resolved', value: incidents.filter(i => i.status === 'RESOLVED').length, color: 'success.main' },
        ].map((stat, i) => (
          <Grid item xs={6} sm={3} key={i}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: stat.color }}>{stat.value}</Typography>
                <Typography variant="caption" color="text.secondary">{stat.label}</Typography>
              </Paper>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Paper>
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <TextField placeholder="Search incidents..." size="small" value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)} sx={{ flex: 1, maxWidth: 300 }}
            InputProps={{ startAdornment: <InputAdornment position="start"><Search /></InputAdornment> }} />
          <Button variant="outlined" startIcon={<FilterList />}>Filter</Button>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Assigned To</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.map((incident) => (
                <TableRow key={incident.id} hover sx={{ cursor: 'pointer' }} onClick={() => { setSelectedIncident(incident); setDetailOpen(true) }}>
                  <TableCell>{incident.id}</TableCell>
                  <TableCell>{incident.title}</TableCell>
                  <TableCell><Chip icon={<>{severityIcons[incident.severity]}</>} label={incident.severity} size="small" color={severityColors[incident.severity]} /></TableCell>
                  <TableCell><Chip label={incident.status} size="small" color={incident.status === 'RESOLVED' ? 'success' : incident.status === 'INVESTIGATING' ? 'info' : 'warning'} /></TableCell>
                  <TableCell>{incident.source}</TableCell>
                  <TableCell>{new Date(incident.timestamp).toLocaleString()}</TableCell>
                  <TableCell>{incident.assignedTo || 'Unassigned'}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={(e) => { e.stopPropagation(); handleMenuOpen(e, incident) }}><MoreVert /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleMenuClose}><CheckCircle sx={{ mr: 1, fontSize: 18 }} /> Start Investigation</MenuItem>
        <MenuItem onClick={handleMenuClose}><CheckCircle sx={{ mr: 1, fontSize: 18 }} /> Contain</MenuItem>
        <MenuItem onClick={handleMenuClose}><CheckCircle sx={{ mr: 1, fontSize: 18 }} /> Resolve</MenuItem>
      </Menu>

      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Incident Details: {selectedIncident?.id}</DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>{selectedIncident?.title}</Typography>
          <Typography variant="body2" color="text.secondary">{(selectedIncident as any)?.description || ''}</Typography>
        </DialogContent>
        <DialogActions><Button onClick={() => setDetailOpen(false)}>Close</Button></DialogActions>
      </Dialog>
    </Box>
  )
}

export default IncidentsPage
