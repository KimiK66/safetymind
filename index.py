def handler(request):
    """Ultra-simple Vercel function - no imports, no dependencies"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": '{"message": "SafetyMind API working", "status": "success"}'
    }
