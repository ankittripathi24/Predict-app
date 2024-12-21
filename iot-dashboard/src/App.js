import React from 'react';
import './index.css';
import { makeStyles } from '@material-ui/core/styles';
import { Container, Grid, Paper, AppBar, Toolbar, Typography } from '@material-ui/core';
import DataVisualization from './components/DataVisualization';
import DataUpload from './components/DataUpload';
import Predictions from './components/Predictions';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column',
  },
  appBar: {
    marginBottom: theme.spacing(4),
  },
}));

function App() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar position="static" className={classes.appBar}>
        <Toolbar>
          <Typography variant="h6">
            IoT Predictive Maintenance Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" className={classes.container}>
        <Grid container spacing={3}>
          {/* Data Visualization Section */}
          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <DataVisualization />
            </Paper>
          </Grid>

          {/* Data Upload Section */}
          <Grid item xs={12} md={6}>
            <Paper className={classes.paper}>
              <DataUpload />
            </Paper>
          </Grid>

          {/* Predictions Section */}
          <Grid item xs={12} md={6}>
            <Paper className={classes.paper}>
              <Predictions />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </div>
  );
}

export default App;
