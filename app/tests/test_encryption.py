import unittest
from app.encryption import Encryption, Ciphertext


class EncryptionUnitTests(unittest.TestCase):

    def setUp(self):
        """Set up a new Encryption instance for each test."""
        self.encryption = Encryption()
        self.public_key_str = f"{self.encryption.paillier.keys['public_key']['g']},{self.encryption.paillier.keys['public_key']['n']}"
        self.private_key_str = str(self.encryption.paillier.keys["private_key"]["phi"])
        self.encryption_with_keys = Encryption(
            public_key=self.public_key_str, private_key=self.private_key_str
        )

    def test_encrypt_decrypt_cycle(self):
        """Test that a plaintext number can be encrypted and then decrypted back to the original value."""
        plaintext = 12345
        ciphertext_obj = self.encryption.encrypt(plaintext)
        self.assertIsNotNone(ciphertext_obj)
        self.assertIsInstance(ciphertext_obj, Ciphertext)
        decrypted_plaintext = self.encryption.decrypt(ciphertext_obj)
        self.assertEqual(plaintext, decrypted_plaintext)
        print("✅ test_encrypt_decrypt_cycle passed.")

    def test_homomorphic_add(self):
        """Test the homomorphic addition of two encrypted numbers."""
        plaintext1 = 100
        plaintext2 = 50
        ct1 = self.encryption.encrypt(plaintext1)
        ct2 = self.encryption.encrypt(plaintext2)
        sum_ct = self.encryption.add(ct1, ct2)
        decrypted_sum = self.encryption.decrypt(sum_ct)
        self.assertEqual(plaintext1 + plaintext2, decrypted_sum)
        print("✅ test_homomorphic_add passed.")

    def test_ciphertext_json_serialization(self):
        """Test that a Ciphertext object can be converted to and from a JSON string."""
        plaintext = 99
        original_ct = self.encryption.encrypt(plaintext)
        json_str = original_ct.to_json()
        self.assertIsInstance(json_str, str)
        reconstructed_ct = Ciphertext.from_json(json_str)
        self.assertEqual(original_ct.ciphertext, reconstructed_ct.ciphertext)
        self.assertEqual(original_ct.randomness, reconstructed_ct.randomness)
        print("✅ test_ciphertext_json_serialization passed.")

    def test_verify_zero(self):
        """Test the ability to verify if a ciphertext is an encryption of zero."""
        zero_ct = self.encryption_with_keys.encrypt(0)
        self.assertTrue(self.encryption_with_keys.verify_zero(zero_ct))
        print("✅ test_verify_zero passed.")

    def test_extract_randomness_from_zero_vector(self):
        """Test the extraction of randomness from a ciphertext of zero."""
        known_randomness = self.encryption_with_keys.generate_random_key()
        zero_ct = self.encryption_with_keys.encrypt(0, rand=known_randomness)
        extracted_randomness = (
            self.encryption_with_keys.extract_randomness_from_zero_vector(zero_ct)
        )
        self.assertEqual(known_randomness, extracted_randomness)
        print("✅ test_extract_randomness_from_zero_vector passed.")

    def test_hash_function(self):
        """Test the SHA-256 hash function for consistency."""
        data = "hello world"
        expected_hash = (
            "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        )
        self.assertEqual(self.encryption.hash(data), expected_hash)
        print("✅ test_hash_function passed.")


