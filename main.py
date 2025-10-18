def handler(request, response):
    """Modern Vercel Python function"""
    response.status_code = 200
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.body = '{"message": "SafetyMind API working", "status": "success"}'
    return response
