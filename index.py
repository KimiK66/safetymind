def handler(request):
    """Simple Vercel Python function that handles all routes"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        },
        "body": '{"message": "SafetyMind API working", "status": "success", "version": "1.0", "endpoints": ["/", "/health", "/api/reports"]}'
    }