db.createUser({
    user: "clippings_db",
    pwd: "password",
    roles: [
        {
            role: "readWrite",
            db: "clippings_db"
        }
    ]
});
