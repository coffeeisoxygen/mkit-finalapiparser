from app.service.srv_hasher import HasherService


def main():
    password = "admin@777999"

    hashed_password = HasherService().hash_password(password)
    print(f"Hashed Password: {hashed_password}")


if __name__ == "__main__":
    main()
