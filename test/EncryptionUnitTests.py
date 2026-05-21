import unittest
import nacl.public
import nacl.bindings
import time
from unittest.mock import patch
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
from EncryptionProtocol import EncryptionProtocol


# ── Shared test vectors ────────────────────────────────────────────────────────
T_CLIENT_PRIVATE_KEY = b'\x99x\x93eP\xdd\xb7h\xd5dJ\xc7\xa5~\x83\xbdX\x04M\xe29\x15\xe2\xf1\xe8\xd8VFk0\xf8\xa1'
T_SERVER_PUBLIC_KEY  = b'f,^\xc0Cb\xf3\x937\xbf\x11\x14"\xed\x13\x0b\x9f\xe7\xaf;\x94\xb0p\x13\xe1\x94\xdd\x85\xcf\x01\x0bC'

T_KEY    = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'
T_INPUT  = b'I love network security'


def make_protocol() -> EncryptionProtocol:
    """Return a non-debug EncryptionProtocol using the worked-example keys."""
    priv = nacl.public.PrivateKey(T_CLIENT_PRIVATE_KEY)
    ep = EncryptionProtocol(priv, T_SERVER_PUBLIC_KEY)
    # Manually set the public key to match the worked example
    ep.client_public_key = bytes(priv.public_key)
    return ep


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestConstructor(unittest.TestCase):

    def test_accepts_raw_bytes_private_key(self):
        ep = EncryptionProtocol(T_CLIENT_PRIVATE_KEY, T_SERVER_PUBLIC_KEY)
        self.assertIsInstance(ep.client_private_key, nacl.public.PrivateKey)

    def test_accepts_private_key_object(self):
        priv = nacl.public.PrivateKey(T_CLIENT_PRIVATE_KEY)
        ep = EncryptionProtocol(priv, T_SERVER_PUBLIC_KEY)
        self.assertIsInstance(ep.client_private_key, nacl.public.PrivateKey)

    def test_raises_on_invalid_key_type(self):
        with self.assertRaises(TypeError):
            EncryptionProtocol("not_a_key", T_SERVER_PUBLIC_KEY)

    def test_private_key_not_stored_as_bytes(self):
        ep = make_protocol()
        self.assertNotIsInstance(ep.client_private_key, bytes)


class TestDH(unittest.TestCase):

    def setUp(self):
        self.ep = make_protocol()

    def test_dh_generate_returns_key_pair(self):
        priv, pub = self.ep.DH_Generate()
        self.assertIsInstance(priv, nacl.public.PrivateKey)
        self.assertIsInstance(pub, nacl.public.PublicKey)

    def test_dh_shared_secret_is_symmetric(self):
        priv_a, pub_a = self.ep.DH_Generate()
        priv_b, pub_b = self.ep.DH_Generate()
        shared_ab = self.ep.DH(bytes(priv_a), bytes(pub_b))
        shared_ba = self.ep.DH(bytes(priv_b), bytes(pub_a))
        self.assertEqual(shared_ab, shared_ba)

    def test_dh_output_is_32_bytes(self):
        priv, pub = self.ep.DH_Generate()
        result = self.ep.DH(bytes(priv), bytes(pub))
        self.assertEqual(len(result), 32)


class TestHash(unittest.TestCase):

    def setUp(self):
        self.ep = make_protocol()

    def test_hash_known_vector(self):
        result = self.ep.Hash(b'Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s')
        expected = b"`\xe2m\xae\xf3'\xef\xc0.\xc35\xe2\xa0%\xd2\xd0\x16\xebB\x06\xf8rw\xf5-8\xd1\x98\x8bx\xcd6"
        self.assertEqual(result, expected)

    def test_hash_accepts_string(self):
        result = self.ep.Hash("hello")
        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), 32)

    def test_hash_accepts_bytes(self):
        result = self.ep.Hash(b"hello")
        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), 32)

    def test_hash_string_and_bytes_match(self):
        self.assertEqual(self.ep.Hash("hello"), self.ep.Hash(b"hello"))

    def test_mixhash_known_vector(self):
        result = self.ep.MixHash(b'a' * 50, b'b' * 50)
        expected = b'#B\x17\x17\xbe=\xfcc\xd6\xb5@81\t\x8dh\x88\x9b\xb3\xa8\xb9\xb2n\n\x02\r:\xcb\xbe\xb0\xa7\xee'
        self.assertEqual(result, expected)


class TestMac(unittest.TestCase):

    def setUp(self):
        self.ep = make_protocol()
        self.key = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'

    def test_mac_known_vector(self):
        result = self.ep.Mac(
            self.key,
            b'I am a message without a MAC, but only for now.'
        )
        expected = b'*\xbd\x8ak4%\xe4\xb0\xe7\x96\xe5z\x14q\xdd!'
        self.assertEqual(result, expected)

    def test_mac_output_is_16_bytes(self):
        result = self.ep.Mac(self.key, b'test')
        self.assertEqual(len(result), 16)


