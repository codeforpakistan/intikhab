from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from app.models import Election, Candidate, Vote
from app.encryption import Encryption, Ciphertext
import json


class ElectionViewIntegrationTests(TestCase):

    def setUp(self):
        """Set up the test client, users, and a complete database state for tests."""
        self.client = Client()
        self.voting_user = User.objects.create_user(
            username="voter", password="password123"
        )
        self.candidate_user1 = User.objects.create_user(
            username="candidate1",
            password="password123",
            first_name="Candidate",
            last_name="A",
        )
        self.candidate_user2 = User.objects.create_user(
            username="candidate2",
            password="password123",
            first_name="Candidate",
            last_name="B",
        )

        self.client.login(username="voter", password="password123")

        self.encryption = Encryption()
        public_key = self.encryption.paillier.keys["public_key"]
        private_key = self.encryption.paillier.keys["private_key"]

        self.election = Election.objects.create(
            name="Test Presidential Election",
            public_key=json.dumps(public_key),
            private_key=json.dumps(private_key),
            description="A test election.",
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
        )

        self.candidate1 = Candidate.objects.create(
            user=self.candidate_user1, election=self.election
        )
        self.candidate2 = Candidate.objects.create(
            user=self.candidate_user2, election=self.election
        )

    def test_election_list_view(self):
        """Test if the election list page loads correctly."""
        response = self.client.get(reverse("election_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.election.name)
        print("✅ test_election_list_view passed.")

    def test_vote_submission(self):
        """Test that a logged-in user can successfully cast a vote."""
        votes_before = Vote.objects.count()
        response = self.client.post(
            reverse("vote", args=[self.election.id, self.candidate1.id])
        )
        self.assertEqual(response.status_code, 302)
        votes_after = Vote.objects.count()
        self.assertEqual(votes_after, votes_before + 1)
        new_vote = Vote.objects.latest("id")
        self.assertEqual(new_vote.user, self.voting_user)
        self.assertNotEqual(new_vote.ballot, "")
        self.assertNotEqual(new_vote.hashed, "")
        print("✅ test_vote_submission passed.")

    def test_verify_results_view_with_valid_data(self):
        """Integration test for the verification logic with correct cryptographic data."""
        vote = Vote(user=self.voting_user, election=self.election)
        vote._candidate = self.candidate1
        vote.save()
        all_votes = self.election.votes.all()
        encrypted_ballots = [json.loads(v.ballot) for v in all_votes]

        # Initialize total with an encryption of [0, 0]
        total_ct = [self.encryption.encrypt(0), self.encryption.encrypt(0)]
        for ballot in encrypted_ballots:
            for i in range(len(ballot)):
                ballot_ct = Ciphertext(ballot[i])
                total_ct[i] = self.encryption.add(total_ct[i], ballot_ct)

        decrypted_total = [self.encryption.decrypt(ct) for ct in total_ct]
        self.assertEqual(
            decrypted_total, [1, 0]
        )  # One vote for candidate 1, zero for candidate 2
        encrypted_positive_total = [ct.to_json() for ct in total_ct]

        decrypted_negative_total = [-x for x in decrypted_total]
        encrypted_negative_total = [
            self.encryption.encrypt(decrypted_negative_total[0], rand=1),
            self.encryption.encrypt(decrypted_negative_total[1], rand=1),
        ]

        encrypted_zero_sum = [
            self.encryption.add(total_ct[0], encrypted_negative_total[0]),
            self.encryption.add(total_ct[1], encrypted_negative_total[1]),
        ]

        zero_randomness = [
            self.encryption.extract_randomness_from_zero_vector(ct)
            for ct in encrypted_zero_sum
        ]

        self.election.decrypted_total = json.dumps(decrypted_total)
        self.election.encrypted_positive_total = json.dumps(encrypted_positive_total)
        self.election.zero_randomness = json.dumps(zero_randomness)
        self.election.save()

        response = self.client.get(reverse("verify_results", args=[self.election.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["verified"])
        print("✅ test_verify_results_view_with_valid_data passed.")

    def test_user_cannot_vote_twice(self):
        """Verify the unique_together constraint prevents a user from voting more than once."""
        # Cast the first vote
        self.client.post(reverse("vote", args=[self.election.id, self.candidate1.id]))
        self.assertEqual(
            Vote.objects.filter(user=self.voting_user, election=self.election).count(),
            1,
        )

        # Attempt to cast a second vote
        # In a real app, the view should catch the IntegrityError and redirect gracefully.
        # Here we confirm the database constraint works.
        with self.assertRaises(
            Exception
        ):
            vote = Vote(
                user=self.voting_user,
                election=self.election,
                _candidate=self.candidate2,
            )
            vote.save()

        # Ensure the vote count has not increased
        self.assertEqual(
            Vote.objects.filter(user=self.voting_user, election=self.election).count(),
            1,
        )
        print("✅ test_user_cannot_vote_twice passed.")

    def test_unauthenticated_user_cannot_vote(self):
        """Ensure a user who is not logged in is redirected to the login page."""
        self.client.logout()
        response = self.client.get(
            reverse("vote", args=[self.election.id, self.candidate1.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(reverse("login") in response.url)
        print("✅ test_unauthenticated_user_cannot_vote passed.")
