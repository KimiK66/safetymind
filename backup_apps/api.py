"""
SafetyMind Vercel Entry Point - Simplest Possible
Just a basic HTTP handler
"""

def handler(request):
    """Basic HTTP handler for Vercel"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        },
        "body": '{"message": "SafetyMind API is running", "status": "healthy", "version": "1.0.0"}'
    }

# For local testing
if __name__ == "__main__":
    print("SafetyMind API handler ready")