class TestHmac(unittest.TestCase):

    def setUp(self):
        self.ep = make_protocol()
        self.key = b':\xb6\x90\xbd\n:\x18Z88"\xd8a\x08\x9f\xa7\x9c\xc7\xcb\x01\x99-\xfd\x9cGX\xdc\x9dO\x0c\xb3@'

    def test_hmac_known_vector(self):
        result = self.ep.Hmac(
            self.key,
            b'I am a message without an HMAC, but only for now.'
        )
        expected = b'\x1ew,:\x03\xdd\x0b\x1e\x96\n\x00J\x8c\xe1QzQ\xff\xb8\x02\xcb\xa29\xa8{\x00\x07(\xa6\xc0\x07\xde'
        self.assertEqual(result, expected)

    def test_hmac_output_is_32_bytes(self):
        result = self.ep.Hmac(self.key, b'test')
        self.assertEqual(len(result), 32)

    def test_hmac_long_key_is_hashed(self):
        long_key = b'x' * 100  # longer than 64-byte block size
        result = self.ep.Hmac(long_key, b'test')
        self.assertEqual(len(result), 32)


class TestKDF(unittest.TestCase):

    def setUp(self):
        self.ep = make_protocol()

    def test_kdf1_known_vector(self):
        result = self.ep.KDF1(T_KEY, T_INPUT)
        expected = b'\xcf\xdf\x9cv\xee\xdc(\x1f\x82}\xdeS\x04;`\xf1llB\xc1\xfd\x9cy\xf6A\xbb\x1e\xdbg-_m'
        self.assertEqual(result, expected)

    def test_kdf2_known_vector(self):
        t1, t2 = self.ep.KDF2(T_KEY, T_INPUT)
        self.assertEqual(t1, b'\xcf\xdf\x9cv\xee\xdc(\x1f\x82}\xdeS\x04;`\xf1llB\xc1\xfd\x9cy\xf6A\xbb\x1e\xdbg-_m')
        self.assertEqual(t2, b'\xe7\x9c\xf0\xc4\x90\x1fG:\x91#\xa8\x8fL\xb0\xba\xfb\xdbx(lLq\xe7\xdc\xf3$\xb7\x1b]#\xe0\x1e')

    def test_kdf3_known_vector(self):
        t1, t2, t3 = self.ep.KDF3(T_KEY, T_INPUT)
        self.assertEqual(t1, b'\xcf\xdf\x9cv\xee\xdc(\x1f\x82}\xdeS\x04;`\xf1llB\xc1\xfd\x9cy\xf6A\xbb\x1e\xdbg-_m')
        self.assertEqual(t2, b'\xe7\x9c\xf0\xc4\x90\x1fG:\x91#\xa8\x8fL\xb0\xba\xfb\xdbx(lLq\xe7\xdc\xf3$\xb7\x1b]#\xe0\x1e')
        self.assertEqual(t3, b'\xafz\\\xe0V\x96\x0e-\xc1~\xef%\xc5\x1eF\xaf\xd8\xcb\x11\x9b\xec\x92\x89\xc2\x01v\xb2e@l\x7f\x17')

    def test_kdf1_output_is_first_output_of_kdf2(self):
        """KDF1 and KDF2's first output must agree."""
        t1_from_kdf1 = self.ep.KDF1(T_KEY, T_INPUT)
        t1_from_kdf2, _ = self.ep.KDF2(T_KEY, T_INPUT)
        self.assertEqual(t1_from_kdf1, t1_from_kdf2)

    def test_kdf2_outputs_are_first_two_of_kdf3(self):
        t1_2, t2_2 = self.ep.KDF2(T_KEY, T_INPUT)
        t1_3, t2_3, _ = self.ep.KDF3(T_KEY, T_INPUT)
        self.assertEqual(t1_2, t1_3)
        self.assertEqual(t2_2, t2_3)


