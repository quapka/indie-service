#!/usr/bin/env python3

import argparse
import asyncio
import random
import secrets

from typing import List, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


class Channel:
    def __init__(self, card_id: Optional[int]):
        self.card_id = card_id
        self.recv_queue = asyncio.Queue()
        self.send_queue = asyncio.Queue()

    def send(self, item):
        # from card to the coordinator
        self.send_queue.put_nowait(item)

    async def receive(self):
        # receive from the coordinator to the card
        item = await self.recv_queue.get()
        return item


async def coordinator(channels: List[Channel], n: int, user: Channel):
    signers = {}

    # Receive everyones public key
    for ind, recv_ch in enumerate(channels):
        match await recv_ch.send_queue.get():
            case {"signer": _id, "pubkey": public_key, "cert": signature}:
                public_key = public_key
        if ind != _id:
            raise ValueError(f"Expected {ind} ID, but got {_id}")
        # Verify self-signed certificates
        public_key.verify(
            signature,
            public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ),
        )
        signers[ind] = public_key

        # Distribute the public keys to the other cards...
        for send_ch in channels:
            send_ch.recv_queue.put_nowait(
                {"signer": ind, "pubkey": public_key, "signature": signature}
            )
        # ...and to the user as well
        user.recv_queue.put_nowait(
            {"signer": ind, "pubkey": public_key, "signature": signature}
        )

    while True:
        # Setup done, wait for the user to send its token, this would be looping in real app
        token = await user.send_queue.get()

        # Distribute the token to the cards
        for ch in channels:
            ch.recv_queue.put_nowait(token)

        # Collect cards' salt "shares"
        for ch in channels:
            salt_share = await ch.send_queue.get()

            # FIXME the token will be encrypted in the final version, thus the following
            #       check won't be possible by the coordinator
            # signers[salt_share["signer"]].verify(salt_share["share"], token)

            print(f"Coordinator received valid share: {salt_share!r}")
            user.recv_queue.put_nowait(salt_share)


async def card(_id: int, channel: Channel, n: int):
    # Generated on-card or outside and loaded?
    # Assumed known to the card issuer/vendor.
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    pubkey_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )

    # Save our own key
    signers = {}
    signers[_id] = public_key

    # self-signd "certificate"
    commit_to_pub = private_key.sign(pubkey_bytes)

    # imitate random waits
    await asyncio.sleep(random.uniform(0.05, 1.0))

    # Commit to our public ke
    channel.send({"signer": _id, "pubkey": public_key, "cert": commit_to_pub})
    print(f"{_id} committed to {pubkey_bytes!r}")

    # Save public keys of other signers
    for _ in range(n):
        # imitate random waits
        await asyncio.sleep(random.uniform(0.05, 1.0))
        match await channel.receive():
            case {"ind": ind, "pubkey": other_public_key, "signature": signature}:
                # Verify that the keys are self-signed
                public_key.verify(
                    signature,
                    public_key.public_bytes(
                        encoding=serialization.Encoding.Raw,
                        format=serialization.PublicFormat.Raw,
                    ),
                )
                if ind != _id:
                    # Save others' keys
                    signers[ind] = other_public_key
                    # And validate wer received what we sent before
                else:
                    if public_key != other_public_key:
                        raise ValueError("Incorrect self key returned")

    while True:
        # salt request
        token = await channel.receive()
        # The signature itself is the share
        share = private_key.sign(token)
        channel.send({"signer": _id, "share": share})


# FIXME turn into service to see that salt derivation is deterministic
async def user(channel: Channel, n: int):
    # Simulates JWT
    token = secrets.token_bytes(32)

    async def get_cards_public():
        # Receive the cards public keys, this should happen out-of-band from the card issuers
        # Actually, but can be cross-checked with the data from the operator
        cards = {}
        for _ in range(n):
            match await channel.receive():
                case {"signer": signer, "pubkey": public_key, "signature": signature}:
                    signature = signature
                    # Verify salt share's signature and...
                    public_key.verify(
                        signature,
                        public_key.public_bytes(
                            encoding=serialization.Encoding.Raw,
                            format=serialization.PublicFormat.Raw,
                        ),
                    )
                    # ...if it's OK, save it
                    cards[signer] = public_key
                    print("Pubkey received")
        return cards

    # Flag to mark when the fist salt was generated
    async def get_salt(cards):
        # Request salt
        channel.send(token)
        print("Token sent")

        salt_shares: List[bytes] = []
        for _ in range(n):
            match await channel.receive():
                case {"signer": signer, "share": share}:
                    signature = share
                    print(f"signer: {signer}")
                    # Verify salt share's signature
                    cards[signer].verify(share, token)
                    salt_shares.append(share)

        salt = derive_salt_from_shares(salt_shares)

        return salt

    cards = await get_cards_public()

    while True:
        salt = await get_salt(cards=cards)

    return salt


def derive_salt_from_shares(shares: List[bytes]) -> bytes:
    # FIXME: Xor for now
    lens = set(len(sh) for sh in shares)
    if len(lens) != 1:
        raise ValueError("The shares aren't of the same length")

    salt = []
    for ind in range(len(shares[0])):
        tmp = 0
        for share in shares:
            tmp ^= share[ind]
        salt.append(tmp)

    return bytes(salt)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--group-size", type=int, default=3)
    parser.add_argument("-t", "--threshold", type=int, default=2)

    args = parser.parse_args()
    group_size = args.group_size
    threshold = args.threshold
    if group_size < 2 or threshold < 1 or threshold > group_size:
        raise ValueError(
            f"Unexpected threshold or group size ({threshold}-of-{group_size})."
        )

    # _group_params = {
    #     "group_size": group_size,
    #     "threshold": threshold,
    # }

    channels = []
    for i, _ in enumerate(range(group_size)):
        channels.append(Channel(card_id=i))

    # FIXME update channel not to require card_id
    user_channel = Channel(card_id=None)

    async def session():
        coroutines = [coordinator(channels=channels, n=group_size, user=user_channel)]
        coroutines += [user(user_channel, n=group_size)]
        for i, channel in enumerate(channels):
            coroutines.append(card(i, channel, n=group_size))

        return await asyncio.gather(*coroutines)

    outputs = asyncio.run(session())
    # The user is the second coroutine
    print(outputs[1])

    return outputs


if __name__ == "__main__":
    main()
