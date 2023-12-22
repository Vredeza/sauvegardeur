from app import create_app

if __name__ == '__main__':
    app = create_app()
    context = ('cert/cert.pem', 'cert/key.pem')
    app.run(host='0.0.0.0', port=555, ssl_context=context)