class TestAEAD(unittest.TestCase):

    def setUp(self):
        self.ep = make_protocol()
        self.key      = T_KEY
        self.counter  = b'\x00' * 12
        self.plaintext = b"attack at dawn"
        self.authtext  = b'\x8e2\x89\xe2\x14\xfd\x16\x19o\x06\xc9\xb2\xd9\xe8F\xfd\xdaf\xdc\xa4\xf9\xe9\x98\xbc\xd8x\xb9\x90\x1e\n\xac\x98'
        self.ciphertext = b'\xfbv\x84\xea\xd0S\n\xc1\x16\x9et\xd5\xa4/\xeee\x9a\xa9MR\xe3\xd5p3\x85\r\xce\x15r\xcd'

    def test_encrypt_known_vector(self):
        result = self.ep.AEAD_encrpyt(self.key, self.counter, self.plaintext, self.authtext)
        self.assertEqual(result, self.ciphertext)

    def test_decrypt_known_vector(self):
        result = self.ep.AEAD_decrypt(self.key, self.counter, self.ciphertext, self.authtext)
        self.assertEqual(result, self.plaintext)

    def test_encrypt_decrypt_roundtrip(self):
        key = self.ep.KDF1(T_KEY, T_INPUT)
        ct  = self.ep.AEAD_encrpyt(key, 0, b"hello world", b"auth")
        pt  = self.ep.AEAD_decrypt(key, 0, ct, b"auth")
        self.assertEqual(pt, b"hello world")

    def test_counter_as_int_and_bytes_agree(self):
        ct_int   = self.ep.AEAD_encrpyt(self.key, 0,              self.plaintext, self.authtext)
        ct_bytes = self.ep.AEAD_encrpyt(self.key, b'\x00' * 12,   self.plaintext, self.authtext)
        self.assertEqual(ct_int, ct_bytes)

    def test_wrong_auth_tag_raises(self):
        from cryptography.exceptions import InvalidTag
        with self.assertRaises(InvalidTag):
            self.ep.AEAD_decrypt(self.key, self.counter, self.ciphertext, b"wrong auth")


class TestTimestamp(unittest.TestCase):

    def setUp(self):
        self.ep = make_protocol()

    def test_timestamp_is_12_bytes(self):
        result = self.ep.Timestamp(time.time())
        self.assertEqual(len(result), 12)

    def test_timestamp_seconds_are_monotonic(self):
        t1 = self.ep.Timestamp(1000.0)
        t2 = self.ep.Timestamp(2000.0)
        s1 = int.from_bytes(t1[:8], 'big')
        s2 = int.from_bytes(t2[:8], 'big')
        self.assertGreater(s2, s1)


