# Per-repo fleet start config for unity3d-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'unity3d-mcp'
    BackendPort  = 10831
    FrontendPort = 10830
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\unity3d-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'unity3d_mcp.server:asgi_app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10831' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
