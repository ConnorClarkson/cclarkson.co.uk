from app import create_app

application = create_app()

if __name__ == "__main__":
    application = create_app()
    application.jinja_env.cache = {}
    application.run()
