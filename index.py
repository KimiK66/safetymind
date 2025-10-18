def handler(request):
    """Minimal Vercel function - guaranteed to work"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": '{"message": "SafetyMind API working", "status": "success"}'
    }
