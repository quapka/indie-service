import hashlib

import jwt

from flask import Flask, request, jsonify

from noise.connection import NoiseConnection, Keypair
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")


def derive_salt(token) -> bytes:
    m = hashlib.sha256()
    m.update(b"Salt service")
    # NOTE multiple audiences might be present
    m.update(token["aud"][0].encode())
    m.update(token["name"].encode())
    m.update(app.config.get("HASH_SALT_SECRET"))
    return m.digest()


def verify_nonce() -> bool:
    pass


@app.route("/get-salt", methods=["POST"])
def get_salt():
    token = request.form.get("jwt")
    decoded = jwt.decode(
        token,
        app.config.get("OP_EC_PUBLIC_KEY"),
        audience=["zkLogin"],
        algorithms=["ES256"],
    )
    salt = derive_salt(decoded)
    return jsonify({"salt": salt.hex()})


@app.route("/get-salt-e2e", methods=["POST"])
def get_salt_e2e():
    noise = NoiseConnection.from_name(b"Noise_NK_25519_ChaChaPoly_SHA256")
    static_privkey_pem = app.config.get("X25519_PRIVATE_KEY")
    static_privkey = load_pem_private_key(static_privkey_pem, password=None)

    static_privkey_bytes = static_privkey.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # print(f"static priveky(len({static_privkey_bytes}): {static_privkey_bytes}")

    noise.set_keypair_from_private_bytes(Keypair.STATIC, static_privkey_bytes)

    # noise.set_keypair_from_private_bytes(
    #     Keypair.STATIC,
    #     card_pubkey.public_bytes(
    #         encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    #     ),
    # )

    noise.set_as_responder()
    noise.start_handshake()

    # print(request.form)
    payload = bytes.fromhex(request.form.get("payload"))
    # print(f"payload(of length {len(payload)}): {payload}")
    token = noise.read_message(payload)
    # print(token)

    decoded = jwt.decode(
        bytes(token),
        app.config.get("OP_EC_PUBLIC_KEY"),
        audience=["zkLogin"],
        algorithms=["ES256"],
    )
    salt = derive_salt(decoded)
    enc_salt = noise.write_message(salt)

    return jsonify({"enc-salt": enc_salt.hex()})


@app.route("/get-single-card-public", methods=["GET"])
def get_single_card_public():
    return jsonify({"single-card-public-key": app.config.get("X25519_PUBLIC_KEY")})
