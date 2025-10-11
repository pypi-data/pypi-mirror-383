use arena_core::server::GameServer;
use tokio::signal;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Create the server instance
    let server = GameServer::new();

    // Address and port to bind to
    let addr = "0.0.0.0:9001"; // listen on all interfaces

    // Spawn the server in a background task
    let server_task = tokio::spawn(async move {
        if let Err(e) = server.start_server(addr).await {
            eprintln!("Server error: {:?}", e);
        }
    });

    println!("Press Ctrl+C to stop...");

    // Wait for Ctrl+C to gracefully shutdown
    signal::ctrl_c().await?;
    println!("Shutting down server...");

    // Optionally: cancel the server task
    server_task.abort();

    Ok(())
}
