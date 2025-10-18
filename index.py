"""
SafetyMind Vercel Function
Properly formatted for Vercel Python runtime
"""

def handler(request, response):
    """
    Vercel Python function handler
    Args:
        request: Vercel request object
        response: Vercel response object
    """
    # Set CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Content-Type'] = 'application/json'
    
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response.status_code = 200
        return response
    
    # Create response data
    data = {
        "message": "SafetyMind API is running",
        "status": "healthy",
        "version": "1.0.0",
        "method": request.method,
        "path": request.path,
        "timestamp": "2025-01-18T00:00:00Z"
    }
    
    # Set response
    response.status_code = 200
    response.body = str(data).replace("'", '"')  # Convert to JSON string
    
    return response
