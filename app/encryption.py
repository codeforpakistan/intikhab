from lightphe.cryptosystems.Paillier import Paillier
import hashlib

class Ciphertext:
    def __init__(self, ciphertext: int, randomness: int):
        self.ciphertext = ciphertext
        self.randomness = randomness

    def __repr__(self):
        """
        Provide a string representation of the CipherData object for debugging.
        """
        return f"CipherData(ciphertext='{self.ciphertext}', randomness='{self.randomness}')"

    def display(self):
        """
        Display the ciphertext and randomness in a readable format.
        """
        print(f"Ciphertext: {self.ciphertext}")
        print(f"Randomness: {self.randomness}")


class Encryption:
    def __init__(self, public_key: str = None, private_key: str = None):
        """
        Initialize the Encryption class with a public and private key.
        
        :param public_key: The public key used for encryption.
        :param private_key: The private key used for decryption.
        """
        if public_key is None and private_key is None:
            self.paillier = Paillier()
        elif public_key is not None and private_key is None:
            public_key_g, public_key_n = public_key.split(',')
            keys = {"public_key": {"g": int(public_key_g), "n": int(public_key_n)}}
            self.paillier = Paillier(keys)
        else:
            public_key_g, public_key_n = public_key.split(',')
            private_key = int(private_key)
            keys = {"public_key": {"g": int(public_key_g), "n": int(public_key_n)}, "private_key": {"phi": private_key}}
            self.paillier = Paillier(keys)
    
    def generate_random_key(self):
        """
        Generate a random key.
        """
        return self.paillier.generate_random_key()

    def encrypt(self, plaintext: int, rand: int):
        """
        Encrypt the given plaintext.

        :param plaintext: The plaintext integer to be encrypted.
        :return: Ciphertext object.
        """
        ct = self.paillier.encrypt(plaintext, rand)
        ciphertext_object = Ciphertext(ct, rand)
        return ciphertext_object

    def add(self, ct1, ct2):
        """
        Add two plaintext values securely with given randomness.

        :param pt1: The first plaintext.
        :param pt2: The second plaintext.
        :param randomness: Randomness or nonce.
        :return: Sum of the two plaintexts.
        """
        sum = self.paillier.add(ct1.ciphertext, ct2.ciphertext)
        combined_randomness = ct1.randomness*ct2.randomness
        ciphertext_object = Ciphertext(sum, combined_randomness)
        return ciphertext_object
    
    def decrypt(self, ct):
        """
        Decrypt the given ciphertext.

        :param ciphertext: The ciphertext to be decrypted.
        :return: The plaintext.
        """
        plaintext = self.paillier.decrypt(ct.ciphertext)
        return plaintext

    def hash(self, ct_str):
        """
        Hash the given ciphertext array.

        :param ciphertext: The ciphertext to be hashed.
        :return: The hash value.
        """
        hash_value = hashlib.sha256(ct_str.encode()).hexdigest()
        return hash_value

    def serialize(self, ciphertext):
        """
        Serialize the ciphertext into a serializable format.

        :param ciphertext: The ciphertext object to serialize.
        :return: Serialized output.
        """
        pass