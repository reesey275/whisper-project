#!/bin/bash
# Multi-Stack Management Scripts

# Function to start different stack configurations
start_stack() {
    local config=$1
    local project_name=$2
    
    case $config in
        "dev")
            echo "Starting development stack: $project_name"
            docker-compose -f docker-compose.yml -f docker-compose.dev.yml -p "$project_name" up -d
            ;;
        "prod")
            echo "Starting production stack: $project_name"
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml -p "$project_name" up -d
            ;;
        "gpu")
            echo "Starting GPU-accelerated stack: $project_name"
            docker-compose -f docker-compose.yml -f docker-compose.gpu.yml -p "$project_name" up -d
            ;;
        "queue")
            echo "Starting stack with queue processing: $project_name"
            docker-compose -f docker-compose.yml -p "$project_name" --profile queue up -d
            ;;
        "auto")
            echo "Starting stack with auto file watching: $project_name"
            docker-compose -f docker-compose.yml -p "$project_name" --profile auto up -d
            ;;
        "full")
            echo "Starting full stack with all features: $project_name"
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml -p "$project_name" --profile queue --profile auto --profile ui up -d
            ;;
        *)
            echo "Unknown configuration: $config"
            echo "Available configs: dev, prod, gpu, queue, auto, full"
            exit 1
            ;;
    esac
}

# Function to stop a stack
stop_stack() {
    local project_name=$1
    echo "Stopping stack: $project_name"
    docker-compose -p "$project_name" down
}

# Function to list running stacks
list_stacks() {
    echo "Running Docker Compose projects:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | grep whisper
}

# Function to show stack logs
show_logs() {
    local project_name=$1
    local service=$2
    
    if [ -z "$service" ]; then
        docker-compose -p "$project_name" logs -f
    else
        docker-compose -p "$project_name" logs -f "$service"
    fi
}

# Main script logic
case $1 in
    "start")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 start <config> <project_name>"
            echo "Example: $0 start dev whisper-project-1"
            exit 1
        fi
        start_stack "$2" "$3"
        ;;
    "stop")
        if [ -z "$2" ]; then
            echo "Usage: $0 stop <project_name>"
            exit 1
        fi
        stop_stack "$2"
        ;;
    "list")
        list_stacks
        ;;
    "logs")
        if [ -z "$2" ]; then
            echo "Usage: $0 logs <project_name> [service_name]"
            exit 1
        fi
        show_logs "$2" "$3"
        ;;
    *)
        echo "Whisper Docker Stack Manager"
        echo "Usage: $0 {start|stop|list|logs}"
        echo ""
        echo "Commands:"
        echo "  start <config> <project_name>  Start a stack with specific configuration"
        echo "  stop <project_name>            Stop a specific stack"
        echo "  list                           List all running stacks"
        echo "  logs <project_name> [service]  Show logs for a stack"
        echo ""
        echo "Available configurations:"
        echo "  dev    - Development with hot reload and debugging"
        echo "  prod   - Production with scaling and optimization"
        echo "  gpu    - GPU acceleration enabled"
        echo "  queue  - With Redis queue processing"
        echo "  auto   - With automatic file watching"
        echo "  full   - All features enabled"
        echo ""
        echo "Examples:"
        echo "  $0 start dev project-alpha      # Development stack for project alpha"
        echo "  $0 start prod project-beta      # Production stack for project beta"
        echo "  $0 start gpu ml-processing      # GPU-accelerated stack for ML work"
        echo "  $0 list                         # Show all running stacks"
        echo "  $0 stop project-alpha           # Stop the alpha project stack"
        ;;
esac