import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Grid,
  CircularProgress,
  Chip,
  Button
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import WarningIcon from '@material-ui/icons/Warning';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import RefreshIcon from '@material-ui/icons/Refresh';
import MuiAlert from '@material-ui/lab/Alert';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const useStyles = makeStyles((theme) => ({
  root: {
    minWidth: 275,
  },
  title: {
    marginBottom: theme.spacing(2),
  },
  card: {
    margin: theme.spacing(1),
  },
  warningChip: {
    backgroundColor: theme.palette.error.main,
    color: theme.palette.error.contrastText,
  },
  healthyChip: {
    backgroundColor: theme.palette.success.main,
    color: theme.palette.success.contrastText,
  },
  lastUpdated: {
    marginTop: theme.spacing(2),
    color: theme.palette.text.secondary,
  },
  refreshButton: {
    marginLeft: theme.spacing(2),
  },
  statsGrid: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  }
}));

const PredictionTimeline = ({ data }) => {
  const formattedData = data.map(point => ({
    time: new Date(point.timestamp).toLocaleTimeString(),
    temperature: point.temperature,
    vibration: point.vibration,
    energy: point.energy
  }));

  return (
    <Box mt={3} height={300}>
      <Typography variant="subtitle2" gutterBottom>
        Predictions Timeline (Next 6 Hours)
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="temperature" stroke="#8884d8" name="Temperature" />
          <Line type="monotone" dataKey="vibration" stroke="#82ca9d" name="Vibration" />
          <Line type="monotone" dataKey="energy" stroke="#ffc658" name="Energy" />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

const PredictionGroup = ({ group }) => {
  const classes = useStyles();
  const { dataType, metadata, prediction } = group;

  // Format metadata for display
  const metadataDisplay = Object.entries(metadata)
    .map(([key, value]) => `${key.replace(/_/g, ' ')}: ${value}`)
    .join(' • ');

  return (
    <Card className={classes.card}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h6" component="h2">
              {dataType.charAt(0).toUpperCase() + dataType.slice(1)}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              {metadataDisplay}
            </Typography>
          </Box>
          <Chip
            icon={prediction.maintenanceNeeded ? <WarningIcon /> : <CheckCircleIcon />}
            label={prediction.maintenanceNeeded ? 'Maintenance Needed' : 'Healthy'}
            className={prediction.maintenanceNeeded ? classes.warningChip : classes.healthyChip}
          />
        </Box>

        <Typography color="textSecondary" gutterBottom>
          Confidence: {(prediction.probability * 100).toFixed(1)}%
        </Typography>

        <Typography color="textSecondary" gutterBottom>
          Estimated Time to Maintenance: {prediction.estimatedTimeToMaintenance}
        </Typography>

        <Grid container spacing={2} className={classes.statsGrid}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Current Readings:
            </Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="body2">
              Temperature: {prediction.averageReadings.temperature.toFixed(1)}
            </Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="body2">
              Vibration: {prediction.averageReadings.vibration.toFixed(1)}
            </Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="body2">
              Energy: {prediction.averageReadings.energy.toFixed(1)}
            </Typography>
          </Grid>
        </Grid>

        {prediction.issues.length > 0 && (
          <Box className={classes.issuesList}>
            <Typography variant="subtitle2" gutterBottom>
              Detected Issues:
            </Typography>
            {prediction.issues.map((issue, index) => (
              <Typography key={index} variant="body2" color="error">
                • {issue}
              </Typography>
            ))}
          </Box>
        )}

        {prediction.predictions && (
          <PredictionTimeline data={prediction.predictions} />
        )}
      </CardContent>
    </Card>
  );
};

const Predictions = () => {
  const classes = useStyles();
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastFetchTime, setLastFetchTime] = useState(null);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/get-predictions');
      setPredictions(response.data);
      setError(null);
      setLastFetchTime(new Date());
    } catch (err) {
      console.error('Error fetching predictions:', err);
      setError(err.response?.data?.detail || 'Failed to load predictions. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
    // Check for predictions once every hour
    const interval = setInterval(fetchPredictions, 60 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    fetchPredictions();
  };

  if (loading && !predictions) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={2}>
        <Typography variant="h6" className={classes.title}>
          Maintenance Predictions
        </Typography>
        <Button
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={loading}
          className={classes.refreshButton}
          size="small"
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Box mb={2}>
          <MuiAlert severity="error" variant="filled">
            {error}
          </MuiAlert>
        </Box>
      )}

      {predictions?.message && (
        <Box mb={2}>
          <MuiAlert severity="info" variant="filled">
            {predictions.message}
          </MuiAlert>
        </Box>
      )}

      {predictions?.groups && predictions.groups.length > 0 && (
        <Grid container spacing={3}>
          {predictions.groups.map((group, index) => (
            <Grid item xs={12} key={index}>
              <PredictionGroup group={group} />
            </Grid>
          ))}
        </Grid>
      )}

      {predictions?.lastUpdated && (
        <Typography variant="caption" className={classes.lastUpdated}>
          Last updated: {new Date(predictions.lastUpdated).toLocaleString()}
        </Typography>
      )}
    </Box>
  );
};

export default Predictions;