class TestHandshake(unittest.TestCase):
    """Tests for send_prep, receive_prep, and the full handshake flow.

    send_prep calls DH_Generate() for a fresh ephemeral keypair and
    time.time() for the timestamp — both of which must be fixed to match
    the worked-example values.
    """

    # Fixed values from the worked example
    FIXED_TIME      = 1744377020.21733
    FIXED_E_I_PRIV  = b'\xac\x03\x18b0\xc4\xf7\xd4*\xa7-\x81&\xfb\xc7\xb3PG0\xae\xa4y0\x90\xe2\xe4\xe2\xa0g\\\x83\xb6'
    FIXED_E_I_PUB   = b"\xb1\x13\xb4\xd3\x00R'\x8b\x80\xd1\xcc\xc8X\x1bYf(4\xce&\xd0V\xde\x97\xff\xba2$u\x9b\xe3G"

    CONSTRUCTION = b'Noise_IKpsk2_25519_ChaChaPoly_BLAKE2s'
    IDENTIFIER   = b'WireGuard v1 zx2c4 Jason@zx2c4.com'

    def setUp(self):
        self.ep = make_protocol()

    def _make_fixed_dh_generate(self):
        """Return a DH_Generate stub that always yields the worked-example ephemeral pair."""
        priv = nacl.public.PrivateKey(self.FIXED_E_I_PRIV)
        pub  = priv.public_key
        return lambda: (priv, pub)

    def _run_send_prep(self):
        ep = make_protocol()
        with patch('time.time', return_value=self.FIXED_TIME), \
             patch.object(ep, 'DH_Generate', self._make_fixed_dh_generate()):
            return ep.send_prep(self.CONSTRUCTION, self.IDENTIFIER)

    def test_send_prep_hash_known_vector(self):
        _, _, _, _, _, hash_out = self._run_send_prep()
        expected = b'r\xdb\rg\x14\xa2\xff\x13h\xf8K\x9dL\xec\x81\xbf\xa6Q\x15\xf3\xeb\xd7{\x87\xa5\x8bs\xc8\xb4k\x8e\x1e'
        self.assertEqual(hash_out, expected)

    def test_send_prep_timestamp_known_vector(self):
        _, _, _, _, msg_timestamp, _ = self._run_send_prep()
        expected = b'\xc6?XF\x845JvXfm\xf9\xfa0\xf4\xb2\x18\xd6\xf9\x046\x17z\x08\x16y\xa9\xa5'
        self.assertEqual(msg_timestamp, expected)

    def test_send_prep_static_known_vector(self):
        _, _, _, msg_static, _, _ = self._run_send_prep()
        expected = b'\xc7\x12ry\x04\xb9\xc3\xaf\x9a\xf4\x7f \xf1\x98\xf3rA\x9d\x92\x0f\xaea[=\xf5N\xe0]Q\x9a\x88\x855\xb046\xb5\xefk\xf4z\xcd#\x0c\x0c\xcd<\xda'
        self.assertEqual(msg_static, expected)

    def test_receive_prep_and_key_derivation(self):
        chain_key = b'\xe0\\UH\\\x12\x9a\xb4\xcc\xd0\r\xa9\xd2\xac\xc7\xb1]ky\xdc\xc2\x18\xb8\x95]NQ\xf9=\xcd\xa5\xc3'
        hash_val  = b'r\xdb\rg\x14\xa2\xff\x13h\xf8K\x9dL\xec\x81\xbf\xa6Q\x15\xf3\xeb\xd7{\x87\xa5\x8bs\xc8\xb4k\x8e\x1e'

        response_msg = (
            b'\x02\x00\x00\x00D\xe6+\xe3Z\r\x85\xee\xe5\xd0!\x98z\x12\xb5\xf8&\x17\xfe\x14K\x9exe(\x1bK\xc2'
            b'\x8e\x15T\x81\xcc\xbe\xceq$\x82v\x7f\x0b\xa1\xfc>\xdf\xb4\xe0\x96Pc\x15\xfe\x9b7\xdc\xb1\x18l'
            b'\xa4sk\xfd"r\xa5z\x03\x1eu\xdd=\xd9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        )

        E_R_pub          = response_msg[12:44]
        msg_empty_cipher = response_msg[44:60]
        E_I_priv = b'\xac\x03\x18b0\xc4\xf7\xd4*\xa7-\x81&\xfb\xc7\xb3PG0\xae\xa4y0\x90\xe2\xe4\xe2\xa0g\\\x83\xb6'
        Q = b'\x00' * 32

        _, chain_key_out = self.ep.recieve_prep(
            chain_key, hash_val, E_R_pub, E_I_priv, T_CLIENT_PRIVATE_KEY, msg_empty_cipher, Q
        )

        sending_key, receiving_key = self.ep.KDF2(chain_key_out, b'')
        self.assertEqual(sending_key,   b'\xd0\x98\xff\xa8\xf4u&\xc4$\x94\xcd&*X\xbfc\x91_\xc3ls\xd1\x1f\xff=\xd4<\x92\xc6\xb5\xb0q')
        self.assertEqual(receiving_key, b'\x032\xb2\xbe\xae"<\'}\x97\x08@w\x98\x10l\xb9\xd4|\xc7\x02\xc4\xefE\x18K\x05\x92\xe0d\x8e\xce')


class TestTransport(unittest.TestCase):
    """Tests for encrypt_transport / decrypt_transport roundtrip."""

    def setUp(self):
        self.ep = make_protocol()
        # Inject known session keys directly
        self.ep.sending_key   = b'\xd0\x98\xff\xa8\xf4u&\xc4$\x94\xcd&*X\xbfc\x91_\xc3ls\xd1\x1f\xff=\xd4<\x92\xc6\xb5\xb0q'
        self.ep.receiving_key = b'\x032\xb2\xbe\xae"<\'}\x97\x08@w\x98\x10l\xb9\xd4|\xc7\x02\xc4\xefE\x18K\x05\x92\xe0d\x8e\xce'
        self.ep.server_index  = 0x12345678
        self.ep.N_send        = 0
        self.ep.N_recv        = 0

    def test_encrypt_produces_correct_packet_structure(self):
        packet = self.ep.encrypt_transport(b"hello")
        self.assertEqual(packet[0:1], b'\x04')          # type
        self.assertEqual(packet[1:4], b'\x00\x00\x00')  # reserved

    def test_encrypt_increments_counter(self):
        self.ep.encrypt_transport(b"msg1")
        self.assertEqual(self.ep.N_send, 1)
        self.ep.encrypt_transport(b"msg2")
        self.assertEqual(self.ep.N_send, 2)

    def test_encrypt_decrypt_roundtrip(self):
        """Swap send/recv keys to simulate both sides of the channel."""
        plaintext = b"secret message"
        packet = self.ep.encrypt_transport(plaintext)

        # Simulate the receiving side (keys swapped)
        receiver = make_protocol()
        receiver.receiving_key = self.ep.sending_key
        receiver.N_recv        = 0

        result = receiver.decrypt_transport(packet)
        self.assertEqual(result, plaintext)

    def test_encrypt_accepts_string(self):
        packet = self.ep.encrypt_transport("hello as string")
        self.assertIsInstance(packet, bytes)


if __name__ == "__main__":
    unittest.main()