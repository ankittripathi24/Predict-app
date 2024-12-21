# IoT Predictive Maintenance Dashboard

A full-stack application for monitoring and predicting maintenance needs in an IoT-enabled manufacturing environment. The system processes sensor data to provide real-time insights and predictive maintenance recommendations.

## Features

- Real-time sensor data monitoring
- Machine learning-based predictive maintenance
- Context-aware predictions based on manufacturing process type
- Interactive data visualization
- Redis-based caching for improved performance
- PostgreSQL database for data persistence

## Project Structure

```
.
├── Connectivity_Layer_API/    # FastAPI backend
├── Model_Training/           # ML model training scripts
└── iot-dashboard/           # React frontend
```

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- Redis

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Set up the backend:
   ```bash
   cd Connectivity_Layer_API
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../iot-dashboard
   npm install
   ```

4. Configure environment variables:
   - Create `.env` files in both backend and frontend directories
   - Set required environment variables (database credentials, API endpoints, etc.)

## Running the Application

1. Start the backend server:
   ```bash
   cd Connectivity_Layer_API
   python ConnectivityFastAPI.py
   ```

2. Start the frontend development server:
   ```bash
   cd iot-dashboard
   npm start
   ```

3. Access the application at `http://localhost:3000`

## API Documentation

The API documentation is available at `http://localhost:8000/docs` when the backend server is running.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
