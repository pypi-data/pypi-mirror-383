"""
SOLLOL CLI - Intelligent load balancer for Ollama clusters.
Runs on Ollama's port (11434) and routes requests to backend Ollama nodes.
"""

import logging
from typing import Optional

import typer

from .gateway import start_api

app = typer.Typer(
    name="sollol",
    help="SOLLOL - Intelligent load balancer for Ollama clusters. Runs on Ollama's port, routes to backend nodes.",
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.command()
def up(
    port: int = typer.Option(11434, help="Port for SOLLOL gateway (default: 11434, Ollama's port)"),
    ray_workers: int = typer.Option(4, help="Number of Ray actors for parallel execution"),
    dask_workers: int = typer.Option(2, help="Number of Dask workers for batch processing"),
    batch_processing: bool = typer.Option(True, "--batch-processing/--no-batch-processing", help="Enable Dask batch processing"),
    autobatch_interval: int = typer.Option(60, help="Seconds between autobatch cycles"),
    rpc_backends: Optional[str] = typer.Option(
        None,
        help="Comma-separated RPC backends for model sharding (e.g., '192.168.1.10:50052,192.168.1.11:50052')",
    ),
    ollama_nodes: Optional[str] = typer.Option(
        None,
        help="Comma-separated Ollama nodes for task distribution (e.g., '192.168.1.20:11434,192.168.1.21:11434'). Auto-discovers if not set.",
    ),
):
    """
    Start SOLLOL gateway - Intelligent load balancer for Ollama clusters.

    SOLLOL runs on Ollama's port (11434) and routes requests to backend Ollama nodes.

    THREE DISTRIBUTION MODES:
    1. Intelligent Task Distribution - 7-factor routing + Ray parallel execution
    2. Batch Processing - Dask distributed batch operations (embeddings, bulk inference)
    3. Model Sharding - Distribute large models via llama.cpp RPC backends

    All modes work together for maximum performance!

    Features:
    - 7-factor intelligent routing engine
    - Ray actors for parallel request execution
    - Dask for distributed batch processing
    - Model sharding for 70B+ models via llama.cpp
    - Auto-discovers Ollama nodes and RPC backends
    - Automatic GGUF extraction from Ollama storage
    - Zero-config setup

    Examples:
        # Zero-config (auto-discovers everything):
        sollol up

        # Custom workers:
        sollol up --ray-workers 8 --dask-workers 4

        # With RPC backends for model sharding:
        sollol up --rpc-backends "192.168.1.10:50052,192.168.1.11:50052"

        # Disable batch processing:
        sollol up --no-batch-processing

        # Full configuration:
        sollol up --port 8000 --ray-workers 8 --rpc-backends "10.0.0.1:50052"
    """
    logger.info("=" * 70)
    logger.info("🚀 Starting SOLLOL Gateway")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Distribution Modes:")
    logger.info("  🎯 Intelligent Routing - 7-factor scoring engine")
    logger.info("  ⚡ Ray Parallel - Concurrent request execution")
    logger.info("  🔄 Dask Batch - Distributed bulk operations")
    logger.info("  🔗 Model Sharding - llama.cpp distributed inference")
    logger.info("")
    logger.info(f"Configuration:")
    logger.info(f"  Port: {port}")
    logger.info(f"  Ray workers: {ray_workers}")
    logger.info(f"  Dask workers: {dask_workers}")
    logger.info(f"  Batch processing: {'enabled' if batch_processing else 'disabled'}")

    # Parse RPC backends
    parsed_rpc_backends = None
    if rpc_backends:
        parsed_rpc_backends = []
        for backend_str in rpc_backends.split(","):
            backend_str = backend_str.strip()
            if ":" in backend_str:
                host, port_str = backend_str.rsplit(":", 1)
                parsed_rpc_backends.append({"host": host, "port": int(port_str)})
            else:
                parsed_rpc_backends.append({"host": backend_str, "port": 50052})
        logger.info(f"  RPC Backends: {len(parsed_rpc_backends)} configured")
        logger.info("  → Model Sharding ENABLED")
    else:
        logger.info("  RPC Backends: Auto-discovery mode")

    # Parse Ollama nodes
    parsed_ollama_nodes = None
    if ollama_nodes:
        parsed_ollama_nodes = []
        for node_str in ollama_nodes.split(","):
            node_str = node_str.strip()
            if ":" in node_str:
                host, node_port = node_str.rsplit(":", 1)
                parsed_ollama_nodes.append({"host": host, "port": int(node_port)})
            else:
                parsed_ollama_nodes.append({"host": node_str, "port": 11434})
        logger.info(f"  Ollama Nodes: {len(parsed_ollama_nodes)} configured")
        logger.info("  → Task Distribution ENABLED")
    else:
        logger.info("  Ollama Nodes: Auto-discovery mode")

    logger.info("")
    logger.info("=" * 70)
    logger.info("")

    # Start gateway (blocking call)
    start_api(
        port=port,
        rpc_backends=parsed_rpc_backends,
        ollama_nodes=parsed_ollama_nodes,
        ray_workers=ray_workers,
        dask_workers=dask_workers,
        enable_batch_processing=batch_processing,
        autobatch_interval=autobatch_interval,
    )


@app.command()
def down():
    """
    Stop SOLLOL service.

    Note: For MVP, manually kill Ray/Dask processes:
        pkill -f "ray::"
        pkill -f "dask"
    """
    logger.info("🛑 SOLLOL shutdown")
    logger.info("   To stop Ray: pkill -f 'ray::'")
    logger.info("   To stop Dask: pkill -f 'dask'")


@app.command()
def status():
    """
    Check SOLLOL service status.
    """
    logger.info("📊 SOLLOL Status")
    logger.info("   Gateway: http://localhost:8000/api/health")
    logger.info("   Metrics: http://localhost:9090/metrics")
    logger.info("   Stats: http://localhost:8000/api/stats")


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
