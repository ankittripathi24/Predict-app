import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  LinearProgress,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Grid,
  Paper
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import Alert from '@material-ui/lab/Alert';
import axios from 'axios';

const useStyles = makeStyles((theme) => ({
  root: {
    '& > *': {
      margin: theme.spacing(1),
    },
  },
  input: {
    display: 'none',
  },
  uploadButton: {
    marginTop: theme.spacing(2),
  },
  progress: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  formControl: {
    marginTop: theme.spacing(2),
    minWidth: 200,
  },
  metadataSection: {
    marginTop: theme.spacing(3),
    padding: theme.spacing(2),
  }
}));

const DataUpload = () => {
  const classes = useStyles();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [dataType, setDataType] = useState('');
  const [customMetadata, setCustomMetadata] = useState({});

  // Predefined data types and their specific metadata fields
  const dataTypes = {
    pressing: {
      name: 'Material Pressing',
      fields: [
        { key: 'material_type', label: 'Material Type', type: 'select', options: [
          'Plastic', 'Metal', 'Composite', 'Rubber', 'Other'
        ]},
        { key: 'pressure_range', label: 'Pressure Range (PSI)', type: 'select', options: [
          'Low (0-1000)', 'Medium (1000-5000)', 'High (5000+)'
        ]},
        { key: 'material_thickness', label: 'Material Thickness (mm)', type: 'text' }
      ]
    },
    machining: {
      name: 'CNC Machining',
      fields: [
        { key: 'material_type', label: 'Material Type', type: 'select', options: [
          'Aluminum', 'Steel', 'Titanium', 'Plastic', 'Other'
        ]},
        { key: 'cutting_speed', label: 'Cutting Speed (RPM)', type: 'select', options: [
          'Low (0-5000)', 'Medium (5000-15000)', 'High (15000+)'
        ]},
        { key: 'coolant_type', label: 'Coolant Type', type: 'select', options: [
          'Water-based', 'Oil-based', 'Synthetic', 'None'
        ]}
      ]
    },
    assembly: {
      name: 'Assembly Line',
      fields: [
        { key: 'product_type', label: 'Product Type', type: 'select', options: [
          'Electronics', 'Automotive', 'Consumer Goods', 'Industrial'
        ]},
        { key: 'line_speed', label: 'Line Speed', type: 'select', options: [
          'Slow', 'Medium', 'Fast'
        ]},
        { key: 'batch_size', label: 'Batch Size', type: 'text' }
      ]
    }
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setUploadStatus(null);
  };

  const handleDataTypeChange = (event) => {
    setDataType(event.target.value);
    setCustomMetadata({}); // Reset metadata when data type changes
  };

  const handleMetadataChange = (field, value) => {
    setCustomMetadata(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleUpload = async () => {
    if (!file || !dataType) {
      setUploadStatus({
        severity: 'error',
        message: 'Please select a file and specify the data type'
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('data_type', dataType);
    formData.append('metadata', JSON.stringify(customMetadata));

    setUploading(true);
    try {
      const response = await axios.post('http://localhost:8000/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setUploadStatus({
        severity: 'success',
        message: 'File uploaded successfully!'
      });
    } catch (error) {
      setUploadStatus({
        severity: 'error',
        message: error.response?.data?.detail || 'Error uploading file'
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={classes.root}>
      <Typography variant="h6" gutterBottom>
        Upload Sensor Data
      </Typography>

      <input
        accept=".csv"
        className={classes.input}
        id="contained-button-file"
        type="file"
        onChange={handleFileChange}
      />
      <label htmlFor="contained-button-file">
        <Button
          variant="contained"
          color="primary"
          component="span"
          startIcon={<CloudUploadIcon />}
        >
          Select CSV File
        </Button>
      </label>

      {file && (
        <Typography variant="body2" gutterBottom>
          Selected file: {file.name}
        </Typography>
      )}

      <FormControl className={classes.formControl} fullWidth>
        <InputLabel>Data Type</InputLabel>
        <Select
          value={dataType}
          onChange={handleDataTypeChange}
        >
          {Object.entries(dataTypes).map(([key, value]) => (
            <MenuItem key={key} value={key}>{value.name}</MenuItem>
          ))}
        </Select>
      </FormControl>

      {dataType && (
        <Paper className={classes.metadataSection}>
          <Typography variant="subtitle1" gutterBottom>
            {dataTypes[dataType].name} Details
          </Typography>
          <Grid container spacing={2}>
            {dataTypes[dataType].fields.map((field) => (
              <Grid item xs={12} sm={6} key={field.key}>
                {field.type === 'select' ? (
                  <FormControl fullWidth>
                    <InputLabel>{field.label}</InputLabel>
                    <Select
                      value={customMetadata[field.key] || ''}
                      onChange={(e) => handleMetadataChange(field.key, e.target.value)}
                    >
                      {field.options.map((option) => (
                        <MenuItem key={option} value={option}>{option}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                ) : (
                  <TextField
                    fullWidth
                    label={field.label}
                    value={customMetadata[field.key] || ''}
                    onChange={(e) => handleMetadataChange(field.key, e.target.value)}
                  />
                )}
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      <Button
        className={classes.uploadButton}
        variant="contained"
        color="primary"
        onClick={handleUpload}
        disabled={!file || uploading || !dataType}
        fullWidth
      >
        Upload
      </Button>

      {uploading && (
        <LinearProgress className={classes.progress} />
      )}

      {uploadStatus && (
        <Alert severity={uploadStatus.severity}>
          {uploadStatus.message}
        </Alert>
      )}
    </div>
  );
};

export default DataUpload;
