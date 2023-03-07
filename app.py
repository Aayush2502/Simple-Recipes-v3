from website import create_app

if __name__ == '__main__':
    app = create_app()
    # now available on all devices connected to network
    app.run(host="0.0.0.0", port=8000, debug=True)
