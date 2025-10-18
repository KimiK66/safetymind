def handler(request, response):
    """Modern Vercel Python function handler"""
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
        "message": "SafetyMind API working",
        "status": "success",
        "version": "1.0.0",
        "method": request.method,
        "path": request.path
    }
    
    # Set response
    response.status_code = 200
    response.body = str(data).replace("'", '"')  # Convert to JSON string
    
    return response