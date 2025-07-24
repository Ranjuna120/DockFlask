# 🐳 DockFlask

A modern, containerized Python Flask web application with Docker integration.

## ✨ Features

- **Python Flask** - Lightweight and powerful web framework
- **Docker Integration** - Fully containerized for easy deployment
- **Production Ready** - Configured with Gunicorn WSGI server
- **Health Monitoring** - Built-in health check endpoints
- **Modern UI** - Bootstrap 5 responsive interface
- **Development Support** - Separate dev environment configuration

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd DockFlask

# Build and run the application
docker-compose up --build

# The app will be available at http://localhost:5000
```

### Development Mode

```bash
# Run in development mode with hot reload
docker-compose --profile dev up --build

# Development server will be available at http://localhost:5001
```

### Manual Docker Build

```bash
# Build the Docker image
docker build -t dockflask .

# Run the container
docker run -p 5000:5000 dockflask
```

## 📁 Project Structure

```
DockFlask/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker ignore patterns
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   └── about.html
└── static/              # Static assets
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 🔗 API Endpoints

- `GET /` - Home page
- `GET /about` - About page
- `GET /api/health` - Health check endpoint
- `GET /api/info` - Application information

## 🛠️ Technologies Used

- **Python 3.11** - Modern Python runtime
- **Flask 2.3.3** - Web framework
- **Gunicorn** - Production WSGI server
- **Docker** - Containerization
- **Bootstrap 5** - Frontend framework

## 🔧 Configuration

### Environment Variables

- `FLASK_ENV` - Set to `development` or `production`
- `PORT` - Port number (default: 5000)

### Health Check

The application includes a health check endpoint at `/api/health` that returns:

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00",
  "message": "Flask app is running successfully!"
}
```

## 🚢 Deployment

The application is production-ready and can be deployed to any Docker-compatible platform:

- **Docker Swarm**
- **Kubernetes**
- **AWS ECS**
- **Google Cloud Run**
- **Azure Container Instances**

## 📝 License

This project is open source and available under the MIT License.

---

Built with ❤️ using Flask and Docker
