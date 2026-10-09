def home(request):
    return HttpResponse("Hello, World!")

def home1(request):
    return HttpResponse("""
    <html>
    <head>
        <title>ABC Academy</title>
    </head>
    <body>
        <h1>Welcome to ABC Academy</h1>
        <p>We teach Python, Django and React.</p>
    </body>
    </html>
    """)